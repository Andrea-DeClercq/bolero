from datetime import datetime, timezone
from urllib.parse import urlencode
import uuid

from jwt import encode as jwt_encode
from jwt.algorithms import requires_cryptography
from werkzeug import Request

from core.services.jsonlib import JSONEncoder
from core.services.tools_belt import humps


class RewriteJWTTokenLocationMiddleware:
    """
    Middleware pour réécrire les tokens JWT passés sous forme brute
    en un token JWT correctement encodé et inséré dans l'environnement WSGI.
    """

    def __init__(self, app):
        algorithm = app.config["JWT_ALGORITHM"]
        if algorithm in requires_cryptography:
            key = app.config["JWT_PRIVATE_KEY"]
        else:
            key = app.config["JWT_SECRET_KEY"] or app.config["SECRET_KEY"]
        if not key:
            raise NotImplementedError("Clé de chiffrement JWT manquante")

        self._wsgi_app = app.wsgi_app
        self._config = {
            "locations": app.config["JWT_TOKEN_LOCATION"],
            "algorithm": algorithm,
            "identity_claim": app.config["JWT_IDENTITY_CLAIM"],
            "key": key,
            "headers": {
                "name": app.config["JWT_HEADER_NAME"],
                "type": app.config["JWT_HEADER_TYPE"],
            },
            "query_string": {
                "name": app.config["JWT_QUERY_STRING_NAME"],
                "prefix": app.config["JWT_QUERY_STRING_VALUE_PREFIX"],
            },
            "json": {
                "key": app.config["JWT_JSON_KEY"],
                "refresh_key": app.config["JWT_REFRESH_JSON_KEY"],
            },
        }

    def __call__(self, environ, start_response):
        request = environ["werkzeug.request"]
        for location in self._config["locations"]:
            if location == "headers":
                self._handle_header_token(request, environ)
                break
            if location == "query_string":
                self._handle_query_token(request, environ)
                break
            if location == "json":
                # Non implémenté
                continue
            if location == "cookies":
                continue
            raise NotImplementedError(f"JWT token location non supportée: {location}")
        return self._wsgi_app(environ, start_response)

    def _encode_jwt_token(self, jwt_token):
        payload = {
            "fresh": False,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "type": "access",
            self._config["identity_claim"]: jwt_token,
        }
        return jwt_encode(
            payload,
            key=self._config["key"],
            algorithm=self._config["algorithm"],
            json_encoder=JSONEncoder,
        )

    def _handle_header_token(self, request, environ):
        header_name = self._config["headers"]["name"]
        jwt_token = request.headers.get(header_name)
        if not jwt_token:
            return
        jwt_token_prefix = self._config["headers"]["type"]
        if not jwt_token.startswith(jwt_token_prefix):
            return
        jwt_token = jwt_token.removeprefix(jwt_token_prefix)
        jwt_token = self._encode_jwt_token(jwt_token)
        environ[f"HTTP_{humps.snakize(header_name).upper()}"] = (
            f"{jwt_token_prefix} {jwt_token}"
        )
        environ["werkzeug.request"] = Request(environ)

    def _handle_query_token(self, request, environ):
        param_name = self._config["query_string"]["name"]
        jwt_token = request.args.get(param_name)
        if not jwt_token:
            return
        prefix = self._config["query_string"]["prefix"]
        if not jwt_token.startswith(prefix):
            return
        jwt_token = jwt_token.removeprefix(prefix)
        jwt_token = self._encode_jwt_token(jwt_token)
        environ["QUERY_STRING"] = urlencode(
            dict(request.args, **{param_name: f"{prefix}{jwt_token}"})
        )
        environ["werkzeug.request"] = Request(environ)
