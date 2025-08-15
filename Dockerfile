FROM my-mistral-base-al2023:latest

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ONLY_BINARY=:all:

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["app.api.handler"]
