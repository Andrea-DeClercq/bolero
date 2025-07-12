#!/usr/bin/env python
"""
Module de gestion des éditeurs.
"""

# Import from local code
from bolero.server.modules.bolero._common import EditorsResource
from core.server.views import req, fields
from core.server.documentation.models import (
    ns_editors,
    create_response,
    editor_model,
)
from core.server.documentation.parsers import (
    editor_get_parser,
    editor_post_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_editors.route("/editeurs")
class Editors(EditorsResource):
    @ns_editors.expect(editor_get_parser())
    @ns_editors.response(
        200, "Liste des éditeurs récupérés avec succès", [editor_model]
    )
    @ns_editors.doc(
        description=(
            "Récupère la liste des éditeurs en fonction d’un filtre facultatif sur le nom.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /editeurs?nom=PUF&page=1&limit=20`\n\n"
            "**Remarques :**\n"
            "- Le champ `nom` permet une recherche insensible à la casse.\n"
            "- La réponse est paginée avec les champs `page`, `limit`, `total`, `pages`.\n"
            "- Si aucun résultat, le champ `items` est une liste vide."
        )
    )
    @req(
        {
            "nom": fields.String(required=False),
            "page": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Récupère la liste des éditeurs avec pagination et recherche optionnelle par nom."""
        return self._get(params)

    @ns_editors.response(201, "Éditeur créé avec succès", create_response(ns_editors))
    @ns_editors.response(409, "Un éditeur avec ce nom existe déjà")
    @ns_editors.response(422, "Champs manquants ou invalides")
    @ns_editors.expect(editor_post_parser())
    @ns_editors.doc(
        description=(
            "Ajoute un nouvel éditeur à la base de données Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec :\n"
            "- `nom` (obligatoire)\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`.\n"
            "- Un éditeur déjà existant ne peut pas être recréé."
        )
    )
    def post(self):
        """Ajoute un nouvel éditeur à la base de données Boléro."""
        return self._post()
