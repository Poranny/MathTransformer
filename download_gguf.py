from pathlib import Path
import os
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

REPO_ID  = "MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF"
QUANT    = os.getenv("QUANT", "Q3_K_M")
FILENAME = os.getenv("MODEL_FILE", f"Mistral-7B-Instruct-v0.3.{QUANT}.gguf")
OUT_DIR  = Path("/models/mistral-gguf")
ENV_SECRET_PATH = Path("/run/secrets/env_file")

if ENV_SECRET_PATH.exists():
    load_dotenv(ENV_SECRET_PATH, override=False)

token = os.getenv("HUGGING_TOKEN")

OUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")  # stabilniejsze pobieranie

path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    token=token,
    local_dir=str(OUT_DIR),
    local_dir_use_symlinks=False,
    resume_download=True,
)
print("Saved:", path)
