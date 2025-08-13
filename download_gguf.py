from pathlib import Path
import os
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

ENV_SECRET_PATH = Path("/run/secrets/env_file")
if ENV_SECRET_PATH.exists():
    load_dotenv(ENV_SECRET_PATH, override=False)

repo   = os.getenv("MODEL_REPO")
base   = os.getenv("MODEL_BASE")
quant  = os.getenv("MODEL_QUANT")
outdir = Path(os.getenv("MODEL_DIR", "/models/mistral-gguf"))
token  = os.getenv("HUGGING_TOKEN")
file_override = os.getenv("MODEL_FILE")

if not (repo and base and quant):
    raise SystemExit("MODEL_REPO, MODEL_BASE, MODEL_QUANT must be set in .env")

candidates = [file_override] if file_override else [
    f"{base}-{quant}.gguf",
    f"{base}.{quant}.gguf",
]

outdir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")

last_err = None
for fname in [f for f in candidates if f]:
    try:
        path = hf_hub_download(
            repo_id=repo,
            filename=fname,
            token=token,
            local_dir=str(outdir),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        print("Saved:", path)
        break
    except Exception as e:
        last_err = e
else:
    raise SystemExit(f"Could not download {candidates} from {repo}: {last_err}")
