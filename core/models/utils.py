#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from collections import OrderedDict

# Imports from external libraries
from sqlalchemy import inspect

# Import from local code
from core.services.tools_belt import humps


class HashableOrderedDict(OrderedDict):
    """
    Un dictionnaire ordonnée pouvant être utilisé comme clé d'un autre dictionnaire
    """

    def __hash__(self):
        return hash(tuple(self.items()))


def normalize_db_name(name: str) -> str:
    """
    Normalise le nom des bases de données
    """
    return humps.snakize(name.lower())


def denormalize_db_name(name: str) -> str:
    return name


def normalize_table_name(name: str) -> str:
    """
    Les tables de cairn sont en MAJUSCULE_UNDERSCORE.
    On les normalise sous la forme PascalCase pour les accès python.
    """
    name = humps.snakize(name)
    return humps.pascalize(name)


def denormalize_table_name(name: str) -> str:
    """
    Opération inverse de `normalize_table_name`
    """
    name = humps.snakize(name)
    return name.upper()


def normalize_column_name(name: str) -> str:
    """
    Les colonnes de cairn sont en MAJUSCULE_UNDERSCORE.
    On les normalise sous la forme majuscule_underscoe pour les accès python.
    """
    return humps.snakize(name.lower())


def denormalize_column_name(name: str) -> str:
    """
    Opération inverse de `normalize_column_name`
    """
    name = humps.snakize(name)
    return name.upper()


def normalize_keys(items: dict) -> OrderedDict:
    keys = sorted(items.items())
    keys = tuple(keys)
    keys = HashableOrderedDict(keys)
    return keys


def normalize_sql_keys(items: dict) -> dict:
    keys = {normalize_column_name(k): v for k, v in items.items()}
    return keys


def extract_primary_keys_from_instance(instance):
    Model, values = inspect(instance).key
    primary_keys = {c.name: values[i] for i, c in enumerate(inspect(Model).primary_key)}
    primary_keys = OrderedDict(sorted(primary_keys.items()))
    return primary_keys


def get_database_real_name_from_table(Table):
    return Table._metadata[Table.__bind_key__].bind.url.database
