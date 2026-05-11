import base64
import io
import os
from contextlib import asynccontextmanager

import torch
from diffusers import AutoencoderKL, AutoPipelineForText2Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

MODEL_ID = os.environ.get("MODEL_ID", "stabilityai/sdxl-turbo")


def pick_device() -> tuple[str, torch.dtype]:
    if torch.cuda.is_available():
        return "cuda", torch.float16
    if torch.backends.mps.is_available():
        return "mps", torch.float16
    return "cpu", torch.float32


def load_pipeline():
    device, dtype = pick_device()
    kwargs = {"torch_dtype": dtype}
    if dtype == torch.float16:
        kwargs["variant"] = "fp16"
    # SDXL fp16 VAE produces black images on MPS. Swap in the community fp16-fix VAE.
    if device == "mps":
        kwargs["vae"] = AutoencoderKL.from_pretrained(
            "madebyollin/sdxl-vae-fp16-fix", torch_dtype=dtype
        )
    pipe = AutoPipelineForText2Image.from_pretrained(MODEL_ID, **kwargs)
    pipe = pipe.to(device)
    return pipe, device


state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    pipe, device = load_pipeline()
    state["pipe"] = pipe
    state["device"] = device
    yield
    state.clear()


app = FastAPI(title="Local SDXL-Turbo Image Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    steps: int = Field(2, ge=1, le=8)
    seed: int | None = None


@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


@app.get("/api/info")
def info():
    return {"model": MODEL_ID, "device": state.get("device", "unknown")}


@app.post("/api/generate")
def generate(req: GenerateRequest):
    pipe = state.get("pipe")
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    device = state["device"]
    generator = None
    if req.seed is not None:
        generator = torch.Generator(device=device).manual_seed(req.seed)

    try:
        image = pipe(
            prompt=req.prompt,
            num_inference_steps=req.steps,
            guidance_scale=0.0,
            generator=generator,
        ).images[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return {
        "image": base64.b64encode(buf.getvalue()).decode("ascii"),
        "prompt": req.prompt,
        "steps": req.steps,
        "seed": req.seed,
    }
