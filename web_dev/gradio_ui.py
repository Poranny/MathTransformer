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
    (function stripThemeParam() {
        const url = new URL(window.location.href);
        if (url.searchParams.has('__theme')) {
            url.searchParams.delete('__theme');
            const newUrl = url.pathname + (url.search ? '?' + url.searchParams.toString() : '') + url.hash;
            history.replaceState(null, '', newUrl);
        }
    })();

    let applying = false;
    function isLight() {
        const html = document.documentElement;
        const body = document.body;
        const gc = document.querySelector('.gradio-container');
        const htmlOk = !html.classList.contains('dark') && (html.getAttribute('data-theme') === 'light');
        const bodyOk = !body.classList.contains('dark') && ((body.getAttribute('data-theme') || 'light') === 'light');
        const gcOk = !gc || (gc.getAttribute('data-theme') === 'light');
        const schemeOk = (html.style.colorScheme || 'light') === 'light';
        return htmlOk && bodyOk && gcOk && schemeOk;
    }
    function applyLight() {
        if (applying) return;
        applying = true;
        const html = document.documentElement;
        const body = document.body;
        const gc = document.querySelector('.gradio-container');
        if (html.classList.contains('dark')) html.classList.remove('dark');
        if (html.getAttribute('data-theme') !== 'light') html.setAttribute('data-theme', 'light');
        if (html.style.colorScheme !== 'light') html.style.colorScheme = 'light';
        if (body.classList.contains('dark')) body.classList.remove('dark');
        if ((body.getAttribute('data-theme') || 'light') !== 'light') body.setAttribute('data-theme', 'light');
        if (gc && gc.getAttribute('data-theme') !== 'light') gc.setAttribute('data-theme', 'light');
        applying = false;
    }
    if (!isLight()) applyLight();
    const config = { attributes: true, attributeFilter: ['class', 'data-theme'] };
    const o = new MutationObserver(() => { if (!isLight()) applyLight(); });
    o.observe(document.documentElement, config);
    o.observe(document.body, config);
    const gc = document.querySelector('.gradio-container');
    if (gc) o.observe(gc, config);

    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.classList.add('welcome-text');
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
            }, i * 45);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    if (gradioContainer) gradioContainer.insertBefore(container, gradioContainer.firstChild);

    function setHeroHeightVar() {
        var h = container.getBoundingClientRect().height;
        var gap = 24;
        document.documentElement.style.setProperty('--hero-h', (h + gap) + 'px');
    }
    setHeroHeightVar();
    window.addEventListener('resize', setHeroHeightVar, { passive: true });

    return 'ok';
}
"""

grad_css = """
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

:root{
  --app-font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  --mono-font: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  --text-color: #222222;
  --hero-h: 0px;
}

html, body {
  height: 100%;
  width: 100%;
  max-width: 100%;
  margin: 0;
  background: #fff;
  color: var(--text-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
  font-size: 16px;
  line-height: 1.5;
}

*, *::before, *::after { box-sizing: border-box; }

.gradio-container {
  width: 100%;
  max-width: 960px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 16px;
  padding-right: 16px;
  color: var(--text-color);
}

.gradio-container * {
  font-family: var(--app-font);
  letter-spacing: .2px;
  color: inherit;
}

code, pre, kbd, samp,
.ace_editor, .cm-scroller, .json, [data-testid="json-output"] {
  font-family: var(--mono-font);
  font-variant-ligatures: contextual;
  color: var(--text-color);
}

#centerer {
  min-height: calc(70vh - var(--hero-h));
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 28px;
}

#gradio-animation.welcome-text {
  margin-top: 40px;
  margin-bottom: 0;
  pointer-events: none;
  width: 100%;
  font-family: 'Merriweather', var(--app-font);
  font-size: clamp(28px, 6vw, 38px);
}

.col-gap { gap: 48px; }

.center-btn {
  display: block;
  margin: 0 auto;
}

input, textarea, button, .btn { font-weight: 500; }

/* hide default bottom footer/buttons */
footer, footer * { display: none !important; }

/* phones portrait */
@media (max-width: 600px) {
  .gradio-container {
    padding-left: 12px;
    padding-right: 12px;
    max-width: 100%;
  }
  #centerer { min-height: calc(60vh - var(--hero-h)); }
}

/* subtle upscale for large screens */
@media (min-width: 1600px) and (min-height: 900px) {
  html { font-size: 18px; }
  .gradio-container { max-width: 1100px; }
  #centerer { gap: 32px; }
  label, .label, .input-label { font-size: 1.08rem; }
  .gradio-container :where(p,span,li,code,pre,input,textarea,button,.btn) { font-size: 1.06rem; }
}

/* bigger, but still subtle, for 1920x1080 and up */
@media (min-width: 1920px) and (min-height: 1000px) {
  html { font-size: 19px; }
  .gradio-container { max-width: 1280px; }
  #centerer { gap: 36px; }
  /* keep title size stable via px-based clamp above */
  label, .label, .input-label { font-size: 1.125rem; }
  .gradio-container :where(p,span,li,code,pre,input,textarea,button,.btn) { font-size: 1.12rem; }
}
"""

extra_css = f"""
#gradio-animation.welcome-text, #gradio-animation.welcome-text * {{
  font-family: '{WELCOME_FONT}', var(--app-font);
}}
"""

with gr.Blocks(
        theme=gr.themes.Citrus(
            spacing_size=gr.themes.sizes.spacing_lg,
            radius_size=gr.themes.sizes.text_lg,
            text_size=gr.themes.sizes.text_lg
        ),
        title="MathTransformer",
        js=js_func,
        css=grad_css + extra_css
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

demo.launch(server_name="0.0.0.0", server_port=7860, root_path="/app")
