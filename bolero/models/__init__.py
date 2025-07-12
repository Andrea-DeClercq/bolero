#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
from __future__ import unicode_literals, print_function, division

# Import from stdlib

# Imports from external libraries

# Import from local code
from config import settings
from core.models import build_modules


binds = dict()
common_config = settings["SQL"]["common"]
for modname, bind in settings["SQL"]["binds"].items():
    binds[modname] = common_config.copy()
    if isinstance(bind, str):
        bind = {"database_uri": bind}
    binds[modname].update(bind)


databases = build_modules(binds, __package__)
