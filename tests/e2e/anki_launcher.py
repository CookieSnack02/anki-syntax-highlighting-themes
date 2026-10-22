"""Start an isolated Anki 26.9.3 (temp base folder, own single-instance key,
remote DevTools) with the add-on under test plus the e2e helper add-on.

    python anki_launcher.py <addon_src> <base_dir> [legacy|new]

Used by run.py; not meant to be run by hand.
"""
import os, shutil, site, sys

A = os.environ.get("ANKI_APP_PACKAGES") or os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "Programs", "Anki", "app_packages")
site.addsitedir(A)
sys.path.insert(0, A)
HERE = os.path.dirname(os.path.abspath(__file__))

addon_src, base = sys.argv[1], sys.argv[2]
os.environ["SH_E2E_MODE"] = sys.argv[3] if len(sys.argv) > 3 else "legacy"
os.environ["SH_E2E_LOG"] = os.path.join(base + "-bridge.log")
open(os.environ["SH_E2E_LOG"], "w").close()

shutil.rmtree(base, ignore_errors=True)
addons = os.path.join(base, "addons21")
os.makedirs(os.path.join(addons, "e2e_helper"))
shutil.copytree(addon_src, os.path.join(addons, "syntax_highlighting_ng"),
                ignore=shutil.ignore_patterns("__pycache__", "meta.json"))
shutil.copy(os.path.join(HERE, "e2e_helper.py"), os.path.join(addons, "e2e_helper", "__init__.py"))

os.environ["ANKI_SINGLE_INSTANCE_KEY"] = "sh-e2e-test"
os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9333"

import aqt.profiles

# skip the first-run language dialog
def _set_default_lang(self, idx=None):
    self.setLang("pt_BR")
aqt.profiles.ProfileManager.setDefaultLang = _set_default_lang

import aqt
sys.argv = ["anki", "-b", base]
aqt.run()
