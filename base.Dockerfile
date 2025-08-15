FROM public.ecr.aws/lambda/python:3.12

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ONLY_BINARY=:all:

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements_base.txt .
RUN python -m pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements_base.txt

COPY download_gguf.py .

ARG MODEL_DIR=/models/mistral-gguf
ENV MODEL_DIR=${MODEL_DIR}

RUN --mount=type=secret,id=env_file,target=/run/secrets/env_file \
    --mount=type=cache,target=/root/.cache/huggingface \
    python download_gguf.py
