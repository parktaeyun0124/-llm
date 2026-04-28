import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Ollama FastAPI Backend")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_BASE_URL = "http://localhost:11434/api"

class ChatRequest(BaseModel):
    model: str
    messages: list

@app.get("/")
def read_root():
    # 현재 디렉토리의 index.html을 반환
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)

@app.get("/api/models")
async def get_models():
    """Ollama 서버에서 설치된 모델 목록을 가져옵니다."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OLLAMA_BASE_URL}/tags")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    """Ollama와 연결하여 스트리밍 답변을 반환합니다."""
    async def generate():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("POST", f"{OLLAMA_BASE_URL}/chat", json={
                    "model": req.model,
                    "messages": req.messages,
                    "stream": True
                }) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except Exception as e:
                yield json.dumps({"error": str(e)}).encode("utf-8")

    return StreamingResponse(generate(), media_type="application/x-ndjson")
