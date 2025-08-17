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
  const gcObsTarget = document.querySelector('.gradio-container');
  if (gcObsTarget) o.observe(gcObsTarget, config);

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

  function createContactUI(){
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
          <a href="mailto:__CONTACT_EMAIL__">
            <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5L4 8V6l8 5 8-5v2Z"/></svg>
            __CONTACT_EMAIL__
          </a>
        </li>
        <li>
          <a href="__CONTACT_LINKEDIN__" target="_blank" rel="noopener">
            <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.447 20.452h-3.554V14.86c0-1.333-.026-3.049-1.859-3.049-1.861 0-2.146 1.45-2.146 2.949v5.692H9.333V9h3.414v1.561h.049c.476-.9 1.637-1.85 3.368-1.85 3.602 0 4.268 2.37 4.268 5.455v6.286zM5.337 7.433a2.062 2.062 0 11-.004-4.124 2.062 2.062 0 01.004 4.124zM6.777 20.452H3.893V9h2.884v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.226.792 24 1.771 24h20.451C23.2 24 24 23.226 24 22.271V1.729C24 .774 23.2 0 22.222 0z"/></svg>
            LinkedIn
          </a>
        </li>
        <li>
          <a href="__CONTACT_GITHUB__" target="_blank" rel="noopener">
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

    function openDrawer(){
      overlay.classList.add('open');
      overlay.setAttribute('aria-hidden','false');
      document.documentElement.classList.add('contact-dim');
    }
    function closeDrawer(){
      overlay.classList.remove('open');
      overlay.setAttribute('aria-hidden','true');
      document.documentElement.classList.remove('contact-dim');
    }

    footer.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    backdrop.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeDrawer(); });

    return { openDrawer, closeDrawer };
  }

  createContactUI();

  return 'ok';
}
