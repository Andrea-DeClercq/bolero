#!/usr/bin/env python
"""
Module de gestion des revues.
"""

# Import from local code
from bolero.server.modules.bolero._common import JournalResource
from core.server.views import req, fields
from core.server.documentation.models import (
    ns_journals,
    create_response,
    journal_model,
)
from core.server.documentation.parsers import (
    journal_get_parser,
    journal_post_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_journals.route("/revues")
class Journals(JournalResource):
    @ns_journals.expect(journal_get_parser())
    @ns_journals.response(
        200, "Liste des revues récupérés avec succès", [journal_model]
    )
    @ns_journals.doc(
        description=(
            "Récupère la liste des revues en fonction d’un filtre facultatif sur le titre.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /revues?titre=PUF&page=1&limit=20`\n\n"
            "**Remarques :**\n"
            "- Le champ `titre` permet une recherche insensible à la casse.\n"
            "- La réponse est paginée avec les champs `page`, `limit`, `total`, `pages`.\n"
            "- Si aucun résultat, le champ `items` est une liste vide."
        )
    )
    @req(
        {
            "titre": fields.String(required=False),
            "page": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Récupère la liste des revues avec pagination et recherche optionnelle par titre."""
        return self._get(params)

    @ns_journals.response(201, "Revue créé avec succès", create_response(ns_journals))
    @ns_journals.response(409, "Un revue avec ce titre existe déjà")
    @ns_journals.response(422, "Champs manquants ou invalides")
    @ns_journals.expect(journal_post_parser())
    @ns_journals.doc(
        description=(
            "Ajoute une nouvelle revue à la base de données Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec :\n"
            "- `titre` (obligatoire)\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`.\n"
            "- Un éditeur déjà existant ne peut pas être recréé."
        )
    )
    def post(self):
        """Ajoute une nouvelle revue à la base de données Boléro."""
        return self._post()
