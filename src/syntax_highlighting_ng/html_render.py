# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Pure rendering functions (no Anki imports, so they can be unit tested).

License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import annotations

import dataclasses as dc
import html
import re

import pygments
import pygments.lexers
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from . import themes


@dc.dataclass
class Style:
    language: str = "python"  # pygments lexer alias
    style: str = themes.DEFAULT_THEME  # theme key (see themes.py)
    linenos: bool = True
    noclasses: bool = True  # inline colors (True) or css classes (False)
    center: bool = False


class RenderError(Exception):
    def render(self) -> str:
        raise NotImplementedError("adds .render method")


class LanguageNotFound(RenderError):
    def render(self) -> str:
        return f"""
<b>Erro</b>: a linguagem '{html.escape(str(self.args[0]))}' não foi encontrada.<br>
Se você definiu uma lista personalizada em <i>limitToLangs</i>,<br>
confira se todos os nomes estão escritos corretamente.
"""


class InvalidStyle(RenderError):
    def render(self) -> str:
        return f"""
<b>Erro</b>: o tema '{html.escape(str(self.args[0]))}' não foi encontrado.<br>
Escolha outro tema em Ferramentas → Syntax Highlighting.
"""


BLOCK_CSS = (
    "padding: 0.6em 0.9em; border-radius: 6px; overflow-x: auto; "
    "border: 1px solid rgba(127, 127, 127, 0.25); "
    "text-align: left; margin: 0.3em 0;"
)
PRE_CSS = "margin: 0; white-space: pre"


def css_class(theme_key: str) -> str:
    """Per-theme css class, so different themes can coexist in a note type"""
    return "sh-" + re.sub(r"[^a-zA-Z0-9_-]", "-", theme_key)


def _formatter(style: Style) -> HtmlFormatter:
    try:
        pyg_style = themes.with_dimmed_linenos(themes.get_style(style.style))
    except ClassNotFound as exc:
        raise InvalidStyle(style.style) from exc

    options: dict = dict(
        style=pyg_style,
        linenos="inline" if style.linenos else False,
        noclasses=style.noclasses,
        prestyles=PRE_CSS,
    )
    if style.noclasses:
        _, fg = themes.base_colors(pyg_style)
        options["cssstyles"] = f"color: {fg}; {BLOCK_CSS}"
    else:
        options["cssclass"] = f"highlight {css_class(style.style)}"
    return HtmlFormatter(**options)


def render_string(txt: str, style: Style = Style()) -> str:
    """Highlight txt and return the bare pygments html"""
    try:
        lexer = pygments.lexers.get_lexer_by_name(style.language, stripall=True)
    except ClassNotFound as exc:
        raise LanguageNotFound(style.language) from exc

    formatter = _formatter(style)
    out = pygments.highlight(txt, lexer, formatter)
    if style.noclasses:
        # mark the inline line numbers, so the code can be recovered from the
        # field later (eg. to change the theme of an existing block)
        for line_css in (formatter._linenos_style, formatter._linenos_special_style):
            out = out.replace(
                f'<span style="{line_css}">', f'<span class="{LINENO_CLASS}" style="{line_css}">'
            )
        out = _STYLE_ATTR.sub(lambda m: f'style="{_nudge_colors(m.group(1))}"', out)
    return out


# Chromium's insertHTML drops inline colors equal to the editor defaults (pure
# white background, pure black text), and the card would then lose them (eg. in
# night mode). Visually identical colors are kept. Only style attributes are
# touched: the code itself is html-escaped text and never contains style="".
_STYLE_ATTR = re.compile(r'style="([^"]*)"')
_PURE_COLORS = (
    (re.compile(r"#(?:ffffff|fff)\b", re.I), "#fefefe"),
    (re.compile(r"#(?:000000|000)\b", re.I), "#010101"),
)


def _nudge_colors(css: str) -> str:
    for pattern, replacement in _PURE_COLORS:
        css = pattern.sub(replacement, css)
    return css


# Marks a highlighted block in a field, with the data needed to re-render it
BLOCK_CLASS = "sh-block"
LINENO_CLASS = "sh-ln"


def render_block(txt: str, style: Style = Style(), trailing_br: bool = True) -> str:
    """Highlight txt and wrap it into html ready to be inserted in a field"""
    processed = render_string(txt, style)
    table_css = ' style="margin-left: auto; margin-right: auto;"' if style.center else ""
    attrs = (
        f'class="{BLOCK_CLASS}" '
        f'data-sh-lang="{html.escape(style.language, quote=True)}" '
        f'data-sh-theme="{html.escape(style.style, quote=True)}"'
    )
    # the table keeps the editor from merging the block with the
    # surrounding text; the trailing <br> lets the user keep typing after it
    pretty = f"<table {attrs}{table_css}><tbody><tr><td>{processed}</td></tr></tbody></table>"
    if trailing_br:
        pretty += "<br>"
    return process_html(pretty)


def process_html(html_: str) -> str:
    """Modify highlighter output to address some Anki idiosyncracies"""
    # "Escape" curly bracket sequences reserved to Anki's card template
    # system by placing an invisible html tag inbetween
    for pattern, replacement in (
        (r"{{", r"{<!---->{"),
        (r"}}", r"}<!---->}"),
        (r"::", r":<!---->:"),
    ):
        html_ = re.sub(pattern, replacement, html_)
    return html_


def theme_css(theme_key: str) -> str:
    """CSS to paste into a note type's Styling, for the css classes mode"""
    try:
        pyg_style = themes.get_style(theme_key)
    except ClassNotFound as exc:
        raise InvalidStyle(theme_key) from exc
    selector = "." + css_class(theme_key)
    _, fg = themes.base_colors(pyg_style)
    defs = HtmlFormatter(style=themes.with_dimmed_linenos(pyg_style)).get_style_defs(selector)
    header = f"/* Syntax Highlighting — {themes.theme_label(theme_key)} */\n"
    block = f"{selector} {{ color: {fg}; {BLOCK_CSS} }}\n{selector} pre {{ {PRE_CSS} }}\n"
    return header + block + defs + "\n"


def languages() -> dict[str, str]:
    """Map of language display name -> pygments alias"""
    return {
        name: aliases[0]
        for name, aliases, _, _ in pygments.lexers.get_all_lexers()
        if aliases
    }
