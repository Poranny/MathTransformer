from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Tuple, Callable
import base64
import mimetypes
import requests
import gradio as gr

try:
    from ans_code_interpret import nice_message
except Exception:

    def nice_message(code: str | None) -> str:
        return "Something went wrong. Please try again 🙂"


def read_and_fill(path: Path, mapping: Dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace(f"__{k}__", v)
    return text


def file_to_data_url(p: Path) -> str | None:
    if not p.exists():
        return None
    mt, _ = mimetypes.guess_type(p.name)
    if not mt:
        mt = "image/png"
    b = p.read_bytes()
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:{mt};base64,{b64}"


def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _skeleton_card(title: str, lines: int = 4) -> str:
    lines_html = "".join("<div class='mt-skel-line'></div>" for _ in range(lines))
    return (
        f"<div class='mt-card skeleton'>"
        f"<div class='mt-card-title'><div class='mt-skel-chip'></div><span>{_escape_html(title)}</span></div>"
        f"<div class='mt-skel-body'>{lines_html}</div>"
        f"</div>"
    )


def _render_symbols(data: Dict[str, Any]) -> str:
    items = [str(x) for x in (data.get("symbols") or [])]
    if not items:
        body = "<div class='mt-empty'>Empty</div>"
    else:
        body = (
            "<ul class='mt-list'>"
            + "".join(f"<li><code>{_escape_html(x)}</code></li>" for x in items)
            + "</ul>"
        )
    return f"<div class='mt-card'><div class='mt-card-title'>Symbols</div>{body}</div>"


def _render_equations(data: Dict[str, Any]) -> str:
    eqs = [str(x) for x in (data.get("equations") or [])]
    if not eqs:
        body = "<div class='mt-empty'>Empty</div>"
    else:
        body = (
            "<ol class='mt-list'>"
            + "".join(f"<li><code>{_escape_html(x)}</code></li>" for x in eqs)
            + "</ol>"
        )
    return (
        f"<div class='mt-card'><div class='mt-card-title'>Equations</div>{body}</div>"
    )

def _render_solution(data: Dict[str, Any]) -> str:
    sol = data.get("solution") or {}

    def _format_val(v):
        s = str(v).strip()

        m = re.match(
            r"""^\s*
                ([+-]?\d+(?:\.\d+)?)        # real
                \s*([+-])\s*                # znak między Re i Im
                (\d+(?:\.\d+)?)             # moduł części urojonej
                \s*[iI]\s*$                 # i/I
            """,
            s,
            re.X,
        )
        if m:
            real = float(m.group(1))
            sign = m.group(2)
            imag = float(m.group(3))
            disp = f"{real:.3f} {sign} {abs(imag):.3f}i"
            return disp, True, True

        m = re.match(
            r"""^\s*
                ([+-]?\d+(?:\.\d+)?)
                \s*[iI]\s*$
            """,
            s,
            re.X,
        )
        if m:
            imag = float(m.group(1))
            sign = "-" if imag < 0 else ""
            disp = f"{sign}{abs(imag):.3f}i"
            return disp, True, True

        m = re.match(r"^\s*([+-]?)\s*[iI]\s*$", s)
        if m:
            sign = "-" if m.group(1) == "-" else ""
            disp = f"{sign}1.000i"
            return disp, True, True

        approx = False
        m = re.match(r"^\s*([+-]?\d+)\.(\d+)\s*$", s)
        if m and len(m.group(2)) > 3:
            try:
                s = f"{float(s):.3f}"
                approx = True
            except Exception:
                pass

        has_imag = bool(re.search(r'(?<![A-Za-z_])[iI](?![A-Za-z0-9_])', s))
        if has_imag:
            approx = True

        return s, approx, has_imag

    def _kv_lines(d: Dict[str, Any]) -> tuple[str, bool, bool]:
        lines = []
        any_approx = False
        any_imag = False
        for k, v in sorted(d.items(), key=lambda kv: str(kv[0])):
            disp, approx, has_imag = _format_val(v)
            any_approx |= approx
            any_imag |= has_imag
            op = "≈" if approx else "="

            lines.append(
                f"<div class='mt-kv'><code>{_escape_html(str(k))} {op} {_escape_html(disp)}</code></div>"
            )
        return "<div class='mt-kv-list'>" + "".join(lines) + "</div>", any_approx, any_imag

    if isinstance(sol, dict) and sol.get("result") == []:
        from ans_code_interpret import nice_message
        body = f"<div class='mt-empty'>{_escape_html(nice_message('NO_SOLUTION'))}</div>"

    elif isinstance(sol, dict) and isinstance(sol.get("solutions"), list):
        many = len(sol["solutions"]) > 1
        blocks = []
        for i, item in enumerate(sol["solutions"], start=1):
            is_complex = False
            any_approx = False

            if isinstance(item, dict) and item:
                inner, any_approx, is_complex = _kv_lines(item)
            else:
                disp, approx, has_imag = _format_val(item)
                any_approx = approx
                is_complex = has_imag
                op = "≈" if approx else "="

                inner = f"<div class='mt-kv'><code>{_escape_html(op + ' ' + disp if not isinstance(item, str) else disp)}</code></div>"

            if many:
                suffix = " <span class='mt-badge-complex'>(complex)</span>" if is_complex else ""
                head = f"<div class='mt-subhead'><span class='mt-chip'>#{i}</span>{suffix}</div>"
            else:
                head = ""

            sub_cls = " mt-subcard--complex" if is_complex else ""
            blocks.append(f"<div class='mt-subcard mt-micro{sub_cls}'>{head}{inner}</div>")

        body = "<div class='mt-multi-list'>" + "".join(blocks) + "</div>"

    elif isinstance(sol, dict) and isinstance(sol.get("results"), list):
        items = []
        for idx, v in enumerate(sol["results"], start=1):
            disp, approx, has_imag = _format_val(v)
            op = "≈" if approx else "="
            li_cls = " class='mt-li--complex'" if has_imag else ""
            label = f"<span class='mt-li-chip'>#{idx}</span>" + ("" if not has_imag else " <span class='mt-badge-complex'>(complex)</span>")
            items.append(f"<li{li_cls}><code>{label} { _escape_html(op + ' ' + disp if not isinstance(v, str) else disp) }</code></li>")
        body = "<ol class='mt-list mt-list--solutions'>" + "".join(items) + "</ol>"

    elif isinstance(sol, dict) and sol:
        inner, any_approx, is_complex = _kv_lines(sol)
        sub_cls = " mt-subcard--complex" if is_complex else ""
        body = f"<div class='mt-subcard mt-micro{sub_cls}'>{inner}</div>"

    else:
        body = "<div class='mt-empty'>Empty</div>"

    return f"<div class='mt-card'><div class='mt-card-title'>Solution</div>{body}</div>"

def _error_box_html(user_message: str) -> str:
    return (
        "<div class='mt-error-card'>"
        "<div class='mt-error-title'>Oops!</div>"
        f"<div class='mt-error-body'>{_escape_html(user_message)}</div>"
        "</div>"
    )

def _ask(api_base: str, prompt: str) -> dict:
    if not prompt.strip():
        return {"ok": False, "code": "PROMPT_INVALID"}

    try:
        r = requests.post(f"{api_base}/answer", json={"prompt": prompt}, timeout=300)
    except requests.RequestException:
        return {"ok": False, "code": "NETWORK_ERROR"}

    try:
        payload = r.json()
    except ValueError:
        payload = None

    if r.ok:
        return {"ok": True, "data": payload}

    detail = (payload or {}).get("detail")
    code = (detail or {}).get("code") if isinstance(detail, dict) else None
    return {"ok": False, "code": code or "UNKNOWN_ERROR"}


def build_handlers(
    api_base: str,
) -> Tuple[
    Callable[[], Tuple[Any, Any, Any, Any]], Callable[[str], Tuple[Any, Any, Any, Any]]
]:
    def start_loading() -> Tuple[Any, Any, Any, Any]:
        return (
            gr.update(visible=True, value=_skeleton_card("Symbols", lines=5)),
            gr.update(visible=True, value=_skeleton_card("Equations", lines=5)),
            gr.update(visible=True, value=_skeleton_card("Solution", lines=4)),
            gr.update(visible=False, value=""),
        )

    def handle(prompt: str) -> Tuple[Any, Any, Any, Any]:
        res = _ask(api_base, prompt)

        if res.get("ok"):
            data = res.get("data") or {}
            return (
                gr.update(visible=True, value=_render_symbols(data)),
                gr.update(visible=True, value=_render_equations(data)),
                gr.update(visible=True, value=_render_solution(data)),
                gr.update(visible=False, value=""),
            )

        code = res.get("code")
        user_msg = nice_message(code)
        return (
            gr.update(visible=False, value=""),
            gr.update(visible=False, value=""),
            gr.update(visible=False, value=""),
            gr.update(visible=True, value=_error_box_html(user_msg)),
        )

    return start_loading, handle


def instructions_html() -> str:
    return """
        <div class="mt-info-title">
          <img class="mt-info-icon" src="https://cdn.jsdelivr.net/npm/bootstrap-icons/icons/journal-text.svg" alt="Instructions">
          <h3>How to use</h3>
        </div>
        The service turns a natural-language description of an equation into real math - and solves it.
        <ul>
          <li>Describe your equation in English; be as creative as you like!</li>
          <li>Examples: <code>x plus one equals 10</code>, or
          <code>a times two is equal to 59.5 divided by b... and b = 7</code></li>
          <li>Press <strong>Solve</strong> and wait for the results to appear :)</li>
        </ul>

        <p class="mt-info-note">
          Sidenote: Currently supported operations are addition, subtraction, multiplication, division, and exponentiation.
          You can also use parentheses <code>( )</code>. Constant <code>π</code> is supported.
          Trigonometric functions (sine, tan, and more) and complex operations are on the way - stay tuned!
        </p>
    """
