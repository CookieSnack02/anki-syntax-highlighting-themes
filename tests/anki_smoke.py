"""Smoke test of the add-on against an installed Anki (legacy and new editor).

    python -I tests/anki_smoke.py [ANKI_APP_PACKAGES]

Default: the Anki 26.x installed by the official Windows installer
(%LOCALAPPDATA%/Programs/Anki/app_packages). Needs a Python with the same
minor version as Anki's (3.13), because Anki ships only bytecode.
"""
import json, logging, os, site, sys

A = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Anki", "app_packages")
site.addsitedir(A)
sys.path.insert(0, A)
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.insert(0, SRC)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import aqt
from aqt.qt import QApplication, QMainWindow, QMenu, QWebEngineView, PYQT_VERSION_STR
import aqt.webview, aqt.editor  # webengine must be imported before QApplication

print("aqt", aqt.appVersion, "PyQt", PYQT_VERSION_STR, "from", os.path.dirname(aqt.__file__))
app = QApplication([])


class FakeCol:
    def __init__(self):
        self.store = {}

    def get_config(self, k, default=None):
        return json.loads(json.dumps(self.store.get(k, default)))

    def set_config(self, k, v, *, undoable=False):
        self.store[k] = json.loads(json.dumps(v))

    class decks:
        @staticmethod
        def current():
            return {"name": "Programação"}


class FakeAM:
    def get_logger(self, m):
        return logging.getLogger(m)

    def getConfig(self, m):
        return json.load(open(os.path.join(SRC, "syntax_highlighting_ng", "config.json")))

    def setConfigAction(self, m, fn):
        self.action = fn


class Form:
    pass


mw = QMainWindow()
mw.form = Form()
mw.form.menuTools = QMenu()
mw.addonManager = FakeAM()
mw.col = FakeCol()
mw.app = app
aqt.mw = mw
import aqt.utils

TOOLTIPS = []
aqt.utils.tooltip = lambda msg, *a, **k: TOOLTIPS.append(msg)

import syntax_highlighting_ng
import syntax_highlighting_ng.main as main
import syntax_highlighting_ng.options as options
from syntax_highlighting_ng import config

main.tooltip = options.tooltip = aqt.utils.tooltip
from aqt import gui_hooks

assert aqt.editor.Editor in main.EDITOR_TYPES
assert getattr(aqt.editor, "NewEditor", None) in (None, *main.EDITOR_TYPES)
assert main.on_editor_buttons in gui_hooks.editor_did_init_buttons._hooks
assert main.on_editor_init in gui_hooks.editor_did_init._hooks
assert main.on_js_message in gui_hooks.webview_did_receive_js_message._hooks
assert [a.text() for a in mw.form.menuTools.actions()] == ["Syntax Highlighting (temas)..."]
assert mw.addonManager.action is main.on_options


class FakeWeb:
    """Records eval()s; evalWithCallback answers with the next editor.js state"""

    def __init__(self):
        self.js, self.state = [], {"ok": False}

    def eval(self, js):
        self.js.append(js)

    def evalWithCallback(self, js, cb):
        assert "__sh.prepare()" in js, js
        cb(self.state)


def make(cls):
    ed = cls.__new__(cls)  # real class, no Qt widgets
    ed.web = FakeWeb()
    ed.parentWindow = mw
    ed.currentField = None
    ed.last_field_index = None
    ed.addButton = lambda icon, cmd, func, tip="", keys=None: f"<button data-command='{cmd}'>"
    return ed


def last_call(ed, fn):
    """the argument of the last __sh.<fn>(...) eval"""
    calls = [js for js in ed.web.js if js.startswith(f"__sh.{fn}(")]
    assert calls, (fn, ed.web.js)
    return json.loads(calls[-1][len(f"__sh.{fn}("):-2])


for cls in main.EDITOR_TYPES:
    name = cls.__name__
    mw.col.store.clear()
    ed = make(cls)

    buttons = []
    gui_hooks.editor_did_init_buttons(buttons, ed)
    gui_hooks.editor_did_init(ed)
    assert len(buttons) == 3, buttons
    assert not any("onchange" in b or "onclick" in b for b in buttons), "inline handlers are blocked by the CSP"
    assert 'data-sh-cmd="shLang"' in buttons[1] and 'data-sh-cmd="shTheme"' in buttons[2]
    assert 'value="monokai" selected' in buttons[2]
    assert ed.web.js[-1] == main.EDITOR_JS and "window.__sh" in main.EDITOR_JS

    # toolbar selects -> python, through the real hook the webview fires
    assert gui_hooks.webview_did_receive_js_message((False, None), "shTheme:dracula", ed) == (True, None)
    assert gui_hooks.webview_did_receive_js_message((False, None), "shLang:Java", ed) == (True, None)
    assert config.get_synced()["style"] == "dracula" and ed._sh_lang == "Java"
    assert config.get_synced()["deckdefaultlang"] == {"Programação": "Java"}
    assert gui_hooks.webview_did_receive_js_message((False, None), "other", ed) == (False, None)
    assert gui_hooks.webview_did_receive_js_message((False, None), "shTheme:dracula", object()) == (False, None)
    gui_hooks.webview_did_receive_js_message((False, None), "shLang:Python", ed)

    # no field to go back to -> hint, nothing inserted
    ed.web.js.clear()
    ed.web.state = {"ok": False}
    main.highlight_code(ed)
    assert TOOLTIPS[-1].startswith("Clique em um campo") and not ed.web.js

    # selected text -> new block, through __sh.insert (pasteHTML, undoable)
    ed.web.state = {"ok": True, "selected": "for i in range(3):\n    print(i)\n", "blocks": []}
    main.highlight_code(ed)
    html = last_call(ed, "insert")
    assert "#282a36" in html.lower() and 'data-sh-theme="dracula"' in html and html.endswith("<br>")
    assert ">for</span>" in html and 'class="sh-ln"' in html

    # caret on an existing block -> replaced with the current theme, not nested
    block = {"code": "x = 1\n", "lang": "python", "theme": "monokai"}
    ed.web.state = {"ok": True, "selected": "", "blocks": [block, dict(block, lang=None, theme=None)]}
    main.highlight_code(ed)
    htmls = last_call(ed, "replace")
    assert len(htmls) == 2 and all('data-sh-theme="dracula"' in h and not h.endswith("<br>") for h in htmls)
    assert all(h.count("<table") == 1 for h in htmls)

    # theme picked with the caret on a block -> that block gets the new theme
    gui_hooks.webview_did_receive_js_message((False, None), "shTheme:one-dark", ed)
    htmls = last_call(ed, "replace")
    assert all('data-sh-theme="one-dark"' in h for h in htmls) and 'data-sh-lang="python"' in htmls[0]

    # language picked with the caret on a block -> new language, block keeps its theme
    ed.web.state = {"ok": True, "selected": "", "blocks": [block]}
    gui_hooks.webview_did_receive_js_message((False, None), "shLang:JavaScript", ed)
    [h] = last_call(ed, "replace")
    assert 'data-sh-lang="javascript"' in h and 'data-sh-theme="monokai"' in h
    print(f"{name}: OK")

# options dialog (QWebEngine can't render offscreen here: capture the html)
PREVIEW = []
QWebEngineView.setHtml = lambda self, h, *a: PREVIEW.append(h)
dlg = options.SyntaxHighlightingOptions(mw, languages=main.lang_selection())
assert dlg.theme_combo.findData("catppuccin-mocha") >= 0
dlg.theme_combo.setCurrentIndex(dlg.theme_combo.findData("tokyo-night"))
assert "#1a1b26" in PREVIEW[-1].lower()
dlg.copy_css()
assert QApplication.clipboard().text().startswith("/* Syntax Highlighting — Tokyo Night */")
dlg.accept()
assert config.get_synced()["style"] == "tokyo-night"
main.refresh_editors_theme("tokyo-night")
print("options dialog: OK")
print("SMOKE OK", aqt.appVersion)
