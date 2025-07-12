#!/usr/bin/env python
"""
TODO: Utiliser le module core.services.error pour sérialiser les erreurs
"""
# Import from stdlib

# Imports from external libraries
from flask import current_app, json, request
from werkzeug.exceptions import HTTPException
from flask_jwt_extended.exceptions import NoAuthorizationError

# Import from local code
from .json_encoder import normalize_json_error


####################################################################################################
# Exceptions HTTP
####################################################################################################
class JSONHTTPException(HTTPException):
    """
    Réponse à renvoyer à l'utilisateur.
    Formatte une exception au format json
    """

    def get_description(self, environ=None):
        return self.description

    def get_body(self, environ=None):
        return json.dumps(
            **{
                "status": 500,
                "type": "error",
                "data": {
                    "name": self.__class__.__name__,
                    "description": self.get_description(environ),
                    "error": self.code,
                },
            }
        )

    def get_headers(self, environ=None):
        return [("Content-Type", "application/json")]


class SafeClientException(Exception):
    """
    Indique qu'on peut envoyer le message et le nom de l'exception sans souci au client
    """

    code = 500

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def description(self):
        return str(self)


####################################################################################################
# Fonctions utilitaires
####################################################################################################
def abort(status_code=500, body=None):
    """
    Met fin à la requête en cours en renvoyant une erreur générique.
    La fonction abort de flask renvoi systématiquement une erreur html.
    """
    normalize_json_error(name, description, code)
    error = JSONHTTPException(body)
    error.code = status_code
    raise error


###############################################################################
# Capture et manipulation des erreurs
###############################################################################
def app_handle_error(err):
    """
    Gestion des erreurs capturés tout au long de l'app
    """
    # Initialisation de l'erreur
    is_debug = current_app.config["DEBUG_EXCEPTION"]

    if isinstance(err, (HTTPException, SafeClientException)):
        # Il s'agit d'une erreur HTTP lambda, on peut envoyer les infos sans souci
        name = err.name
        code = err.code
        description = err.description
    else:
        # Le programme rencontre une erreur inconnue, on empêche l'affichage d'infos en prod
        current_app.logger.exception("On %s", request)
        code = 500
        name = err.__class__.__name__ if is_debug else "ServerError"
        description = (
            str(err) if current_app.config["DEBUG_EXCEPTION"] else "server error"
        )
    return normalize_json_error(name, description, code)
