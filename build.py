"""Build the add-on package and a theme gallery.

    python build.py

Outputs:
    dist/syntax_highlighting_ng.ankiaddon   (double-click or drag into Anki)
    dist/temas.html                         (preview of every theme)
"""

import html
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
ADDON = os.path.join(SRC, "syntax_highlighting_ng")
DIST = os.path.join(ROOT, "dist")

SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {"meta.json"}  # user settings written by Anki, never ship them


def build_package() -> str:
    os.makedirs(DIST, exist_ok=True)
    target = os.path.join(DIST, "syntax_highlighting_ng.ankiaddon")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder, dirs, files in os.walk(ADDON):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name in SKIP_FILES or name.endswith(".pyc"):
                    continue
                path = os.path.join(folder, name)
                # files must be at the root of the archive, not in a subfolder
                zf.write(path, os.path.relpath(path, ADDON))
    return target


def build_gallery() -> str:
    os.environ["STANDALONE_ADDON"] = "1"
    sys.path.insert(0, SRC)
    from syntax_highlighting_ng import html_render, themes
    from syntax_highlighting_ng.samples import SAMPLES

    cards = []
    for theme in themes.all_themes():
        block = html_render.render_block(
            SAMPLES["python"], html_render.Style(style=theme.key)
        )
        cards.append(
            f'<section><h2>{html.escape(theme.label)} <code>{theme.key}</code></h2>{block}</section>'
        )
    page = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Temas de destaque</title><style>"
        "body{font-family:system-ui,sans-serif;margin:16px;background:#f4f4f5;color:#18181b}"
        "main{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}"
        "section{background:#fff;border-radius:8px;padding:8px 12px}"
        "h2{font-size:15px}code{font-size:12px;color:#71717a}"
        "table{width:100%;border-collapse:collapse}td{padding:0}"
        "@media (prefers-color-scheme: dark){body{background:#18181b;color:#f4f4f5}section{background:#27272a}}"
        "</style></head><body><h1>Syntax Highlighting (NG) — temas</h1><main>"
        + "".join(cards)
        + "</main></body></html>"
    )
    target = os.path.join(DIST, "temas.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(page)
    return target


if __name__ == "__main__":
    print(build_package())
    print(build_gallery())
