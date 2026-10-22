/*
 * This file is part of the Syntax Highlighting add-on for Anki.
 * License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
 *
 * Injected into the editor page (legacy and new editor) with web.eval, which
 * is not subject to the page Content-Security-Policy.
 *
 * - routes the toolbar <select> changes to python (inline handlers are
 *   blocked by the CSP);
 * - remembers the last focused field and its selection, so focus can be given
 *   back synchronously after the user clicked a toolbar <select>;
 * - finds the highlighted blocks under the caret/selection and replaces them
 *   (through pasteHTML -> execCommand, so Ctrl+Z works) instead of nesting.
 */
(function () {
    "use strict";
    if (window.__sh) {
        return;
    }

    var sh = (window.__sh = { el: null, pos: null, frozen: false, targets: [] });

    function deepActive() {
        var a = document.activeElement;
        while (a && a.shadowRoot && a.shadowRoot.activeElement) {
            a = a.shadowRoot.activeElement;
        }
        return a;
    }

    // the outermost contenteditable element (the field)
    function fieldOf(node) {
        var el = node && node.nodeType === 1 ? node : node && node.parentElement;
        if (!el || !el.isContentEditable) {
            return null;
        }
        while (el.parentElement && el.parentElement.isContentEditable) {
            el = el.parentElement;
        }
        return el;
    }

    function selectionOf(el) {
        var root = el.getRootNode();
        return root.getSelection ? root.getSelection() : document.getSelection();
    }

    /* The position is kept as child-index paths, not as a Range: a Range is
     * live, and when a field loses the focus the editor rewrites its html,
     * which collapses any Range to the start of the field. The rewritten html
     * is the same, so the paths stay valid. */
    function pathOf(el, node) {
        var path = [];
        while (node && node !== el) {
            var parent = node.parentNode;
            if (!parent) {
                return null;
            }
            path.unshift(Array.prototype.indexOf.call(parent.childNodes, node));
            node = parent;
        }
        return node === el ? path : null;
    }

    function nodeAt(el, path) {
        var node = el;
        for (var i = 0; i < path.length; i++) {
            node = node.childNodes[path[i]];
            if (!node) {
                return null;
            }
        }
        return node;
    }

    function clampOffset(node, offset) {
        var max = node.nodeType === 3 ? node.data.length : node.childNodes.length;
        return Math.min(offset, max);
    }

    function rangeFromPos(el, pos) {
        var start = nodeAt(el, pos.sp);
        var end = nodeAt(el, pos.ep);
        if (!start || !end) {
            return null;
        }
        var r = document.createRange();
        r.setStart(start, clampOffset(start, pos.so));
        r.setEnd(end, clampOffset(end, pos.eo));
        return r;
    }

    function remember(node) {
        if (sh.frozen) {
            return;
        }
        var el = fieldOf(node || deepActive());
        if (!el) {
            return;
        }
        var sel = selectionOf(el);
        sh.el = el;
        sh.pos = null;
        if (sel && sel.rangeCount) {
            var r = sel.getRangeAt(0);
            var sp = pathOf(el, r.startContainer);
            var ep = pathOf(el, r.endContainer);
            if (sp && ep) {
                sh.pos = { sp: sp, so: r.startOffset, ep: ep, eo: r.endOffset };
            }
        }
    }

    // Only while a field has the focus: when it is losing it (focusout) the
    // selection is no longer reliable
    ["keyup", "mouseup", "input", "selectionchange"].forEach(function (type) {
        document.addEventListener(type, function () { remember(); }, true);
    });

    // Toolbar selects: remember the field before they take the focus, and
    // freeze it: when the field loses the focus the editor collapses its
    // selection, which must not overwrite the position we want to go back to.
    function shCmd(el) {
        return el && el.getAttribute ? el.getAttribute("data-sh-cmd") : null;
    }
    ["mousedown", "focusin"].forEach(function (type) {
        document.addEventListener(type, function (event) {
            if (shCmd(event.target) && !sh.frozen) {
                remember();
                sh.frozen = true;
            }
        }, true);
    });
    // the user is back in a field by himself: follow him again
    ["mousedown", "keydown"].forEach(function (type) {
        document.addEventListener(type, function (event) {
            var path = event.composedPath ? event.composedPath() : [];
            if (fieldOf(path[0])) {
                sh.frozen = false;
            }
        }, true);
    });
    document.addEventListener("change", function (event) {
        var cmd = shCmd(event.target);
        if (cmd) {
            pycmd(cmd + ":" + event.target.value);
        }
    }, true);

    function selectionInside(el) {
        var sel = selectionOf(el);
        return !!(sel && sel.rangeCount && el.contains(sel.getRangeAt(0).commonAncestorContainer));
    }

    // Give the focus (and the selection) back to the last field
    function restore() {
        var el = fieldOf(deepActive());
        if (!el) {
            if (!sh.el || !sh.el.isConnected) {
                sh.frozen = false;
                return null;
            }
            el = sh.el;
            el.focus();
        }
        if (sh.pos && el === sh.el && (sh.frozen || !selectionInside(el))) {
            var r = rangeFromPos(el, sh.pos);
            if (r) {
                var sel = selectionOf(el);
                sel.removeAllRanges();
                sel.addRange(r);
            }
        }
        sh.frozen = false;
        return el;
    }

    // Blocks: new ones are <table class="sh-block">, older ones (add-on 1.0
    // and 1.1) a <div class="highlight"> wrapped in a <table>
    function blockOf(div) {
        var table = div.closest("table." + "sh-block");
        if (table) {
            return table;
        }
        var td = div.parentElement;
        if (td && td.tagName === "TD") {
            var t = td.closest("table");
            if (t && t.rows.length === 1 && t.rows[0].cells.length === 1) {
                return t;
            }
        }
        return div;
    }

    var LEGACY_LINENO = /padding-left:\s*5px;\s*padding-right:\s*5px/;

    function codeOf(block) {
        var pre = block.querySelector("pre");
        if (!pre) {
            return "";
        }
        var copy = pre.cloneNode(true);
        copy.querySelectorAll(".sh-ln, .linenos").forEach(function (n) { n.remove(); });
        copy.querySelectorAll("span[style]").forEach(function (n) {
            if (LEGACY_LINENO.test(n.getAttribute("style")) && /^\s*\d*\s*$/.test(n.textContent)) {
                n.remove();
            }
        });
        copy.querySelectorAll("br").forEach(function (n) { n.replaceWith("\n"); });
        return copy.textContent.replace(/ /g, " ");
    }

    function blocksInSelection(el) {
        var sel = selectionOf(el);
        if (!sel || !sel.rangeCount) {
            return [];
        }
        var range = sel.getRangeAt(0);
        var found = [];
        el.querySelectorAll("div.highlight").forEach(function (div) {
            var b = blockOf(div);
            if (found.indexOf(b) < 0 && range.intersectsNode(b)) {
                found.push(b);
            }
        });
        return found;
    }

    /* Prepare an operation: focus the last field and report the blocks under
     * the caret/selection, or the selected text when there are none. */
    sh.prepare = function () {
        sh.targets = [];
        var el = restore();
        if (!el) {
            return { ok: false };
        }
        var blocks = blocksInSelection(el);
        sh.targets = blocks;
        var sel = selectionOf(el);
        return {
            ok: true,
            selected: blocks.length || !sel ? "" : sel.toString(),
            blocks: blocks.map(function (b) {
                return {
                    code: codeOf(b),
                    lang: b.getAttribute("data-sh-lang"),
                    theme: b.getAttribute("data-sh-theme"),
                };
            }),
        };
    };

    sh.insert = function (html) {
        restore();
        pasteHTML(html, true, false);
    };

    // Replace the prepared blocks, last to first (an undo step each)
    sh.replace = function (htmls) {
        var el = restore();
        if (!el) {
            return 0;
        }
        var sel = selectionOf(el);
        var done = 0;
        for (var i = sh.targets.length - 1; i >= 0; i--) {
            var b = sh.targets[i];
            if (!b.isConnected || htmls[i] == null) {
                continue;
            }
            var r = document.createRange();
            r.selectNode(b);
            sel.removeAllRanges();
            sel.addRange(r);
            pasteHTML(htmls[i], true, false);
            done++;
        }
        sh.targets = [];
        remember();
        return done;
    };
})();
