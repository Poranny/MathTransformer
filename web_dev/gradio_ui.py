import os, requests, gradio as gr

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
WELCOME_FONT = "Merriweather"

def ask(prompt: str):
    if not prompt.strip():
        return {"error": "Prompt is empty"}
    try:
        r = requests.post(f"{API}/answer", json={"prompt": prompt}, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

js_func = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }

    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.classList.add('welcome-text');
    container.style.fontSize = '2.6em';
    container.style.textAlign = 'center';

    var text = 'Welcome to MathTransformer!';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.5s';
                letter.innerText = text[i];
                container.appendChild(letter);
                setTimeout(function() { letter.style.opacity = '1'; }, 50);
            }, i * 50);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);
    return 'Animation created';
}
"""

grad_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..900&family=JetBrains+Mono:wght@300..800&family=DM+Serif+Display:ital@0;1&family=Cormorant+Garamond:wght@400;600&family=Abril+Fatface&family=Cinzel:wght@400;700&family=Lora:wght@400;600&family=Merriweather:wght@400;700&family=Fraunces:wght@400;700&family=Spectral:wght@400;600&family=Prata&family=Marcellus&family=Libre+Baskerville:wght@400;700&display=swap');


:root{
  --app-font: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
  --mono-font: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  --text-color: #2a2a2a;
}

html, body { height: 100%; color: var(--text-color); }

html, body, .gradio-container, .gradio-container * {
  font-family: var(--app-font) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: .2px;
  color: var(--text-color) !important;
}

code, pre, kbd, samp,
.ace_editor, .cm-scroller, .json, [data-testid="json-output"] {
  font-family: var(--mono-font) !important;
  font-variant-ligatures: contextual;
}

.gradio-container {
  width: 40vw;
  min-width: 640px;
  margin: 0 auto;
  position: relative;
}

#centerer {
  min-height: 80vh;
  display: flex !important;
  flex-direction: column;
  justify-content: center;
}

#gradio-animation.welcome-text {
  position: absolute;
  top: 50px;
  left: 0;
  right: 0;
  pointer-events: none;
}

.col-gap { gap: 60px !important; }
footer{display:none !important}

.center-btn {
  display: block !important;
  margin: 0 auto !important;
}

input, textarea, button, .btn { font-weight: 500; }
"""

extra_css = f"""
#gradio-animation.welcome-text, #gradio-animation.welcome-text * {{
  font-family: '{WELCOME_FONT}', var(--app-font) !important;
}}
"""

with gr.Blocks(
        theme=gr.themes.Citrus(
            spacing_size=gr.themes.sizes.spacing_lg,
            radius_size=gr.themes.sizes.text_lg,
            text_size=gr.themes.sizes.text_lg
        ),
        js=js_func,
        css=grad_css + extra_css
) as demo:
    with gr.Column(elem_id="centerer", elem_classes=["col-gap"]):
        inp = gr.Textbox(
            label="Prompt",
            lines=1,
            placeholder="two a minus twentyone equals b...",
            autofocus=True
        )
        btn = gr.Button("Send", size="md", variant="primary", elem_classes=["center-btn"])
        out = gr.JSON(label="Answer")
        btn.click(ask, inputs=inp, outputs=out)

demo.launch(server_name="0.0.0.0", server_port=8000)
