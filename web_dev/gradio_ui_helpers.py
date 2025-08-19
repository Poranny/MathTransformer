from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple, Callable
import base64
import mimetypes
import requests


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
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )

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
        body = "<ul class='mt-list'>" + "".join(
            f"<li><code>{_escape_html(x)}</code></li>" for x in items
        ) + "</ul>"
    return f"<div class='mt-card'><div class='mt-card-title'>Symbols</div>{body}</div>"

def _render_equations(data: Dict[str, Any]) -> str:
    eqs = [str(x) for x in (data.get("equations") or [])]
    if not eqs:
        body = "<div class='mt-empty'>Empty</div>"
    else:
        body = "<ol class='mt-list'>" + "".join(
            f"<li><code>{_escape_html(x)}</code></li>" for x in eqs
        ) + "</ol>"
    return f"<div class='mt-card'><div class='mt-card-title'>Equations</div>{body}</div>"

def _render_solution(data: Dict[str, Any]) -> str:
    sol = data.get("solution") or {}
    if not sol:
        body = "<div class='mt-empty'>Empty</div>"
    else:
        lines = []
        for k, v in sorted(sol.items(), key=lambda kv: str(kv[0])):
            lines.append(
                f"<div class='mt-kv'><code>{_escape_html(str(k))} = {_escape_html(str(v))}</code></div>"
            )
        body = "<div class='mt-kv-list'>" + "".join(lines) + "</div>"
    return f"<div class='mt-card'><div class='mt-card-title'>Solution</div>{body}</div>"

def _format_error(msg: str) -> Tuple[str, str, str]:
    html = (
        "<div class='mt-card error'>"
        "<div class='mt-card-title'>Error</div>"
        f"<p class='mt-error'>{_escape_html(msg)}</p></div>"
    )
    return html, html, html


def _ask(api_base: str, prompt: str) -> Dict[str, Any] | Dict[str, str]:
    if not prompt.strip():
        return {"error": "Prompt is empty"}
    try:
        r = requests.post(f"{api_base}/answer", json={"prompt": prompt}, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def build_handlers(api_base: str) -> Tuple[
    Callable[[], Tuple[str, str, str]],
    Callable[[str], Tuple[str, str, str]]
]:
    def start_loading() -> Tuple[str, str, str]:
        return (
            _skeleton_card("Symbols", lines=5),
            _skeleton_card("Equations", lines=5),
            _skeleton_card("Solution", lines=4),
        )

    def handle(prompt: str) -> Tuple[str, str, str]:
        res = _ask(api_base, prompt)
        if isinstance(res, dict) and "error" in res:
            return _format_error(res["error"])
        if not isinstance(res, dict):
            return _format_error("Invalid response from API")
        return (
            _render_symbols(res),
            _render_equations(res),
            _render_solution(res),
        )

    return start_loading, handle
