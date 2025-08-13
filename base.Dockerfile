FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements_base.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements_base.txt

COPY download_gguf.py .

RUN --mount=type=secret,id=env_file,target=/run/secrets/env_file \
    --mount=type=cache,target=/root/.cache/huggingface \
    python download_gguf.py
