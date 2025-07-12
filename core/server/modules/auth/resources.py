from flask import request, current_app, jsonify
from flask_restx import Resource, Namespace, fields
from werkzeug.exceptions import BadRequest

from .views import LoginView

ns_auth = Namespace("Authentification", description="Authentification JWT")

# Modèle pour Swagger uniquement — pas utilisé pour valider
ns_auth.model(
    "Authentification",
    {
        "identifier": {
            "type": "string",
            "description": "Nom d'utilisateur",
            "required": True,
        },
        "type": {
            "type": "string",
            "default": "username",
            "description": "Type d'identifiant",
        },
        "password": {"type": "string", "description": "Mot de passe", "required": True},
        "remember_me": {
            "type": "boolean",
            "default": False,
            "description": "Connexion prolongée",
        },
    },
)

login_model = ns_auth.model(
    "Authentification",
    {
        "identifier": fields.String(required=True, description="Nom d'utilisateur"),
        "type": fields.String(default="username", description="Type d'identifiant"),
        "password": fields.String(required=True, description="Mot de passe"),
        "remember_me": fields.Boolean(default=False, description="Connexion prolongée"),
    },
)


@ns_auth.route("/login")
class LoginResource(Resource):
    def __init__(self, api=None):
        config = current_app.config["LOGIN_FACTORY"]
        self.view = LoginView(**config)
        super().__init__()

    @ns_auth.expect(login_model, validate=False)
    @ns_auth.response(200, "Token généré avec succès")
    @ns_auth.response(401, "Identifiants invalides")
    def post(self):
        params = request.get_json()
        for key in ["identifier", "type", "password"]:
            if key not in params:
                raise BadRequest(f"Champ requis manquant : {key}")
        data = self.view.post(params)
        return jsonify(
            {
                "status": 200,
                "type": "response",
                "data": {
                    "token": data["token"],
                    "expire-at": data["expire_at"],
                    "duration": data["duration"],
                },
            }
        )
