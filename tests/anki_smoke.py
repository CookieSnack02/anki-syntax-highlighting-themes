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
    def __init__(self, sel=""):
        self.js, self.sel = [], sel

    def selectedText(self):
        return self.sel

    def eval(self, js):
        self.js.append(js)


def make(cls, sel):
    ed = cls.__new__(cls)  # real class, no Qt widgets
    ed.web = FakeWeb(sel)
    ed.parentWindow = mw
    ed.currentField = None
    ed.last_field_index = None
    ed.addButton = lambda icon, cmd, func, tip="", keys=None: f"<button data-command='{cmd}'>"
    return ed


for cls in main.EDITOR_TYPES:
    name = cls.__name__
    mw.col.store.clear()
    ed = make(cls, "for i in range(3):\n    print(i)\n")
    pasted = []
    if hasattr(cls, "doPaste"):
        ed.doPaste = lambda h, internal, extended=False: pasted.append((h, internal))

    buttons = []
    gui_hooks.editor_did_init_buttons(buttons, ed)
    gui_hooks.editor_did_init(ed)
    assert len(buttons) == 3, buttons
    assert not any("onchange" in b or "onclick" in b for b in buttons), "inline handlers are blocked by the CSP"
    assert 'data-sh-cmd="shLang"' in buttons[1] and 'data-sh-cmd="shTheme"' in buttons[2]
    assert 'value="monokai" selected' in buttons[2]
    assert any("data-sh-cmd" in js and "pycmd" in js for js in ed.web.js)

    # toolbar selects -> python, through the real hook the webview fires
    assert gui_hooks.webview_did_receive_js_message((False, None), "shTheme:dracula", ed) == (True, None)
    assert gui_hooks.webview_did_receive_js_message((False, None), "shLang:Java", ed) == (True, None)
    assert config.get_synced()["style"] == "dracula" and ed._sh_lang == "Java"
    assert config.get_synced()["deckdefaultlang"] == {"Programação": "Java"}
    assert gui_hooks.webview_did_receive_js_message((False, None), "other", ed) == (False, None)
    assert gui_hooks.webview_did_receive_js_message((False, None), "shTheme:dracula", object()) == (False, None)

    # no field ever focused -> hint, nothing inserted
    main.highlight_code(ed)
    assert TOOLTIPS[-1].startswith("Clique em um campo") and not pasted

    # field 1 was focused, then the user clicked the <select> (blur)
    ed.last_field_index, ed.currentField = 1, None
    ed.web.js.clear()
    main.highlight_code(ed)
    assert ed.web.js[0] == "focusField(1);", ed.web.js
    if hasattr(cls, "doPaste"):
        html, internal = pasted[-1]
        assert internal is True
    else:
        assert ed.web.js[1].startswith("pasteHTML(") and ed.web.js[1].endswith(", true, false);")
        html = json.loads(ed.web.js[1][len("pasteHTML("):-len(", true, false);")])
    assert "#282a36" in html.lower(), "dracula background"  # theme picked in the toolbar
    assert ">for</span>" in html and "<table><tbody><tr><td>" in html

    # field still focused -> no refocus
    ed.currentField = 1
    ed.web.js.clear()
    main.highlight_code(ed)
    assert not any(js.startswith("focusField") for js in ed.web.js)
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
