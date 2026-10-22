"""Test-only add-on: opens Add Cards, exposes a few bridge commands, logs."""
import json, os

from aqt import dialogs, gui_hooks, mw
from aqt.qt import QApplication, QTimer

MODE = os.environ.get("SH_E2E_MODE", "legacy")
LOG = open(os.environ["SH_E2E_LOG"], "a", encoding="utf-8")


def log(line):
    LOG.write(line + "\n")
    LOG.flush()


def open_add():
    if MODE == "new":
        dialogs.open("NewAddCards", mw).load_new_note()
    else:
        dialogs.open("AddCards", mw)


def on_msg(handled, msg, ctx):
    if msg.startswith("e2e:clip:"):
        QApplication.clipboard().setText(json.loads(msg[len("e2e:clip:"):]))
        return True, "ok"
    if msg.startswith("e2e:reinstall:"):
        # what "Install from file" does, with the add-on loaded (Windows locks)
        path = json.loads(msg[len("e2e:reinstall:"):])
        try:
            result = mw.addonManager.install(path)
        except Exception as e:  # noqa: BLE001
            return True, json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})
        return True, json.dumps({"ok": True, "result": type(result).__name__,
                                 "detail": str(getattr(result, "errmsg", "") or getattr(result, "name", ""))})
    if msg == "e2e:activate":
        # synthetic key events are dropped while the window is not active
        win = ctx.parentWindow
        win.raise_()
        win.activateWindow()
        ctx.web.setFocus()
        return True, "ok"
    if msg == "e2e:editor":
        return True, json.dumps(dict(cls=type(ctx).__name__, current=getattr(ctx, "currentField", "?"),
                                     last=getattr(ctx, "last_field_index", "?")))
    if not msg.startswith("key:"):
        log(f"JS->PY {type(ctx).__name__} {msg[:70]!r}")
    return handled


def wrap_addon():
    import syntax_highlighting_ng.main as m

    for name in ("_highlight_code", "rerender_blocks", "on_theme_select", "on_lang_select"):
        orig = getattr(m, name)

        def wrapper(*a, _orig=orig, _name=name, **k):
            log(f"PY {_name} {[str(x)[:90] for x in a[1:]]}")
            return _orig(*a, **k)

        setattr(m, name, wrapper)
    QTimer.singleShot(1500, open_add)


gui_hooks.profile_did_open.append(wrap_addon)
gui_hooks.webview_did_receive_js_message.append(on_msg)
