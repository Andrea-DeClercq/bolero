#!/usr/bin/env python
"""
Permet d'encoder/decoder correctement les json
"""
# Import from stdlib
from datetime import datetime, date
from enum import Enum
from functools import partial
import json

# Imports from external libraries
from arrow import Arrow
from flask.json.provider import _default

# Import from local code


def default(o):  # pylint: disable=invalid-name
    """
    Si l'encodeur json n'arrive pas à gérer un type de donnée, on le fait ici en priorité
    puis on le renvoi à celui de flask
    """
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Arrow):
        return str(o)
    if isinstance(o, Enum):
        return o.value
    return _default(o)


class JSONEncoder(json.JSONEncoder):
    """
    Encodeur vers JSON
    """

    def default(self, o):
        return default(o)


load = json.loads
loads = json.loads
dump = partial(json.dump, cls=JSONEncoder)
dumps = partial(json.dumps, cls=JSONEncoder)
