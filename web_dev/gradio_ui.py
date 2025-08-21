from __future__ import annotations
import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv

from gradio_ui_helpers import (
    build_handlers,
    file_to_data_url,
    read_and_fill,
    instructions_html,
)

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env", override=False)

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
WELCOME_FONT = os.getenv("WELCOME_FONT", "Merriweather")

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
CONTACT_LINKEDIN = os.getenv("CONTACT_LINKEDIN", "")
CONTACT_GITHUB = os.getenv("CONTACT_GITHUB", "")

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://mathtransformer.app/")
OG_TITLE = os.getenv("OG_TITLE", "MathTransformer")
OG_DESC = os.getenv(
    "OG_DESC", "Solving math equations from natural language descriptions"
)
OG_IMAGE = os.getenv("OG_IMAGE", "https://mathtransformer.app/og-image.png")

HEAD_HTML = """
<link rel="icon" href="/og-image.png" type="image/png" sizes="32x32">
"""

CANDIDATES = [
    HERE / "static" / "og-image-big.png",
    Path("/home/app/static/og-image-big.png"),
]
LOGO_DATA_URL = None
for cand in CANDIDATES:
    LOGO_DATA_URL = file_to_data_url(cand)
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
js_code = read_and_fill(HERE / "app.js", placeholders)
css_code = read_and_fill(HERE / "styles.css", placeholders)

start_loading, handle = build_handlers(api_base=API)

with gr.Blocks(
    theme=gr.themes.Citrus(
        spacing_size=gr.themes.sizes.spacing_lg,
        radius_size=gr.themes.sizes.text_lg,
        text_size=gr.themes.sizes.text_lg,
    ),
    title="MathTransformer",
    js=js_code,
    css=css_code,
    head=HEAD_HTML,
) as demo:

    gr.HTML(
        f'<div id="mt_logo_wrap"><a id="mt_logo_btn" href="#" onclick="window.location.reload();return false;" aria-label="Reload"><img src="{LOGO_DATA_URL}" alt="Logo"></a></div>',
        visible=True,
    )

    with gr.Column(elem_id="centerer", elem_classes=["col-gap"]):
        instructions = gr.Markdown(
            instructions_html(),
            elem_id="mt-instructions",
        )

        inp = gr.Textbox(
            label="Your equation",
            lines=1,
            placeholder="x minus twenty-one is equal to 0...",
            autofocus=True,
            html_attributes={"spellcheck": "false", "autocorrect": "off"},
        )
        btn = gr.Button(
            "Solve", size="lg", variant="primary", elem_classes=["center-btn"]
        )

        with gr.Row(elem_id="mt-row", equal_height=True):
            out_symbols = gr.HTML(value="", label=None, visible=True)
            out_equations = gr.HTML(value="", label=None, visible=True)
            out_solution = gr.HTML(value="", label=None, visible=True)

        err_box = gr.HTML(
            value="",
            visible=False,
            elem_id="mt-error-box",
            elem_classes=["mt-error", "mt-error-rounded"],
        )

        btn.click(
            start_loading,
            inputs=None,
            outputs=[out_symbols, out_equations, out_solution, err_box],
            show_progress="hidden",
        ).then(
            handle,
            inputs=inp,
            outputs=[out_symbols, out_equations, out_solution, err_box],
            show_progress="hidden",
        )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
