# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Main Module, hooks add-on methods into Anki.

Copyright: (c) 2012-2015 Tiago Barroso <https://github.com/tmbb>
           (c) 2015 Tim Rae <https://github.com/timrae>
           (c) 2018-2023 Glutanimate <https://glutanimate.com/>
           (c) 2023- A. Cavallo <https://github.com/cav71>

License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import annotations

import functools
import html
import json
import traceback
import weakref
from typing import Any, Callable

import pygments
from aqt import gui_hooks, mw
from aqt.editor import Editor
from aqt.qt import QAction, QApplication
from aqt.utils import showWarning, tooltip

from . import config, html_render, themes
from .consts import EDITOR_JS_PATH, ICON_PATH

# Anki 26.x ships two editors: the legacy one (aqt.editor.Editor, still the
# default) and the new SvelteKit one (aqt.editor.NewEditor, behind the
# SVELTE_EDITOR experiment or Shift+click). Both must be supported.
try:
    from aqt.editor import NewEditor
except ImportError:  # Anki < 26
    EDITOR_TYPES: tuple[type, ...] = (Editor,)
else:
    EDITOR_TYPES = (Editor, NewEditor)

log = mw.addonManager.get_logger(__name__)
log.info(
    "addon syntax_highlighting_ng loaded pygments %s",
    getattr(pygments, "__version__", "N/A"),
)

# Language display name -> pygments alias
LANGUAGES_MAP = html_render.languages()

# Open editors, so a theme change can be reflected in their toolbars
_editors: "weakref.WeakSet[Editor]" = weakref.WeakSet()


# Misc


def show_error(msg: str, parent: Any) -> None:
    showWarning(msg, title="Syntax Highlighting", parent=parent, textFormat="rich")


def ui_code(fn: Callable) -> Callable:
    """Show rendering errors to the user instead of raising them"""

    @functools.wraps(fn)
    def _fn(ed: Editor, *args: Any, **kwargs: Any) -> Any:
        try:
            return fn(ed, *args, **kwargs)
        except html_render.RenderError as e:
            log.warning("".join(traceback.format_exc()))
            show_error(e.render(), parent=ed.parentWindow)
        return False

    return _fn


def lang_selection() -> list[str]:
    limited = config.get_local().get("limitToLangs") or []
    return list(limited) or sorted(LANGUAGES_MAP.keys(), key=str.lower)


# Default language (synced, optionally per deck)


def get_deck_name() -> str | None:
    try:
        return mw.col.decks.current()["name"]
    except AttributeError:
        # no collection opened
        return None


def get_default_lang() -> str:
    conf = config.get_synced()
    lang = conf["lang"]
    if conf["defaultlangperdeck"]:
        deck_name = get_deck_name()
        if deck_name and deck_name in conf["deckdefaultlang"]:
            lang = conf["deckdefaultlang"][deck_name]
    return lang


def set_default_lang(lang: str) -> None:
    conf = config.get_synced()
    conf["lang"] = lang  # always update the overall default
    if conf["defaultlangperdeck"]:
        deck_name = get_deck_name()
        if deck_name:
            conf["deckdefaultlang"][deck_name] = lang
    config.set_synced(conf)


# Editor toolbar


def _select(elm_id: str, cmd: str, tip: str, options: list[tuple[str, str]], current: str) -> str:
    opts = "".join(
        '<option value="{v}"{s}>{l}</option>'.format(
            v=html.escape(value, quote=True),
            l=html.escape(label),
            s=" selected" if value == current else "",
        )
        for value, label in options
    )
    # no inline onchange: the editor's Content-Security-Policy blocks inline
    # handlers, the change events are caught by editor.js instead
    return (
        f'<select id="{elm_id}" data-sh-cmd="{cmd}" '
        f'title="{html.escape(tip, quote=True)}" '
        'style="vertical-align: middle; max-width: 11em; margin: 0 2px; '
        'font-size: 0.85em;">'
        f"{opts}</select>"
    )


# Editor-side helper (window.__sh), see editor.js. It is run through web.eval,
# which is not subject to the page CSP.
with open(EDITOR_JS_PATH, encoding="utf-8") as _f:
    EDITOR_JS = _f.read()


def on_editor_init(ed: Editor) -> None:
    ed.web.eval(EDITOR_JS)


def on_editor_buttons(buttons: list[str], ed: Editor) -> None:
    local = config.get_local()
    hotkey = local.get("hotkey") or "Alt+S"

    ed._sh_lang = get_default_lang()  # type: ignore[attr-defined]
    _editors.add(ed)

    buttons.append(
        ed.addButton(
            ICON_PATH,
            "syntaxHighlightNg",
            highlight_code,
            tip=f"Inserir código destacado ({hotkey})",
            keys=hotkey,
        )
    )

    langs = lang_selection()
    if ed._sh_lang not in langs:  # type: ignore[attr-defined]
        langs = [ed._sh_lang] + langs  # type: ignore[attr-defined]
    buttons.append(
        _select(
            "sh-lang-select",
            "shLang",
            "Linguagem do código",
            [(lang, lang) for lang in langs],
            ed._sh_lang,  # type: ignore[attr-defined]
        )
    )

    if local.get("showThemeSelector", True):
        buttons.append(
            _select(
                "sh-theme-select",
                "shTheme",
                "Tema do destaque",
                [(t.key, t.label) for t in themes.all_themes()],
                config.get_synced()["style"],
            )
        )


def refresh_editors_theme(theme_key: str) -> None:
    """Reflect a theme change in the toolbar of every open editor"""
    js = (
        "(function(){var s=document.getElementById('sh-theme-select');"
        f"if(s){{s.value={json.dumps(theme_key)};}}}})();"
    )
    for ed in list(_editors):
        try:
            ed.web.eval(js)
        except RuntimeError:
            # underlying Qt object already deleted
            pass


# Editor state: the JS side (editor.js) gives the focus back to the last field
# and reports the highlighted blocks under the caret/selection.


def with_editor_state(ed: Editor, callback: Callable[[dict], None]) -> None:
    def on_state(state: Any) -> None:
        try:
            callback(state if isinstance(state, dict) else {"ok": False})
        except html_render.RenderError as e:
            log.warning("".join(traceback.format_exc()))
            show_error(e.render(), parent=ed.parentWindow)

    ed.web.evalWithCallback("window.__sh ? __sh.prepare() : {ok: false}", on_state)


def current_alias(ed: Editor) -> str:
    lang = getattr(ed, "_sh_lang", None) or config.get_synced()["lang"]
    alias = LANGUAGES_MAP.get(lang)
    if not alias:
        raise html_render.LanguageNotFound(lang)
    return alias


def make_style(conf: dict, language: str, theme: str) -> html_render.Style:
    return html_render.Style(
        language=language,
        style=theme,
        linenos=bool(conf["linenos"]),
        # css classes take less space and are customizable, but require the
        # theme css (see the options dialog) in every note type using code
        noclasses=not conf["cssclasses"],
        center=bool(conf["centerfragments"]),
    )


def rerender_blocks(
    ed: Editor, blocks: list[dict], theme: str | None = None, language: str | None = None
) -> None:
    """Replace existing blocks (instead of nesting a new one inside them).

    theme/language: the new value; when None, each block keeps its own.
    """
    conf = config.get_synced()
    htmls: list[str | None] = []
    for block in blocks:
        code = (block.get("code") or "").replace(chr(0xA0), " ")
        if not code.strip():
            htmls.append(None)
            continue
        style = make_style(
            conf,
            language=language or block.get("lang") or current_alias(ed),
            theme=theme or block.get("theme") or conf["style"],
        )
        htmls.append(html_render.render_block(code, style, trailing_br=False))
    ed.web.eval(f"__sh.replace({json.dumps(htmls)});")


@ui_code
def on_lang_select(ed: Editor, lang: str) -> None:
    if lang not in LANGUAGES_MAP:
        raise html_render.LanguageNotFound(lang)
    ed._sh_lang = lang  # type: ignore[attr-defined]
    set_default_lang(lang)

    def on_state(state: dict) -> None:
        if state.get("ok") and state.get("blocks"):
            rerender_blocks(ed, state["blocks"], language=LANGUAGES_MAP[lang])

    with_editor_state(ed, on_state)


@ui_code
def on_theme_select(ed: Editor, theme_key: str) -> None:
    if not themes.is_valid(theme_key):
        raise html_render.InvalidStyle(theme_key)
    config.update_synced(style=theme_key)
    label = themes.theme_label(theme_key)

    def on_state(state: dict) -> None:
        if state.get("ok") and state.get("blocks"):
            rerender_blocks(ed, state["blocks"], theme=theme_key)
            tooltip(f"Tema {label} aplicado ao bloco", parent=ed.parentWindow)
        else:
            tooltip(f"Tema: {label}", parent=ed.parentWindow)

    with_editor_state(ed, on_state)


def on_js_message(handled: tuple[bool, Any], message: str, context: Any) -> tuple[bool, Any]:
    if not isinstance(context, EDITOR_TYPES):
        return handled
    cmd, _, arg = message.partition(":")
    if cmd == "shLang":
        on_lang_select(context, arg)
        return True, None
    if cmd == "shTheme":
        on_theme_select(context, arg)
        return True, None
    return handled


# Actual code highlighting


def highlight_code(ed: Editor) -> None:
    with_editor_state(ed, functools.partial(_highlight_code, ed))


def _highlight_code(ed: Editor, state: dict) -> None:
    if not state.get("ok"):
        tooltip("Clique em um campo antes de inserir o código.", parent=ed.parentWindow)
        return

    conf = config.get_synced()

    # The caret/selection is on existing blocks: apply the current theme to
    # them, instead of highlighting the highlighted html again
    if state.get("blocks"):
        rerender_blocks(ed, state["blocks"], theme=conf["style"])
        return

    # Selected text first, clipboard otherwise. The selection may contain
    # non-breaking spaces (U+00A0) which confuse the formatter.
    code = state.get("selected") or QApplication.clipboard().text()
    code = code.replace(chr(0xA0), " ")
    if not code.strip():
        tooltip(
            "Nada para destacar: selecione o código ou copie-o para a área de transferência.",
            parent=ed.parentWindow,
        )
        return

    style = make_style(conf, language=current_alias(ed), theme=conf["style"])
    pretty_code = html_render.render_block(code, style)
    # pasteHTML(html, internal=true): the editor keeps the inline colors, and
    # it goes through execCommand, so Ctrl+Z removes the block again. Both the
    # legacy editor and the NewEditor of Anki 26 expose it.
    ed.web.eval(f"__sh.insert({json.dumps(pretty_code)});")


# Options


def on_options() -> None:
    if mw.col is None:
        showWarning("Abra um perfil antes de configurar o add-on.")
        return
    from .options import SyntaxHighlightingOptions

    dialog = SyntaxHighlightingOptions(mw, languages=lang_selection())
    if dialog.exec():
        refresh_editors_theme(config.get_synced()["style"])


def setup_menu() -> None:
    action = QAction("Syntax Highlighting (temas)...", mw)
    action.triggered.connect(on_options)
    mw.form.menuTools.addAction(action)
    # the "Config" button of the add-ons manager opens our dialog too
    mw.addonManager.setConfigAction(__name__, on_options)


# Hooks

setup_menu()
gui_hooks.editor_did_init_buttons.append(on_editor_buttons)
gui_hooks.editor_did_init.append(on_editor_init)
gui_hooks.webview_did_receive_js_message.append(on_js_message)
