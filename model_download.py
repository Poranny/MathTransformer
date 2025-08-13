from pathlib import Path
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"
OUT_DIR = Path("/models/mistral")
ENV_SECRET_PATH = Path("/run/secrets/env_file")
TOKEN_VAR = "HUGGING_TOKEN"

if ENV_SECRET_PATH.exists():
    load_dotenv(dotenv_path=ENV_SECRET_PATH, override=False)

token = os.getenv(TOKEN_VAR)
if not token:
    raise SystemExit(f"No {TOKEN_VAR} provided in secret .env or environment.")

OUT_DIR.mkdir(parents=True, exist_ok=True)
tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
mdl = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=token)
tok.save_pretrained(OUT_DIR)
mdl.save_pretrained(OUT_DIR)

print(f"Model saved to {OUT_DIR}")
