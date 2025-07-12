# core/server/modules/auth/__init__.py

from flask import g
from flask_jwt_extended import (
    JWTManager,
    get_current_user,
    verify_jwt_in_request,
    jwt_required as auth_required,
    current_user,
)

from dateutil.relativedelta import relativedelta
from core.server.json_encoder import normalize_json_error
from core.server.modules.auth.middleware import RewriteJWTTokenLocationMiddleware
from core.server.modules.auth.resources import ns_auth, LoginResource


# Initialisation de l'extension JWT (à appeler dans setup)
jwt = JWTManager()


########################################
# Gestion des erreurs JWT
########################################


@jwt.token_verification_failed_loader
def token_verification_failed_loader():
    return normalize_json_error(
        "VerificationFailed", "User claims verification failed", 400
    )


@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    return normalize_json_error("ExpiredToken", "Token has expired", 401)


@jwt.invalid_token_loader
def invalid_token_loader(error_string):
    return normalize_json_error("InvalidToken", error_string, 422)


@jwt.needs_fresh_token_loader
def needs_fresh_token_loader(jwt_header, jwt_payload):
    return normalize_json_error("NeedsFreshToken", "Fresh token required", 401)


@jwt.revoked_token_loader
def revoked_token_loader(jwt_header, jwt_payload):
    return normalize_json_error("RevokedToken", "Token has been revoked", 401)


@jwt.unauthorized_loader
def unauthorized_loader(error_string):
    return normalize_json_error("Unauthorized", error_string, 401)


@jwt.user_lookup_error_loader
def user_lookup_error_loader(jwt_header, jwt_payload):
    return normalize_json_error("UserLoaderError", "Error loading the user", 401)


########################################
# Setup du module auth
########################################


def setup_resources(api, app, factory_user_model):
    """
    Initialise le module d'authentification avec JWT, les ressources REST et le middleware optionnel.
    """
    jwt.init_app(app)
    expirations = app.config.auth.expiration

    app.config["LOGIN_FACTORY"] = {
        "factory_user_model": factory_user_model,
        "delta_not_remember_me": relativedelta(**expirations.not_remember_me),
        "delta_remember_me": relativedelta(**expirations.remember_me),
    }
    api.add_namespace(ns_auth, path="/auth")

    # Récupération de l'utilisateur à partir du token
    @jwt.user_lookup_loader
    def user_lookup_loader(jwt_header, jwt_data):
        UserModel = factory_user_model()
        return UserModel.get(jwt_data["sub"]["id"])

    # Injection dans `g.current_user` (utile même hors décorateur `@auth_required`)
    @app.before_request
    def inject_user():
        if verify_jwt_in_request(optional=True):
            user = get_current_user()
        else:
            user = None
        g.current_user = user

    # Middleware de réécriture d'identité si activé
    if app.config.auth.jwt_is_identity:
        app.wsgi_app = RewriteJWTTokenLocationMiddleware(app)


# Exportés pour les autres modules
__all__ = ["setup", "auth_required", "current_user", "jwt"]
