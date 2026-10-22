"""End-to-end test in a real, isolated Anki (Windows installer of Anki 26.x).

    python -m pip install websocket-client
    python -I tests/e2e/run.py [legacy|new|both]

Starts Anki from its own packages with a throwaway base folder (your profile is
never touched), its own single-instance key (it runs next to an open Anki) and
remote DevTools on port 9333; installs the add-on from src/ plus a test helper,
opens Add Cards, and drives the editor: insert, Ctrl+Z, theme/language changes
on existing blocks, blocks made by older versions; last, installs the built
package over the running add-on (Windows file locks).

Needs a Python with the same minor version as Anki's (3.13): Anki ships only
bytecode. Another Anki install: set ANKI_APP_PACKAGES to its packages folder.
The Anki window shows up while the test runs.
"""
import os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ADDON = os.path.normpath(os.path.join(HERE, "..", "..", "src", "syntax_highlighting_ng"))


def run(mode: str) -> int:
    base = tempfile.mkdtemp(prefix=f"sh-e2e-{mode}-")
    print(f"===== {mode} editor (base: {base})", flush=True)
    log = open(base + "-anki.log", "w", encoding="utf-8")
    anki = subprocess.Popen(
        [sys.executable, "-I", os.path.join(HERE, "anki_launcher.py"), ADDON, base, mode],
        stdout=log, stderr=subprocess.STDOUT,
    )
    code = 1
    try:
        code = subprocess.call([sys.executable, "-I", os.path.join(HERE, "scenarios.py")])
        return code
    finally:
        anki.kill()
        anki.wait()
        log.close()
        # its child processes (web engine) may still hold files for a moment
        for _ in range(10):
            shutil.rmtree(base, ignore_errors=True)
            if not os.path.exists(base):
                break
            time.sleep(0.5)
        if code == 0:
            for suffix in ("-anki.log", "-bridge.log"):
                if os.path.exists(base + suffix):
                    os.remove(base + suffix)
        else:
            print(f"logs: {base}-anki.log, {base}-bridge.log")


if __name__ == "__main__":
    # the package is installed over the running add-on in the last scenario
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    import build

    os.environ["SH_E2E_PACKAGE"] = build.build_package()
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    modes = ["legacy", "new"] if which == "both" else [which]
    failed = [m for m in modes if run(m) != 0]
    print("\nE2E:", "OK" if not failed else f"FAILED in {failed}")
    sys.exit(1 if failed else 0)
