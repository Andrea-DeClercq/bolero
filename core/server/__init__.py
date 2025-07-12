#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from functools import wraps
import importlib
import pkgutil
import re

# Imports from external libraries
from dynaconf import FlaskDynaconf
from flask import Blueprint, current_app, json
from flask.cli import AppGroup as _AppGroup

from flask_cors import CORS
from path import Path
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix
import arrow
import click

# Import from local code
from .error import app_handle_error, JSONHTTPException
from .json_encoder import JSONProvider
from .views import Api, Schema
from core.server.api import BoleroAPI


# Monkey patching pour flask_restful qui utilise la bibliothèque python pour JSON
# Y a certainement moyen de faire autrement, je m'en occuperais plus tard


__all__ = [
    "abort",
    "CoreServer",
    "Schema",
]


###############################################################################
# Fonctions utilitaires
###############################################################################
class ModuleInvalidException(Exception):
    pass


class AppGroup(_AppGroup):
    def command(self, *args, **kwargs):
        parent = super()

        def decorator_command(fn):
            @wraps(fn)
            def wrapper_fn(*subargs, **subkwargs):
                """
                Permet d'injecter et d'enregistrer la date de dernière exécution d'une commande
                """
                now = arrow.utcnow()
                ctx = click.get_current_context()
                littledb_key = ctx.command_path.replace(" ", ":")
                littledb_table = current_app.littledb.last_execution
                ctx.ensure_object(dict)
                ctx.obj["last_execution"] = littledb_table[littledb_key]
                result = fn(*subargs, **subkwargs)
                littledb_table[littledb_key] = now
                return result

            return parent.command(*args, **kwargs)(wrapper_fn)

        return decorator_command

    # def invoke(self, ctx, *args, **kwargs):
    #     print(ctx.invoked_subcommand)
    #     ctx.ensure_object(dict)
    #     # ctx.obj["last_execution"] = current_app.last_execution
    #     return super().invoke(ctx, *args, **kwargs)


def abort(status_code, body=None, headers=None):
    """Arrête la requête en renvoyant un message JSON"""
    headers = headers or dict()
    error_cls = JSONHTTPException

    class_name = error_cls.__name__
    bases = [error_cls]
    attributes = {"code": status_code}

    error_cls = type(class_name, tuple(bases), attributes)
    raise error_cls(body)


###############################################################################
# Extension flask
###############################################################################
class CoreServer:
    def __init__(self, app=None, base_setup_module=None, dynaconf_instance=None):
        self.app = app
        self.api = None
        self.base_setup_module = base_setup_module
        self.dynaconf_instance = dynaconf_instance
        if app is not None:
            self.init_app(app)

    def load_documentation(self):
        """
        Charge automatiquement tous les fichiers de documentation
        dans `core/server/documentation/`
        """
        package = "core.server.documentation"
        for _, module_name, _ in pkgutil.iter_modules(["core/server/documentation"]):
            importlib.import_module(f"{package}.{module_name}")

    def init_app(self, app):
        # Configuration
        app.json = JSONProvider(app)
        app.url_map.strict_slashes = False

        # Mise en place extensions
        app.extensions["core"] = self
        FlaskDynaconf(app, dynaconf_instance=self.dynaconf_instance)
        CORS(app, resources={r"*": {"origins": "*"}})

        # Création de l'instance API RESTX avec Swagger intégré
        self.api = BoleroAPI(app).api
        self.load_documentation()
        # Gestion des erreurs
        app.register_error_handler(Exception, app_handle_error)
        # Permet d'afficher les valeurs des variables dans la traceback
        if app.config.DEBUG_TRACEBACK_WITH_VARIABLE:
            from traceback_with_variables import activate_by_import

        # Proxy HTTP pour la production
        if app.config.get("APP_PROXY_FIX"):
            app.wsgi_app = ProxyFix(app.wsgi_app)

        # Proxy de profile pour mesurer les performances
        if app.config.get("APP_PROXY_PROFILE"):
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir="./_profile")

    def init_modules(self, app, modules: list, base_setup_module: str = None):
        for module in modules:
            self.init_module(app, module, base_setup_module)

    def init_module(
        self, app, name: str, base_setup_module: str = None, *args, **kwargs
    ):
        if not base_setup_module:
            if self.base_setup_module:
                base_setup_module = self.base_setup_module
            else:
                raise ModuleInvalidException()

        # Importation dynamique de la mise en place des modèles pour les différentes bases de données
        module_name = f"{base_setup_module}.{name}"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            app.logger.exception('Module "%s" not found', module_name)
            return

        blueprint = Blueprint(
            name.replace(".", "/"),
            module_name,
            template_folder="templates",
        )

        # Appeler setup_resources avec l'API existante (sans créer de namespace)
        module.setup_resources(self.api, app, *args, **kwargs)

        # Enregistrer le blueprint, mais **pas de namespace ici**
        app.register_blueprint(blueprint, url_prefix=f"/{name.replace('.', '/')}")

        app.logger.info('Module "%s" chargé', name)
        self.init_cli(app, f"{module_name}.cli", base_setup_module, strict=False)

    def init_cli(self, app, module_name, base_setup_module=None, strict=True):
        # Récupération du chemin absolu du module de cli
        module_path = module_name.replace(".", "/")
        module_path = Path(f"./{module_path}").absolute()

        if not strict and not module_path.exists():
            return

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            app.logger.exception('Cli "%s" not found', module_name)
            return

        # Mise en place du groupe cli
        cli_group_name = re.sub(
            rf"^{base_setup_module}\.(.*?)(\.cli)?$",
            r"\1",
            module_name,
        )
        try:
            cli_group_help = module.setup.__doc__
        except AttributeError:
            cli_group_help = None
        cli_group = AppGroup(cli_group_name, help=cli_group_help)
        app.cli.add_command(cli_group)

        # Si le module contient une fonction setup, elle doit être lancée
        if hasattr(module, "setup"):
            module.setup(app, cli_group)
            app.logger.info('Cli "%s" chargé', module_name)

        # Si le module est un dossier, vérification des sous-modules
        if not module_path.is_dir():
            return

        for submodule_info in pkgutil.iter_modules([module_path]):
            if submodule_info.name.startswith("_"):
                continue
            submodule_name = f"{module_name}.{submodule_info.name}"
            try:
                submodule = importlib.import_module(submodule_name)
            except ModuleNotFoundError:
                app.logger.exception('Cli submodule "%s" not found', submodule_name)
                return
            # Nom du sous-module
            cli_subgroup_name = re.sub(
                rf"^{module_name}.(.*?)(\.cli)?$",
                r"\1",
                submodule_name,
            )
            # Ajout du sous-module
            cli_subgroup = AppGroup(cli_subgroup_name, help=submodule.setup.__doc__)
            cli_group.add_command(cli_subgroup)
            submodule.setup(app, cli_subgroup)
            app.logger.info('Cli "%s" chargé', submodule_name)
