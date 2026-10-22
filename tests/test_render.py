"""Rendering tests, run without Anki:  python -m pytest tests"""

import os
import re
import sys

os.environ["STANDALONE_ADDON"] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest  # noqa: E402

from syntax_highlighting_ng import STANDALONE, html_render, themes  # noqa: E402

CODE = 'def f(x):\n    return {"a": x}  # {{c1::cloze}}\n'


def test_standalone():
    assert STANDALONE


def test_uses_shipped_pygments():
    # pytest imports its own pygments, so check in a clean interpreter
    import subprocess

    code = (
        "import os,sys; os.environ['STANDALONE_ADDON']='1'; sys.path.insert(0, %r);"
        "import syntax_highlighting_ng, pygments; print(pygments.__version__, pygments.__file__)"
    ) % os.path.join(os.path.dirname(__file__), "..", "src")
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.startswith("2.21.0") and ".whl" in out.stdout


@pytest.mark.parametrize("theme", [t.key for t in themes.all_themes()])
def test_every_theme_renders(theme):
    out = html_render.render_block(CODE, html_render.Style(style=theme))
    assert out.startswith("<table><tbody><tr><td>")
    # inline background and foreground on the block
    bg, fg = themes.base_colors(themes.get_style(theme))
    assert f"background: {bg}" in out
    assert f"color: {fg}" in out
    assert re.fullmatch(r"#[0-9a-fA-F]{3,8}", fg)


def test_featured_themes_available():
    keys = {t.key for t in themes.all_themes()}
    for k in ("monokai", "github-dark", "github-light", "one-dark", "one-light",
              "dracula", "tokyo-night", "catppuccin-mocha", "vscode-dark"):
        assert k in keys


def test_custom_theme_colors():
    out = html_render.render_string("def f(): pass", html_render.Style(style="one-dark"))
    assert "#C678DD" in out.upper()  # one-dark keyword
    out = html_render.render_string("def f(): pass", html_render.Style(style="github-light"))
    assert "#CF222E" in out.upper()  # github keyword


def test_anki_template_escaping():
    out = html_render.render_block(CODE, html_render.Style())
    assert "{{" not in out and "}}" not in out
    assert "{<!---->{" in out


def test_linenos_toggle():
    on = html_render.render_string("a\nb\n", html_render.Style(linenos=True))
    off = html_render.render_string("a\nb\n", html_render.Style(linenos=False))
    assert ">2</span>" in on and ">2</span>" not in off
    # line numbers are dimmed (comment color) rather than inheriting the text color
    assert "color: inherit" not in on


def test_center():
    out = html_render.render_block("x", html_render.Style(center=True))
    assert out.startswith('<table style="margin-left: auto; margin-right: auto;">')


def test_css_classes_mode():
    out = html_render.render_string("x = 1", html_render.Style(style="dracula", noclasses=False))
    assert 'class="highlight sh-dracula"' in out
    assert "style=\"color" not in out
    css = html_render.theme_css("dracula")
    assert ".sh-dracula" in css and "background" in css


def test_errors():
    with pytest.raises(html_render.LanguageNotFound):
        html_render.render_string("x", html_render.Style(language="nope-lang"))
    with pytest.raises(html_render.InvalidStyle):
        html_render.render_string("x", html_render.Style(style="nope-theme"))
    assert "nope" in html_render.InvalidStyle("nope").render()


def test_languages_map():
    langs = html_render.languages()
    assert langs["Python"] == "python"
    assert "JavaScript" in langs and "Java" in langs
