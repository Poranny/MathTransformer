import os, requests, gradio as gr
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
WELCOME_FONT = "Merriweather"

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
CONTACT_LINKEDIN = os.getenv("CONTACT_LINKEDIN", "")
CONTACT_GITHUB = os.getenv("CONTACT_GITHUB", "")

def ask(prompt: str):
    if not prompt.strip():
        return {"error": "Prompt is empty"}
    try:
        r = requests.post(f"{API}/answer", json={"prompt": prompt}, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

js_func = f"""
function refresh() {{
    (function stripThemeParam() {{
        const url = new URL(window.location.href);
        if (url.searchParams.has('__theme')) {{
            url.searchParams.delete('__theme');
            const newUrl = url.pathname + (url.search ? '?' + url.searchParams.toString() : '') + url.hash;
            history.replaceState(null, '', newUrl);
        }}
    }})();

    let applying = false;
    function isLight() {{
        const html = document.documentElement;
        const body = document.body;
        const gc = document.querySelector('.gradio-container');
        const htmlOk = !html.classList.contains('dark') && (html.getAttribute('data-theme') === 'light');
        const bodyOk = !body.classList.contains('dark') && ((body.getAttribute('data-theme') || 'light') === 'light');
        const gcOk = !gc || (gc.getAttribute('data-theme') === 'light');
        const schemeOk = (html.style.colorScheme || 'light') === 'light';
        return htmlOk && bodyOk && gcOk && schemeOk;
    }}
    function applyLight() {{
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
    }}
    if (!isLight()) applyLight();
    const config = {{ attributes: true, attributeFilter: ['class', 'data-theme'] }};
    const o = new MutationObserver(() => {{ if (!isLight()) applyLight(); }});
    o.observe(document.documentElement, config);
    o.observe(document.body, config);
    const gcObsTarget = document.querySelector('.gradio-container');
    if (gcObsTarget) o.observe(gcObsTarget, config);

    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.classList.add('welcome-text');
    container.style.textAlign = 'center';

    var text = 'Welcome to MathTransformer!';
    for (var i = 0; i < text.length; i++) {{
        (function(i){{
            setTimeout(function(){{
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.5s';
                letter.innerText = text[i];
                container.appendChild(letter);
                setTimeout(function() {{ letter.style.opacity = '1'; }}, 50);
            }}, i * 45);
        }})(i);
    }}

    var gradioContainer = document.querySelector('.gradio-container');
    if (gradioContainer) gradioContainer.insertBefore(container, gradioContainer.firstChild);

    function setHeroHeightVar() {{
        var h = container.getBoundingClientRect().height;
        var gap = 24;
        document.documentElement.style.setProperty('--hero-h', (h + gap) + 'px');
    }}
    setHeroHeightVar();
    window.addEventListener('resize', setHeroHeightVar, {{ passive: true }});

    function createContactUI(){{
        if (document.getElementById('contact-footer')) return;

        const footer = document.createElement('div');
        footer.id = 'contact-footer';
        footer.textContent = 'Get in touch!';
        document.body.appendChild(footer);

        const overlay = document.createElement('div');
        overlay.id = 'contact-overlay';
        overlay.setAttribute('aria-hidden','true');

        const backdrop = document.createElement('div');
        backdrop.className = 'contact-backdrop';

        const drawer = document.createElement('div');
        drawer.className = 'contact-drawer';
        drawer.setAttribute('role','dialog');
        drawer.setAttribute('aria-modal','true');
        drawer.setAttribute('aria-labelledby','contact-title');

        const closeBtn = document.createElement('button');
        closeBtn.id = 'contact-close';
        closeBtn.setAttribute('aria-label','Close');
        closeBtn.innerHTML = '×';

        const content = document.createElement('div');
        content.className = 'contact-content';
        content.innerHTML = `
            <h3 id="contact-title">Found a bug? Or just want to say hi? Get in touch :)</h3>
            <p class="copyright">© Adam Malinowski</p>
            <ul class="links">
              <li>
                <a href="mailto:{CONTACT_EMAIL}">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5L4 8V6l8 5 8-5v2Z"/></svg>
                  {CONTACT_EMAIL}
                </a>
              </li>
              <li>
                <a href="{CONTACT_LINKEDIN}" target="_blank" rel="noopener">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.447 20.452h-3.554V14.86c0-1.333-.026-3.049-1.859-3.049-1.861 0-2.146 1.45-2.146 2.949v5.692H9.333V9h3.414v1.561h.049c.476-.9 1.637-1.85 3.368-1.85 3.602 0 4.268 2.37 4.268 5.455v6.286zM5.337 7.433a2.062 2.062 0 11-.004-4.124 2.062 2.062 0 01.004 4.124zM6.777 20.452H3.893V9h2.884v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.226.792 24 1.771 24h20.451C23.2 24 24 23.226 24 22.271V1.729C24 .774 23.2 0 22.222 0z"/></svg>
                  LinkedIn
                </a>
              </li>
              <li>
                <a href="{CONTACT_GITHUB}" target="_blank" rel="noopener">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.39.6.1.82-.26.82-.58 0-.29-.01-1.04-.02-2.04-3.34.73-4.04-1.61-4.04-1.61-.55-1.4-1.34-1.78-1.34-1.78-1.1-.75.08-.74.08-.74 1.22.09 1.86 1.25 1.86 1.25 1.08 1.85 2.83 1.31 3.52 1 .11-.8.42-1.31.76-1.61-2.67-.3-5.47-1.34-5.47-5.96 0-1.32.47-2.4 1.24-3.25-.12-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 016 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.65.24 2.87.12 3.17.77.85 1.24 1.93 1.24 3.25 0 4.63-2.8 5.66-5.48 5.96.43.37.81 1.1.81 2.22 0 1.6-.02 2.88-.02 3.27 0 .32.22.7.83.58C20.56 21.8 24 17.3 24 12 24 5.37 18.63 0 12 0z"/></svg>
                  GitHub
                </a>
              </li>
            </ul>
        `;

        drawer.appendChild(closeBtn);
        drawer.appendChild(content);
        overlay.appendChild(backdrop);
        overlay.appendChild(drawer);
        document.body.appendChild(overlay);

        function openDrawer(){{
            overlay.classList.add('open');
            overlay.setAttribute('aria-hidden','false');
            document.documentElement.classList.add('contact-dim');
        }}
        function closeDrawer(){{
            overlay.classList.remove('open');
            overlay.setAttribute('aria-hidden','true');
            document.documentElement.classList.remove('contact-dim');
        }}

        footer.addEventListener('click', openDrawer);
        closeBtn.addEventListener('click', closeDrawer);
        backdrop.addEventListener('click', closeDrawer);
        document.addEventListener('keydown', (e)=>{{ if(e.key === 'Escape') closeDrawer(); }});

        return {{ openDrawer, closeDrawer }};
    }}

    createContactUI();

    return 'ok';
}}
"""

grad_css = """
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

:root{
  --app-font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  --mono-font: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  --text-color: #222222;
  --hero-h: 0px;
  --muted: #6b7280;
  --border: #e5e7eb;
  --shadow: 0 6px 30px rgba(0,0,0,.12);
  --overlay-bg: rgba(0,0,0,.35);
  --surface: #ffffff;
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

footer, footer * { display: none !important; }

@media (max-width: 600px) {
  .gradio-container {
    padding-left: 12px;
    padding-right: 12px;
    max-width: 100%;
  }
  #centerer { min-height: calc(60vh - var(--hero-h)); }
}

@media (min-width: 1600px) and (min-height: 900px) {
  html { font-size: 18px; }
  .gradio-container { max-width: 1100px; }
  #centerer { gap: 32px; }
  label, .label, .input-label { font-size: 1.08rem; }
  .gradio-container :where(p,span,li,code,pre,input,textarea,button,.btn,a) { font-size: 1.06rem; }
}

@media (min-width: 1920px) and (min-height: 1000px) {
  html { font-size: 19px; }
  .gradio-container { max-width: 1280px; }
  #centerer { gap: 36px; }
  label, .label, .input-label { font-size: 1.125rem; }
  .gradio-container :where(p,span,li,code,pre,input,textarea,button,.btn,a) { font-size: 1.12rem; }
}

#contact-footer{
  position: fixed;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%);
  background: var(--surface);
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.95rem;
  line-height: 1;
  box-shadow: var(--shadow);
  z-index: 60;
  cursor: pointer;
  user-select: none;
  transition: transform .12s ease, box-shadow .12s ease, color .12s ease;
}
#contact-footer:hover{ transform: translateX(-50%) translateY(-1px); color: #4b5563; }
#contact-footer:active{ transform: translateX(-50%) translateY(0); }

#contact-overlay{
  position: fixed;
  inset: 0;
  z-index: 80;
  pointer-events: none;
}
#contact-overlay .contact-backdrop{
  position: absolute;
  inset: 0;
  background: var(--overlay-bg);
  opacity: 0;
  transition: opacity .25s ease;
}
#contact-overlay .contact-drawer{
  position: absolute;
  left: 0; right: 0; bottom: 0;
  background: var(--surface);
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  box-shadow: 0 -10px 40px rgba(0,0,0,.18);
  transform: translateY(102%);
  transition: transform .28s ease;
  padding: 18px 20px 24px;
  max-width: 720px;
  margin: 0 auto;
}
#contact-overlay.open{ pointer-events: auto; }
#contact-overlay.open .contact-backdrop{ opacity: 1; }
#contact-overlay.open .contact-drawer{ transform: translateY(0); }

#contact-close{
  position: absolute;
  top: 8px;
  right: 12px;
  border: 0;
  background: transparent;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  color: var(--muted);
}
#contact-close:hover{ color: #4b5563; }

.contact-content{
  color: var(--text-color);
}
.contact-content h3{
  margin: 6px 0 8px;
  font-size: 1.15rem;
  color: var(--text-color);
}
.contact-content .copyright{
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 0.95rem;
}
.contact-content .links{
  list-style: none;
  padding: 8px 0 0;
  margin: 0;
  display: grid;
  gap: 10px;
}
.contact-content .links a{
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-color);
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
}
.contact-content .links a:hover{
  background: #fafafa;
}
.icon{
  width: 20px;
  height: 20px;
  display: inline-block;
  fill: currentColor;
}

.contact-dim body{ }
.contact-dim .gradio-container{ filter: none; }
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
