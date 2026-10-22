# -*- coding: utf-8 -*-

"""
Anki Add-on: Syntax Highlighting (NG) — Themes edition

Module-level entry point for the add-on (Anki 2.1.55+ / 23.x / 24.x / 25.x+).

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
           (c) 2023- A. Cavallo <https://github.com/cav71>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""
import os
import sys

from ._version import __version__  # noqa: F401
from .consts import PYGMENTS_WHEEL

# Always use the shipped pygments library. Anki itself does not bundle
# pygments, so putting the wheel first on sys.path is enough.
if PYGMENTS_WHEEL not in sys.path:
    sys.path.insert(0, PYGMENTS_WHEEL)

STANDALONE = False
try:
    import aqt  # noqa: F401
except ModuleNotFoundError as e:
    # allow importing the rendering modules (eg. from unit tests)
    # without a running Anki
    if not os.environ.get("STANDALONE_ADDON") == "1":
        raise RuntimeError(
            "set env STANDALONE_ADDON=1 if you don't need anki modules"
        ) from e
    STANDALONE = True
else:
    from . import main  # noqa: F401
