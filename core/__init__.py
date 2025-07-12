#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
import os
import tempfile
import logging.config

# Imports from external libraries
from dynaconf import Dynaconf

# Import from local code


__all__ = [
    "setup_settings",
    "settings",
]


def setup_settings(**kwargs):
    """
    Instanciation de dynaconf avec les options **kwargs, et les valeurs par défaut usuelles.
    Permet l'injection de variables d'environnement avec l'entrée ENVIRON
    """
    # Les variables d'environnements par défaut, qui seront utilisable par les fichiers dynaconf
    os.environ.setdefault("TEMPDIR", tempfile.gettempdir())
    # Paramètre par défaut
    kwargs.setdefault(
        "settings_files",
        [
            "settings.yaml",
            ".secrets.yaml",
        ],
    )
    kwargs.setdefault("load_dotenv", True)
    kwargs.setdefault("environments", True)
    kwargs.setdefault("merge_enabled", True)
    # Instanciation de dynaconf
    dynaconf = Dynaconf(**kwargs)
    # Injection dans l'environnement des variables définies dans la conf
    for name, value in dynaconf.get("ENVIRON", {}).items():
        os.environ.setdefault(name, str(value))
    # Flask doit surveiller automatiquement les fichiers de conf, c'est à dire
    # qu'il se relance quand ils sont modifiés et qu'il est en mode debug
    extra_files = os.environ.get("FLASK_RUN_EXTRA_FILES", "").split(":")
    extra_files.extend(kwargs["settings_files"])
    os.environ["FLASK_RUN_EXTRA_FILES"] = ":".join(extra_files)
    # Mise en place de la configuration pour les logs
    if "LOGGING_CONFIG" in dynaconf:
        logging.config.dictConfig(dynaconf["LOGGING_CONFIG"])
    return dynaconf


settings = setup_settings()

import warnings

warnings.filterwarnings("ignore")
