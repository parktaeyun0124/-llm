FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/data/.cache/huggingface \
    HUGGINGFACE_HUB_CACHE=/data/.cache/huggingface/hub \
    TRANSFORMERS_CACHE=/data/.cache/huggingface/transformers \
    MODEL_ID=stabilityai/sd-turbo

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd -m -u 1000 user && \
    mkdir -p /data/.cache/huggingface && \
    chown -R user:user /data /app

USER user
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user requirements.txt .
RUN pip install --user --upgrade pip && \
    pip install --user --index-url https://download.pytorch.org/whl/cpu torch && \
    pip install --user -r requirements.txt

COPY --chown=user . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
