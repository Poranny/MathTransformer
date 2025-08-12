from pathlib import Path
import os

from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"
OUT_DIR = Path("/models/mistral")
SECRET_PATH = "/run/secrets/env_file"
TOKEN_NAME = 'HUGGING_TOKEN'

def read_token():
    if os.path.exists(SECRET_PATH):
        with open(SECRET_PATH) as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#") and s.startswith(f"{TOKEN_NAME}="):
                    return s.split("=", 1)[1]

    return os.environ.get(f"{TOKEN_NAME}")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    token = read_token()
    if not token:
        raise SystemExit(f"No {TOKEN_NAME}.")
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    mdl = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=token)
    tok.save_pretrained(OUT_DIR)
    mdl.save_pretrained(OUT_DIR)
    print(f"Model saved to {OUT_DIR}")

if __name__ == "__main__":
    main()
