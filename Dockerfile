FROM my-mistral-base:latest

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

ENV AWS_LWA_PORT=8000 \
    AWS_LWA_READINESS_CHECK_PATH=/healthz \
    AWS_LWA_ENABLE_COMPRESSION=true

EXPOSE 8000
CMD ["uvicorn","app.api:app","--host","0.0.0.0","--port","8000"]
