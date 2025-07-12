#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
import pkgutil

# Imports from external libraries
from box import Box
from flask import Flask, Response, g
from flask_jwt_extended import current_user

from path import Path
from sentry_sdk import set_user as set_user_sentry
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import arrow
import sentry_sdk

# Import from local code
from bolero.models import databases
from config import settings
from core.server import CoreServer
from core.server.flask_littledb import LittleDB
from core.services.tools_belt import RemapWsgiEnvMiddleware


# Initialisation de l'appli
app = Flask("bolero", static_folder=None)
if settings.remap_wsgi_env or settings.inject_wsgi_env:
    app.wsgi_app = RemapWsgiEnvMiddleware(
        app.wsgi_app, settings.remap_wsgi_env, settings.inject_wsgi_env
    )

# Chargement des plugins Flask
core = CoreServer(
    app=app,
    dynaconf_instance=settings,
    base_setup_module="bolero.server.modules",
)

littleDB = LittleDB(app)

# Chargement des modules
core.init_modules(
    app,
    app.config["MODULES"],
)

# Module d'authentification avec JWT
core.init_module(
    app, "auth", "core.server.modules", lambda: databases.bolero.queries.User
)

# Chargement des modules cli présent dans bolero/cli
for submodule_info in pkgutil.iter_modules([Path.cwd() / "bolero/cli"]):
    if submodule_info.name.startswith("_"):
        continue
    core.init_cli(app, f"bolero.cli.{submodule_info.name}", "bolero.cli")

# Initialisation de Sentry
sentry_config = app.config["SENTRY"]
if sentry_config.enabled:
    sentry_options = sentry_config.init_options
    sentry_options.setdefault("environment", settings.current_env)
    sentry_options.setdefault(
        "integrations",
        [
            FlaskIntegration(),
            SqlalchemyIntegration(),
        ],
    )
    sentry_sdk.init(**sentry_options)


@app.before_request
def inject_services():
    """
    Injection de différents services
    """

    # Ajout des informations utilisateur à Sentry
    if current_user:
        set_user_sentry(
            {
                "id": current_user.id,
                "username": f"{current_user.username}",
                # "email": current_user.email,
                "ip": "{{auto}}",
            }
        )


@app.teardown_appcontext
def teardown_sql(error=None):
    databases.disconnect()
    databases.close_all()


@app.route("/ping")
def ping():
    """Pour vérifier que l'appli est bien vivante"""
    return Response("pong", mimetype="text/plain")


@app.route("/raise-error")
def trigger_error():
    """Pour tester l'envoi vers Sentry"""
    division_by_zero = 1 / 0
    return division_by_zero


# On ferme les connexions qui ont pu s'ouvrir lors du setup de l'app
databases.disconnect()
databases.close_all()
