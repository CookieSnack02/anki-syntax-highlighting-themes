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
    assert out.stdout.startswith("2.21.0")
    pygments_file = out.stdout.split(" ", 1)[1].strip()
    assert os.path.join("syntax_highlighting_ng", "libs", "pygments") in pygments_file


def test_no_zip_imports_in_addon():
    # importing from a .whl/.zip keeps it open: on Windows Anki then cannot
    # delete the add-on folder to update it while running
    addon = os.path.join(os.path.dirname(__file__), "..", "src", "syntax_highlighting_ng")
    for folder, _, files in os.walk(addon):
        for name in files:
            assert not name.endswith((".whl", ".zip", ".egg")), os.path.join(folder, name)


@pytest.mark.parametrize("theme", [t.key for t in themes.all_themes()])
def test_every_theme_renders(theme):
    out = html_render.render_block(CODE, html_render.Style(style=theme))
    assert out.startswith(f'<table class="sh-block" data-sh-lang="python" data-sh-theme="{theme}">')
    assert out.endswith("</table><br>")
    # inline background and foreground on the block (pure white/black nudged)
    bg, fg = themes.base_colors(themes.get_style(theme))
    assert html_render._nudge_colors(f"background: {bg}; color: {fg}") in out
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
    assert out.startswith('<table class="sh-block" ')
    assert 'data-sh-theme="monokai" style="margin-left: auto; margin-right: auto;">' in out


def test_block_markup_for_rerendering():
    out = html_render.render_block("a\nb\n", html_render.Style(language="java", style="dracula"))
    assert 'data-sh-lang="java"' in out and 'data-sh-theme="dracula"' in out
    # inline line numbers are marked, so the code can be recovered from the field
    assert out.count('<span class="sh-ln" style=') == 2
    # replacing an existing block must not add another <br> each time
    assert not html_render.render_block("x", html_render.Style(), trailing_br=False).endswith("<br>")


def test_code_recoverable_without_line_numbers():
    out = html_render.render_string("x = 1\ny = 2\n", html_render.Style())
    without_ln = re.sub(r'<span class="sh-ln"[^>]*>[^<]*</span>', "", out)
    text = re.sub(r"<[^>]+>", "", without_ln)
    assert text.strip() == "x = 1\ny = 2"


def test_pure_white_and_black_are_nudged_in_styles_only():
    # insertHTML would drop colors equal to the editor defaults
    out = html_render.render_block('c = "#fff #000000"\n', html_render.Style(style="vscode-light"))
    styles = " ".join(re.findall(r'style="([^"]*)"', out))
    assert not re.search(r"#(ffffff|fff|000000|000)\b", styles, re.I)
    assert "background: #fefefe" in out and "color: #010101" in out
    # the code itself is untouched
    assert "#fff #000000" in out


def test_nudge_does_not_touch_other_colors():
    assert html_render._nudge_colors("color: #fff8c5; background: #0000ff") == "color: #fff8c5; background: #0000ff"
    assert html_render._nudge_colors("color: #FFF; background: #000") == "color: #fefefe; background: #010101"


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
