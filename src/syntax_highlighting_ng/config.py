# -*- coding: utf-8 -*-

"""
This file is part of the Syntax Highlighting add-on for Anki.

Configuration: synced options (stored in the collection, so they follow
the user across machines) and local options (config.json).

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import annotations

import copy
from typing import Any

from aqt import mw

from . import themes

KEY = "syntax_highlighting_ng_conf"

# Synced conf defaults
default_conf: dict[str, Any] = {
    "linenos": True,  # show line numbers
    "centerfragments": False,  # center the code blocks
    "cssclasses": False,  # use css classes instead of inline colors
    "defaultlangperdeck": True,  # remember the last language per deck
    "deckdefaultlang": {},  # deck name -> language
    "lang": "Python",  # default language
    "style": themes.DEFAULT_THEME,  # highlight theme
}


def get_synced() -> dict[str, Any]:
    """Synced options, merged with the defaults (a fresh copy)"""
    stored = {}
    if mw.col is not None:
        stored = mw.col.get_config(KEY, default={}) or {}
    conf = copy.deepcopy(default_conf)
    conf.update({k: v for k, v in stored.items() if k in default_conf})
    if not themes.is_valid(conf["style"]):
        conf["style"] = themes.DEFAULT_THEME
    return conf


def set_synced(conf: dict[str, Any]) -> None:
    if mw.col is None:
        return
    mw.col.set_config(KEY, {k: conf[k] for k in default_conf if k in conf})


def update_synced(**changes: Any) -> dict[str, Any]:
    conf = get_synced()
    conf.update(changes)
    set_synced(conf)
    return conf


# Local conf (config.json, editable from the add-ons manager)


def get_local() -> dict[str, Any]:
    return mw.addonManager.getConfig(__name__) or {}
