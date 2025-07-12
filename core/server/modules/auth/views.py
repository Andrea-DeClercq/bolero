from datetime import datetime
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import undefer
from werkzeug.exceptions import Unauthorized


class LoginView:
    def __init__(self, factory_user_model, delta_not_remember_me, delta_remember_me):
        self.UserModel = factory_user_model()
        self.delta_not_remember_me = delta_not_remember_me
        self.delta_remember_me = delta_remember_me

    def _get_user(self, identifier, type_of_identifier):
        query = self.UserModel.options(undefer("password"))
        query = query.filter_by(**{type_of_identifier: identifier})
        return query.first()

    def _generate_token(self, user, remember_me):
        expire_delta = (
            self.delta_remember_me if remember_me else self.delta_not_remember_me
        )
        now = datetime.utcnow()
        token = create_access_token(
            identity={"id": user.id, "id_portail": user.id_portail},
            expires_delta=expire_delta,
        )
        return {
            "token": token,
            "expire_at": now + expire_delta,
            "duration": ((now + expire_delta) - now).total_seconds(),
        }

    def post(self, params):
        user = self._get_user(params["identifier"], params["type"])
        if not user:
            raise Unauthorized("Identifiant non trouvé")
        if not user.check_password(params["password"]):
            raise Unauthorized("Mot de passe incorrect")
        return self._generate_token(user, params.get("remember_me", False))
