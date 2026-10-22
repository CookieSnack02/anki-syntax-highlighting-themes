"""Tiny Chrome DevTools Protocol client for QtWebEngine pages."""
import itertools, json, os, sys, time, urllib.request

try:
    import websocket
except ImportError:  # pragma: no cover
    sys.exit("missing dependency: python -m pip install websocket-client")

PORT = 9333


def targets():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=3) as r:
        return json.load(r)


def wait_target(pred, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            for t in targets():
                if t.get("type") == "page" and pred(t):
                    return t
        except OSError:
            pass
        time.sleep(0.5)
    raise TimeoutError("target not found")


class Page:
    def __init__(self, target):
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=30)
        self.ids = itertools.count(1)

    def call(self, method, **params):
        i = next(self.ids)
        self.ws.send(json.dumps({"id": i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == i:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result")

    def js(self, expr, await_promise=True):
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=await_promise,
                      returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(r["exceptionDetails"].get("exception", {}).get("description") or r["exceptionDetails"])
        return r["result"].get("value")

    def pycmd(self, cmd):
        """call pycmd and wait for its callback value"""
        return self.js(f"new Promise(res => pycmd({json.dumps(cmd)}, res))")

    def key(self, key, code, vk, modifiers=0, text=None):
        # modifiers: 1=alt 2=ctrl 4=meta 8=shift
        base = dict(key=key, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=modifiers)
        self.call("Input.dispatchKeyEvent", type="rawKeyDown", **base)
        if text:
            self.call("Input.dispatchKeyEvent", type="char", text=text, **base)
        self.call("Input.dispatchKeyEvent", type="keyUp", **base)

    def type_text(self, text):
        self.call("Input.insertText", text=text)

    def ctrl_z(self):
        self.key("z", "KeyZ", 90, modifiers=2)


# JS helpers injected into the editor page
HELPERS = r"""
window.__e2e = {
  editables() {
    const out = [];
    const walk = (root) => {
      root.querySelectorAll('*').forEach(el => {
        if (el.isContentEditable && el.getAttribute('contenteditable') === 'true') out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot);
      });
    };
    walk(document);
    return out;
  },
  field(i) { return this.editables()[i]; },
  html(i) { const f = this.field(i); return f ? f.innerHTML : null; },
  deepActive() {
    let a = document.activeElement;
    while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
    return a;
  },
  caretInto(i, selector, atStart) {
    const f = this.field(i); const el = selector ? f.querySelector(selector) : f;
    f.focus();
    const root = f.getRootNode();
    const sel = root.getSelection ? root.getSelection() : document.getSelection();
    const r = document.createRange();
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    if (!atStart) { let n; while ((n = walker.nextNode())) node = n; }
    if (node) { r.setStart(node, atStart ? 0 : node.length); } else { r.selectNodeContents(el); r.collapse(atStart); }
    r.collapse(true);
    sel.removeAllRanges(); sel.addRange(r);
    return true;
  },
  selectAllIn(i) {
    const f = this.field(i); f.focus();
    const root = f.getRootNode();
    const sel = root.getSelection ? root.getSelection() : document.getSelection();
    const r = document.createRange(); r.selectNodeContents(f);
    sel.removeAllRanges(); sel.addRange(r); return sel.toString().length;
  },
  pickTheme(key) {
    const s = document.getElementById('sh-theme-select');
    s.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
    s.focus(); s.value = key;
    s.dispatchEvent(new Event('change', {bubbles: true}));
    return s.value;
  },
  pickLang(name) {
    const s = document.getElementById('sh-lang-select');
    s.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
    s.focus(); s.value = name;
    s.dispatchEvent(new Event('change', {bubbles: true}));
    return s.value;
  },
  clickCH() { document.querySelector('[data-command="syntaxHighlightNg"]').dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true}));
              document.querySelector('[data-command="syntaxHighlightNg"]').click(); return true; },
};
true
"""
