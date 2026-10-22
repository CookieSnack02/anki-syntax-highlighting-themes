# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Theme catalog: curated pygments styles plus a few popular editor themes
that pygments does not ship (GitHub Light, One Light, VS Code, Tokyo Night,
Catppuccin Mocha).

License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import annotations

import dataclasses as dc

from pygments.style import Style
from pygments.styles import get_all_styles, get_style_by_name
from pygments.token import (
    Comment,
    Error,
    Escape,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Token,
)
from pygments.util import ClassNotFound


def _palette(
    *,
    fg: str,
    comment: str,
    keyword: str,
    control: str | None = None,
    string: str,
    number: str,
    function: str,
    klass: str,
    builtin: str,
    operator: str,
    tag: str,
    attribute: str,
    variable: str | None = None,
    decorator: str | None = None,
    escape: str | None = None,
    error: str = "#f44747",
    comment_italic: bool = True,
) -> dict:
    """Build a pygments token->style dict from a compact editor palette"""
    italic = " italic" if comment_italic else ""
    variable = variable or fg
    return {
        Token: fg,
        Text: fg,
        Escape: escape or number,
        Error: error,
        Comment: comment + italic,
        Comment.Preproc: control or keyword,
        Comment.PreprocFile: string,
        Keyword: keyword,
        Keyword.Namespace: control or keyword,
        Keyword.Constant: number,
        Keyword.Type: klass,
        Operator: operator,
        Operator.Word: control or keyword,
        Punctuation: fg,
        Name: fg,
        Name.Attribute: attribute,
        Name.Builtin: builtin,
        Name.Builtin.Pseudo: keyword,
        Name.Class: klass,
        Name.Constant: number,
        Name.Decorator: decorator or function,
        Name.Exception: klass,
        Name.Function: function,
        Name.Function.Magic: function,
        Name.Label: tag,
        Name.Namespace: klass,
        Name.Tag: tag,
        Name.Variable: variable,
        Name.Variable.Magic: builtin,
        String: string,
        String.Doc: comment + italic,
        String.Escape: escape or number,
        String.Interpol: keyword,
        String.Regex: escape or string,
        Number: number,
        Generic.Deleted: error,
        Generic.Emph: "italic",
        Generic.Error: error,
        Generic.Heading: "bold " + function,
        Generic.Inserted: string,
        Generic.Prompt: comment,
        Generic.Strong: "bold",
        Generic.Subheading: "bold " + keyword,
    }


class GithubLightStyle(Style):
    name = "github-light"
    background_color = "#ffffff"
    highlight_color = "#fff8c5"
    line_number_color = "#8c959f"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#1f2328",
        comment="#6e7781",
        comment_italic=False,
        keyword="#cf222e",
        string="#0a3069",
        number="#0550ae",
        function="#8250df",
        klass="#953800",
        builtin="#0550ae",
        operator="#cf222e",
        tag="#116329",
        attribute="#0550ae",
        variable="#953800",
        error="#82071e",
    )


class OneLightStyle(Style):
    name = "one-light"
    background_color = "#fafafa"
    highlight_color = "#e5e5e6"
    line_number_color = "#9d9d9f"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#383a42",
        comment="#a0a1a7",
        keyword="#a626a4",
        string="#50a14f",
        number="#986801",
        function="#4078f2",
        klass="#c18401",
        builtin="#0184bc",
        operator="#0184bc",
        tag="#e45649",
        attribute="#986801",
        variable="#e45649",
        error="#ca1243",
    )


class VSCodeDarkStyle(Style):
    name = "vscode-dark"
    background_color = "#1e1e1e"
    highlight_color = "#264f78"
    line_number_color = "#858585"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#d4d4d4",
        comment="#6a9955",
        comment_italic=False,
        keyword="#569cd6",
        control="#c586c0",
        string="#ce9178",
        number="#b5cea8",
        function="#dcdcaa",
        klass="#4ec9b0",
        builtin="#4ec9b0",
        operator="#d4d4d4",
        tag="#569cd6",
        attribute="#9cdcfe",
        variable="#9cdcfe",
        escape="#d7ba7d",
    )


class VSCodeLightStyle(Style):
    name = "vscode-light"
    background_color = "#ffffff"
    highlight_color = "#add6ff"
    line_number_color = "#237893"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#000000",
        comment="#008000",
        comment_italic=False,
        keyword="#0000ff",
        control="#af00db",
        string="#a31515",
        number="#098658",
        function="#795e26",
        klass="#267f99",
        builtin="#267f99",
        operator="#000000",
        tag="#800000",
        attribute="#e50000",
        variable="#001080",
        escape="#ee0000",
        error="#cd3131",
    )


class TokyoNightStyle(Style):
    name = "tokyo-night"
    background_color = "#1a1b26"
    highlight_color = "#283457"
    line_number_color = "#3b4261"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#c0caf5",
        comment="#565f89",
        keyword="#bb9af7",
        control="#9d7cd8",
        string="#9ece6a",
        number="#ff9e64",
        function="#7aa2f7",
        klass="#2ac3de",
        builtin="#2ac3de",
        operator="#89ddff",
        tag="#f7768e",
        attribute="#73daca",
        decorator="#e0af68",
        escape="#b4f9f8",
        error="#db4b4b",
    )


class CatppuccinMochaStyle(Style):
    name = "catppuccin-mocha"
    background_color = "#1e1e2e"
    highlight_color = "#313244"
    line_number_color = "#6c7086"
    line_number_background_color = "transparent"
    styles = _palette(
        fg="#cdd6f4",
        comment="#9399b2",
        keyword="#cba6f7",
        string="#a6e3a1",
        number="#fab387",
        function="#89b4fa",
        klass="#f9e2af",
        builtin="#f38ba8",
        operator="#89dceb",
        tag="#cba6f7",
        attribute="#f9e2af",
        decorator="#fab387",
        escape="#f5c2e7",
        error="#f38ba8",
    )


CUSTOM_STYLES: dict[str, type[Style]] = {
    s.name: s
    for s in (
        GithubLightStyle,
        OneLightStyle,
        VSCodeDarkStyle,
        VSCodeLightStyle,
        TokyoNightStyle,
        CatppuccinMochaStyle,
    )
}


@dc.dataclass(frozen=True)
class Theme:
    key: str  # what we store in the config
    label: str  # what we show to the user


# Curated list shown first in the selectors (key, label)
FEATURED = [
    Theme("monokai", "Monokai"),
    Theme("github-dark", "GitHub Dark"),
    Theme("github-light", "GitHub Light"),
    Theme("one-dark", "One Dark"),
    Theme("one-light", "One Light"),
    Theme("vscode-dark", "VS Code Dark+"),
    Theme("vscode-light", "VS Code Light+"),
    Theme("dracula", "Dracula"),
    Theme("tokyo-night", "Tokyo Night"),
    Theme("catppuccin-mocha", "Catppuccin Mocha"),
    Theme("nord", "Nord"),
    Theme("gruvbox-dark", "Gruvbox Dark"),
    Theme("gruvbox-light", "Gruvbox Light"),
    Theme("solarized-dark", "Solarized Dark"),
    Theme("solarized-light", "Solarized Light"),
    Theme("material", "Material"),
    Theme("night-owl", "Night Owl"),
    Theme("zenburn", "Zenburn"),
    Theme("xcode", "Xcode"),
    Theme("vs", "Visual Studio (clássico)"),
    Theme("default", "Pygments Default"),
]

DEFAULT_THEME = "monokai"


def all_themes() -> list[Theme]:
    """Featured themes first, then every other pygments style"""
    builtin = set(get_all_styles())
    featured = [t for t in FEATURED if t.key in CUSTOM_STYLES or t.key in builtin]
    seen = {t.key for t in featured}
    others = [
        Theme(name, name.replace("_", " ").replace("-", " ").title())
        for name in sorted(builtin)
        if name not in seen
    ]
    return featured + others


def theme_label(key: str) -> str:
    for theme in all_themes():
        if theme.key == key:
            return theme.label
    return key


def get_style(key: str) -> type[Style]:
    """Resolve a theme key into a pygments Style class

    Raises pygments.util.ClassNotFound if the theme does not exist.
    """
    if key in CUSTOM_STYLES:
        return CUSTOM_STYLES[key]
    return get_style_by_name(key)


def is_valid(key: str) -> bool:
    try:
        get_style(key)
    except ClassNotFound:
        return False
    return True


def with_dimmed_linenos(style: type[Style]) -> type[Style]:
    """Most pygments styles let line numbers inherit the text color:
    use the comment color instead, as code editors do"""
    if style.line_number_color not in (None, "", "inherit"):
        return style
    comment = style.style_for_token(Comment).get("color")
    if not comment:
        return style
    return type(style.__name__, (style,), {"line_number_color": f"#{comment}"})


def base_colors(style: type[Style]) -> tuple[str, str]:
    """(background, foreground) of a style, as css colors"""
    background = style.background_color or "#ffffff"
    fg = style.style_for_token(Token.Text).get("color") or style.style_for_token(
        Token
    ).get("color")
    if not fg:
        fg = "000000" if _is_light(background) else "ffffff"
    return background, f"#{fg}"


def _is_light(color: str) -> bool:
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    try:
        r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return True
    return (0.299 * r + 0.587 * g + 0.114 * b) > 140
