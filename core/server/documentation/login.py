# #!/usr/bin/env python
# """
# Module de gestion de l'authentification.
# """
# # Import from stdlib

# # Imports from external libraries

# # Import from local code
# from core.server.documentation.models import ns_login, login_model
# from core.server.modules.auth import LoginView


# # Définir la ressource pour la route
# @ns_login.route("/login")
# class LoginResource(LoginView):
#     """
#     Ressource d'authentification exposée à Swagger.

#     Cette classe hérite de `LoginView` et permet d'obtenir un token JWT
#     via une requête POST avec un identifiant et un mot de passe.
#     """

#     @ns_login.expect(login_model, validate=True)
#     @ns_login.doc(
#         description=(
#             "Permet d'obtenir un token pour l'authentification des requêtes POST, PUT et DELETE.\n\n"
#             "Un token a une durée de vie de 1 heure et peut être prolongé jusqu'à 7 jours si `remember_me` est défini à **True**.\n\n"
#             "Cette méthode nécessite un identifiant et un mot de passe valides."
#         )
#     )
#     def post(self):
#         """
#         Authentifie un utilisateur et génère un token JWT.
#         """
#         return super().post()
