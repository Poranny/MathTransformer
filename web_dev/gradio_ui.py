import os
from pathlib import Path
import base64
import mimetypes
import requests
import gradio as gr
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env", override=False)

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
WELCOME_FONT = os.getenv("WELCOME_FONT", "Merriweather")

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
CONTACT_LINKEDIN = os.getenv("CONTACT_LINKEDIN", "")
CONTACT_GITHUB = os.getenv("CONTACT_GITHUB", "")

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://mathtransformer.app/")
OG_TITLE = os.getenv("OG_TITLE", "MathTransformer")
OG_DESC  = os.getenv("OG_DESC", "Solving math equations from natural language descriptions")
OG_IMAGE = os.getenv("OG_IMAGE", "https://mathtransformer.app/og-image.png")

HEAD_HTML = f"""
<link rel="icon" href="/og-image.png" type="image/png" sizes="32x32">
"""

def _read_and_fill(path: Path, mapping: dict) -> str:
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

def _file_to_data_url(p: Path) -> str | None:
    if not p.exists():
        return None
    mt, _ = mimetypes.guess_type(p.name)
    if not mt:
        mt = "image/png"
    b = p.read_bytes()
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:{mt};base64,{b64}"

CANDIDATES = [
    HERE / "static" / "og-image-big.png",
    Path("/home/app/static/og-image-big.png"),
]
LOGO_DATA_URL = None
for cand in CANDIDATES:
    LOGO_DATA_URL = _file_to_data_url(cand)
    if LOGO_DATA_URL:
        break

if not LOGO_DATA_URL:
    LOGO_DATA_URL = OG_IMAGE


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
    css=css_code,
    head=HEAD_HTML
) as demo:

    gr.HTML(
        f'<div id="mt_logo_wrap"><a id="mt_logo_btn" href="#" onclick="window.location.reload();return false;" aria-label="Reload"><img src="{LOGO_DATA_URL}" alt="Logo"></a></div>',
        visible=True
    )

    with gr.Column(elem_id="centerer", elem_classes=["col-gap"]):
        inp = gr.Textbox(
            label="Prompt",
            lines=1,
            placeholder="a minus twentyone is equal to 0...",
            autofocus=True,
            html_attributes={"spellcheck": "false", "autocorrect": "off"}
        )
        btn = gr.Button("Send", size="lg", variant="primary", elem_classes=["center-btn"])
        out = gr.JSON(label="Answer")
        btn.click(ask, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
