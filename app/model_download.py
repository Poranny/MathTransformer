from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import os

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"
OUT_DIR = Path("/models/mistral")
SECRET_PATH = "/run/secrets/env_file"

def read_token():
    if os.path.exists(SECRET_PATH):
        with open(SECRET_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("HUGGING_TOKEN="):
                    return line.split("=", 1)[1]
    return os.environ.get("HUGGING_TOKEN")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    token = read_token()
    if not token:
        raise RuntimeError("No token of such name in .env")
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    mdl = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=token)
    tok.save_pretrained(OUT_DIR)
    mdl.save_pretrained(OUT_DIR)
    print(f"Model saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
