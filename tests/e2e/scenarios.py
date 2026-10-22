"""End-to-end scenarios, driven through DevTools against the Add Cards editor
of the isolated Anki started by run.py."""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp

p = cdp.Page(cdp.wait_target(lambda t: t.get("title") == "editor", 90))
deadline = time.time() + 30
while not p.js("!!window.__sh && document.getElementById('sh-theme-select') !== null"):
    if time.time() > deadline:
        raise SystemExit("editor not ready")
    time.sleep(0.3)
p.js(cdp.HELPERS)
p.pycmd("e2e:activate")
print("editor:", p.pycmd("e2e:editor"))
F = 1
FAILS = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def html():
    return p.js(f"__e2e.html({F})") or ""


def blocks(h=None):
    return (h or html()).count('class="highlight')


def bg(h=None):
    m = re.findall(r"background: (rgb\([^)]*\)|#[0-9a-fA-F]+)", h or html())
    return m


def settle(t=0.8):
    time.sleep(t)


def reset(text="antes "):
    for _ in range(5):
        p.pycmd("e2e:activate"); settle(0.2)
        p.js(f"__e2e.caretInto({F}, null, false)"); settle(0.2)
        p.key("a", "KeyA", 65, modifiers=2); p.key("Delete", "Delete", 46); settle(0.3)
        if blocks() == 0 and len(re.sub(r"<br>|&nbsp;|\s", "", html())) == 0:
            break
    else:
        raise SystemExit("could not clear the field (is the test window being covered?)")
    if text:
        p.type_text(text); settle(0.3)


def clip(code):
    p.pycmd("e2e:clip:" + json.dumps(code))


CODE = "def soma(a, b):\n    return a + b\n"
MONOKAI, DRACULA, ONEDARK = "rgb(39, 40, 34)", "rgb(40, 42, 54)", "rgb(40, 44, 52)"

# --- 1. insert from the clipboard, then Ctrl+Z removes it
p.js("__e2e.pickTheme('monokai')"); settle()
reset(); clip(CODE)
before = html()
p.js("__e2e.clickCH()"); settle()
h = html()
check("1 insert: one block", blocks(h) == 1, h[:200])
check("1 insert: block marked", 'class="sh-block"' in h and 'data-sh-lang="python"' in h, h[:200])
check("1 insert: line numbers marked", 'class="sh-ln"' in h)
check("1 insert: monokai", MONOKAI in bg(h), bg(h))
p.ctrl_z(); settle(0.6)
check("1 ctrl+z removes the block", blocks() == 0 and html() == before, repr(html()[:120]))

# --- 2. pick a theme in the toolbar (focus leaves the field), then CH, then Ctrl+Z
reset(); clip(CODE)
p.js("__e2e.pickTheme('dracula')"); settle()
before = html()  # the editor appends a <br> to the field when it loses the focus
check("2 select took the focus", p.js("(__e2e.deepActive()||{}).tagName") in ("ANKI-EDITABLE", "SELECT"))
p.js("__e2e.clickCH()"); settle()
h = html()
check("2 insert after toolbar select", blocks(h) == 1 and DRACULA in bg(h), (blocks(h), bg(h)))
check("2 text before kept", h.startswith("antes"), h[:40])
p.ctrl_z(); settle(0.6)
check("2 ctrl+z removes the block", blocks() == 0 and html() == before, repr(html()[:120]))

# --- 3. caret inside an existing block + theme change -> block replaced, not nested
reset(); clip(CODE)
p.js("__e2e.pickTheme('monokai')"); settle()
p.js("__e2e.clickCH()"); settle()
code_before = p.js(f"__e2e.field({F}).querySelector('pre').textContent")
p.js(f"__e2e.caretInto({F}, 'pre', true)"); settle(0.3)
p.js("__e2e.pickTheme('one-dark')"); settle()
h = html()
check("3 theme change replaces the block", blocks(h) == 1 and ONEDARK in bg(h) and MONOKAI not in bg(h), (blocks(h), bg(h)))
check("3 no nested tables", h.count("<table") == 1, h.count("<table"))
code_after = p.js(f"__e2e.field({F}).querySelector('pre').textContent")
check("3 same code and line numbers", code_after == code_before, (code_before, code_after))
check("3 no leaked line numbers", "11def" not in code_after.replace(" ", ""), code_after)
p.ctrl_z(); settle(0.6)
check("3 ctrl+z restores the previous theme", blocks() == 1 and MONOKAI in bg(), bg())

# --- 4. select everything (block included) + CH -> re-themed, not re-highlighted
p.js("__e2e.pickTheme('dracula')"); settle()   # caret still in block -> replaced again
p.js(f"__e2e.selectAllIn({F})"); settle(0.3)
p.js("__e2e.pickTheme('github-light')"); settle()
p.js(f"__e2e.selectAllIn({F})"); settle(0.3)
p.js("__e2e.clickCH()"); settle()
h = html()
check("4 select-all + CH keeps one block", blocks(h) == 1 and h.count("<table") == 1, (blocks(h), h.count("<table")))
check("4 code intact", p.js(f"__e2e.field({F}).querySelector('pre').textContent") == code_before)
check("4 github-light applied", "rgb(254, 254, 254)" in bg(h), bg(h))

# --- 5. language change with the caret in the block re-highlights with the new language
p.js(f"__e2e.caretInto({F}, 'pre', true)"); settle(0.3)
p.js("__e2e.pickLang('JavaScript')"); settle()
h = html()
check("5 language change replaces the block", blocks(h) == 1 and 'data-sh-lang="javascript"' in h, re.findall(r'data-sh-lang="[^"]*"', h))
p.js("__e2e.pickLang('Python')"); settle()

# --- 6. a block from add-on 1.1 (no data attributes) can be re-themed
old = ('<table><tbody><tr><td><div class="highlight" style="background: #272822; color: #f8f8f2;">'
       '<pre style="margin: 0;"><span></span><span style="color: inherit; background-color: transparent; '
       'padding-left: 5px; padding-right: 5px;">1</span><span style="color: #66D9EF">print</span>'
       '<span style="color: #F8F8F2">(</span><span style="color: #E6DB74">"oi"</span>'
       '<span style="color: #F8F8F2">)</span>\n</pre></div></td></tr></tbody></table>')
reset(""); p.js(f"pasteHTML({json.dumps(old)}, true, false)"); settle(0.5)
p.js(f"__e2e.caretInto({F}, 'pre', false)"); settle(0.3)
p.js("__e2e.pickTheme('dracula')"); settle()
h = html()
code = p.js(f"__e2e.field({F}).querySelector('pre').textContent")
check("6 legacy block re-themed in place", blocks(h) == 1 and DRACULA in bg(h) and h.count("<table") == 1, (blocks(h), bg(h)))
check("6 legacy line number not leaked", re.sub(r"\s", "", code) == '1print("oi")', code)

# --- 7. the field value saved by Anki has the block
p.js(f"__e2e.caretInto({F}, null, false)"); p.type_text(" fim"); settle(1.5)
# --- 8. installing the package over the loaded add-on (Windows file locks)
package = os.environ.get("SH_E2E_PACKAGE")
if package:
    for i in (1, 2):
        r = json.loads(p.pycmd("e2e:reinstall:" + json.dumps(package)))
        check(f"8 reinstall while running #{i}", r.get("ok") and r.get("result") == "InstallOk", r)

print("\nRESULT:", "ALL PASS" if not FAILS else f"{len(FAILS)} FAIL: {FAILS}")
sys.exit(1 if FAILS else 0)
