#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
import importlib
from types import SimpleNamespace
from typing import Union

# Imports from external libraries

# Import from local code
from core.services.tools_belt import humps
from .core import SQLClient, SQLAutomapClient


class DatabaseNamespace(SimpleNamespace):
    def __recursive_call(self, method_name):
        for child in self.__dict__.values():
            method = getattr(child, method_name, None)
            if not method:
                continue
            method()

    def rollback(self):
        return self.__recursive_call("rollback")

    def commit(self):
        return self.__recursive_call("commit")

    def close(self):
        return self.__recursive_call("close")

    def close_all(self):
        return self.__recursive_call("close_all")

    def disconnect(self):
        return self.__recursive_call("disconnect")


def _setup_database(bind: str, config: Union[str, dict], base_setup_module: str) -> SQLClient:
    kwargs = dict(config)
    # Importation dynamique de la mise en place des modèles pour les différentes
    # base de données
    module_name = "%s.%s" % (base_setup_module, bind)
    module_name = module_name.replace("-", "_")
    kwargs["bind_key"] = bind
    try:
        module = importlib.import_module(module_name)
        kwargs["setup"] = module.setup
        kwargs["module_key"] = module_name
    except ModuleNotFoundError:
        # TODO: Créer un warning
        pass
    # Instanciation du client de la base de données
    ClientClass = SQLAutomapClient if kwargs.pop("automap", True) else SQLClient
    return ClientClass(**kwargs)


def build_modules(binds: dict, base_setup_module: str) -> DatabaseNamespace:
    """
    Pour chaque entrée dans SQLALCHEMY_BINDS, on va créer un ensemble de modules
    groupés par les entrées divisées par des points.
    Par exemple, pour les binds sous la forme :

        ['cairn.back-office.pub', 'cairn.back-office.com',
         'cairn-int.back-office.pub', 'cairn-int.back-office.com']

    Ça va donner des modules sous la forme :

        cairn.back_office.pub
        cairn.back_office.com
        cairn_int.back_office.pub
        cairn_int.back_office.com
    """
    modules = DatabaseNamespace()
    for bind, config in binds.items():
        if bind in ("box_it_up",):
            # La bibliothèque Box n'utilise plus ce paramètre, qui est encore utilisé par dynaconf
            # (dans la classe DynaBox)
            # Pour éviter tout souci, on ignore cet attribut.
            continue
        parent = modules
        parts = bind.split(".")
        for index, part in enumerate(parts, 1):
            part = humps.snakize(part)
            current = getattr(parent, part, None)
            if not current:
                if index < len(parts):
                    current = DatabaseNamespace()
                else:
                    current = _setup_database(bind, config, base_setup_module)
                setattr(parent, part, current)
            parent = current
    return modules
