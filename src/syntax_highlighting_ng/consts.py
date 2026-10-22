# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Global variables

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import os

addon_path = os.path.dirname(__file__)

# Vendored libraries (pygments 2.21.0), as plain folders: importing from a .whl
# (zipimport) keeps the file open, and on Windows Anki then cannot delete the
# add-on folder to update it while it is running.
LIBS_PATH = os.path.join(addon_path, "libs")
ICON_PATH = os.path.join(addon_path, "icons", "button.png")
EDITOR_JS_PATH = os.path.join(addon_path, "editor.js")
