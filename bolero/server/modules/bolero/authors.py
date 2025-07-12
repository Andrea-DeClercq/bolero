#!/usr/bin/env python
"""
Module de gestion des auteurs.
"""

# Import from stdlib

# Imports from external libraries

# Import from local code
from bolero.server.modules.bolero._common import AuthorsResource
from core.server.views import req, fields
from core.server.documentation.models import (
    ns_authors,
    create_response,
    author_model,
)
from core.server.documentation.parsers import (
    author_get_parser,
    author_post_parser,
    author_put_parser,
    author_export_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_authors.route("/auteurs")
class Authors(AuthorsResource):
    @ns_authors.expect(author_get_parser())
    @ns_authors.response(200, "Liste des auteurs récupérés avec succès", [author_model])
    @ns_authors.doc(
        description=(
            "Récupère la liste des auteurs en fonction des critères de recherche spécifiés.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /auteurs?id=1&nom=Dupont`\n\n"
            "**Remarques :**\n"
            "- Tous les paramètres sont facultatifs.\n"
            "- Le paramètre `limit` définit le nombre maximal de résultats.\n"
            "- Si un auteur n’a aucune relation, il apparaîtra avec des listes vides.\n"
            "- En cas de non résultats, la requête renvoie une liste vide."
        ),
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "id_ref": fields.String(required=False),
            "nom": fields.String(required=False),
            "prenom": fields.String(required=False),
            "limit": fields.Integer(required=False),
            "page": fields.Integer(required=False),
            "sort": fields.String(required=False),
            "order": fields.String(required=False),
            "id_proprio": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Récupère la liste des auteurs à l’aide de filtres optionnels."""
        return self._get(params)

    @ns_authors.response(201, "Auteur créé avec succès", create_response(ns_authors))
    @ns_authors.response(409, "L'auteur existe déjà")
    @ns_authors.response(422, "Champs manquants ou invalides")
    @ns_authors.expect(author_post_parser())
    @ns_authors.doc(
        description=(
            "Ajoute un nouvel auteur à la base de données Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec les champs suivants :\n"
            "- `nom` (obligatoire)\n"
            "- `prenom` (obligatoire)\n"
            "- `id_ref` (optionnel)\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def post(self):
        """Ajoute un nouvel auteur à la base de données Boléro."""
        return self._post()


@ns_authors.route("/auteurs/by-proprio/<string:id_proprio>")
@ns_authors.param(
    "id_proprio", "Identifiant propriétaire unique de l'auteur", _in="path"
)
class AuthorByIdProprio(AuthorsResource):
    @ns_authors.response(200, "Détails de l’auteur récupérés avec succès", author_model)
    @ns_authors.response(404, "Auteur non trouvé")
    @ns_authors.doc(
        description=(
            "Récupère les détails d’un auteur à partir de son identifiant propriétaire unique dans la base Boléro.\n\n"
        ),
    )
    def get(self, id_proprio):
        """Récupère les détails d’un auteur à partir de son identifiant propriétaire unique."""
        return self._get_author_by_proprio_id(id_proprio)


@ns_authors.route("/auteurs/<int:id>")
@ns_authors.param("id", "Identifiant unique de l'auteur", _in="path")
class Author(AuthorsResource):
    @ns_authors.response(200, "Détails de l’auteur récupérés avec succès", author_model)
    @ns_authors.response(404, "Auteur non trouvé")
    @ns_authors.doc(
        description=(
            "Récupère les détails d’un auteur à partir de son identifiant unique dans la base Boléro.\n\n"
        ),
    )
    def get(self, id):
        """Récupère les détails d’un auteur à partir de son identifiant unique."""
        return self._get_author_by_id(id)

    @ns_authors.response(
        200,
        "Auteur mis à jour avec succès",
        create_response(ns_authors),
    )
    @ns_authors.response(404, "Auteur non trouvé")
    @ns_authors.response(400, "Champs manquants ou invalides")
    @ns_authors.expect(author_put_parser())
    @ns_authors.doc(
        description=(
            "Met à jour les informations d’un auteur existant dans la base Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec l’un des champs suivants :\n"
            "- `nom`, `prenom` ou `id_ref` (optionnels)\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def put(self, id):
        """Met à jour les informations d’un auteur, partiellement ou intégralement."""
        return self._put(id)

    @ns_authors.response(204, "Auteur supprimé avec succès")
    @ns_authors.response(404, "Auteur non trouvé")
    @ns_authors.doc(
        description=(
            "Supprime définitivement un auteur existant dans la base Boléro.\n\n"
        )
    )
    def delete(self, id):
        """Supprime définitivement un auteur de la base de données Boléro."""
        return self._delete(id)


@ns_authors.route("/auteurs/export")
class AuthorsExport(AuthorsResource):
    @ns_authors.expect(author_export_parser())
    @ns_authors.produces(["text/csv"])
    @ns_authors.response(200, "Fichier CSV généré avec succès (Content-Type: text/csv)")
    @ns_authors.doc(
        description=(
            "Exporte les auteurs correspondant aux filtres fournis au format CSV.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /auteurs/export?nom=Durand`\n\n"
            "**Remarques :**\n"
            "- Tous les filtres de recherche classiques sont disponibles.\n"
            "- La réponse est un fichier `.csv` directement téléchargeable."
        )
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "id_ref": fields.String(required=False),
            "nom": fields.String(required=False),
            "prenom": fields.String(required=False),
            "id_proprio": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Exporte les auteurs filtrés au format CSV."""
        return self._export_csv(params)
