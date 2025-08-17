import os
from pathlib import Path
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
API = os.getenv("API_BASE", "http://127.0.0.1:8000")
WELCOME_FONT = os.getenv("WELCOME_FONT", "Merriweather")

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
CONTACT_LINKEDIN = os.getenv("CONTACT_LINKEDIN", "")
CONTACT_GITHUB = os.getenv("CONTACT_GITHUB", "")

HERE = Path(__file__).resolve().parent

def _read_and_fill(path: Path, mapping: dict) -> str:
    """Wczytaj plik i podmień placeholdery w formacie __PLACEHOLDER__."""
    text = path.read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace(f"__{k}__", v)
    return text

def ask(prompt: str):
    if not prompt.strip():
        return {"error": "Prompt is empty"}
    try:
        r = requests.post(f"{API}/answer", json={"prompt": prompt}, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# Wczytaj zewnętrzny JS i CSS (zastępując placeholdery)
placeholders = {
    "CONTACT_EMAIL": CONTACT_EMAIL,
    "CONTACT_LINKEDIN": CONTACT_LINKEDIN,
    "CONTACT_GITHUB": CONTACT_GITHUB,
    "WELCOME_FONT": WELCOME_FONT,
}

js_code = _read_and_fill(HERE / "app.js", placeholders)
css_code = _read_and_fill(HERE / "styles.css", placeholders)

with gr.Blocks(
    theme=gr.themes.Citrus(
        spacing_size=gr.themes.sizes.spacing_lg,
        radius_size=gr.themes.sizes.text_lg,
        text_size=gr.themes.sizes.text_lg
    ),
    title="MathTransformer",
    js=js_code,
    css=css_code
) as demo:
    with gr.Column(elem_id="centerer", elem_classes=["col-gap"]):
        inp = gr.Textbox(
            label="Prompt",
            lines=1,
            placeholder="a minus twentyone is equal to 0...",
            autofocus=True
        )
        btn = gr.Button("Send", size="lg", variant="primary", elem_classes=["center-btn"])
        out = gr.JSON(label="Answer")
        btn.click(ask, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, root_path="/app")
