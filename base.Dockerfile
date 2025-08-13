FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface

WORKDIR /app

COPY requirements_base.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements_base.txt

COPY model_download.py .

RUN --mount=type=secret,id=env_file,target=/run/secrets/env_file \
    --mount=type=cache,target=/root/.cache/huggingface \
    HF_HUB_ENABLE_HF_TRANSFER=0 \
    python model_download.py

ENV TRANSFORMERS_OFFLINE=1
