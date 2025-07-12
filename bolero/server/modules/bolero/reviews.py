#!/usr/bin/env python
"""
Module de gestion des recensions.
"""

# Import from stdlib

# Imports from external libraries

# Import from local code
from bolero.server.modules.bolero._common import ReviewsResource
from core.server.views import req, fields
from core.server.documentation.models import (
    ns_reviews,
    review_model,
    create_response,
)
from core.server.documentation.parsers import (
    review_get_parser,
    review_post_parser,
    review_put_parser,
    review_export_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_reviews.route("/recensions")
class Reviews(ReviewsResource):
    @ns_reviews.expect(review_get_parser())
    @ns_reviews.response(
        200, "Liste des recensions récupérées avec succès", [review_model]
    )
    @ns_reviews.response(404, "Aucune recension trouvée")
    @ns_reviews.doc(
        description=(
            "Récupère la liste des recensions en fonction des critères de recherche spécifiés.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /recensions?titre=Exemple&annee=2022`\n\n"
            "**Remarques :**\n"
            "- Tous les paramètres sont facultatifs.\n"
            "- Le paramètre `limit` définit le nombre maximal de résultats.\n"
            "- Si une recension n’a aucune relation, elle apparaîtra avec des listes vides."
        )
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "titre": fields.String(required=False),
            "sous_titre": fields.String(required=False),
            "portail": fields.String(required=False),
            "titre_revue": fields.String(required=False),
            "annee": fields.String(required=False),
            "volume": fields.String(required=False),
            "numero": fields.String(required=False),
            "date_parution": fields.String(required=False),
            "url": fields.String(required=False),
            "auteur_nom": fields.String(required=False),
            "auteur_prenom": fields.String(required=False),
            "id_auteur": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
            "page": fields.Integer(required=False),
            "sort": fields.String(required=False),
            "order": fields.String(required=False),
            "id_proprio": fields.String(required=False),
            "traducteur": fields.String(required=False),
            "langue": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Récupère la liste des recensions à l’aide de filtres optionnels."""
        return self._get(params)

    @ns_reviews.expect(review_post_parser())
    @ns_reviews.response(
        201, "Recension créée avec succès", create_response(ns_reviews)
    )
    @ns_reviews.response(409, "La recension existe déjà")
    @ns_reviews.response(422, "Champs manquants ou invalides")
    @ns_reviews.doc(
        description=(
            "Ajoute une nouvelle recension à la base de données Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec les champs obligatoires suivants :\n"
            "- `titre`, `annee`, `titre_revue`, `url`\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def post(self):
        """Ajoute une nouvelle recension à la base de données Boléro."""
        return self._post()


@ns_reviews.route("/recensions/by-proprio/<string:id_proprio>")
@ns_reviews.param(
    "id_proprio", "Identifiant propriétaire unique de la recension", _in="path"
)
class ReviewByIdProprio(ReviewsResource):
    @ns_reviews.response(
        200, "Détails de la recension récupérés avec succès", review_model
    )
    @ns_reviews.response(404, "Recension non trouvée")
    @ns_reviews.doc(
        description=(
            "Récupère les détails d’une recension à partir de son identifiant propriétaire unique dans la base Boléro."
        )
    )
    def get(self, id_proprio):
        """Récupère les détails d’une recension à partir de son identifiant propriétaire unique."""
        return self._get_review_by_id_proprio(id_proprio)


@ns_reviews.route("/recensions/<int:id>")
@ns_reviews.param("id", "Identifiant unique de la recension", _in="path")
class Review(ReviewsResource):
    @ns_reviews.response(
        200, "Détails de la recension récupérés avec succès", review_model
    )
    @ns_reviews.response(404, "Recension non trouvée")
    @ns_reviews.doc(
        description=(
            "Récupère les détails d’une recension à partir de son identifiant unique dans la base Boléro."
        )
    )
    def get(self, id):
        """Récupère les détails d’une recension à partir de son identifiant unique."""
        return self._get_review_by_id(id)

    @ns_reviews.response(
        200, "Recension mise à jour avec succès", create_response(ns_reviews)
    )
    @ns_reviews.response(404, "Recension non trouvée")
    @ns_reviews.response(400, "Champs manquants ou invalides")
    @ns_reviews.expect(review_put_parser())
    @ns_reviews.doc(
        description=(
            "Met à jour les informations d’une recension existante dans la base Boléro.\n\n"
            "**Remarque :**\n"
            "- La mise à jour est partielle : les champs laissés vides ne seront pas modifiés.\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def put(self, id):
        """Permet de mettre à jour les données d'une recension de manière complète ou partielle."""
        return self._put(id)

    @ns_reviews.response(204, "Recension supprimée avec succès")
    @ns_reviews.response(404, "Recension non trouvée")
    @ns_reviews.doc(
        description=(
            "Supprime définitivement une recension existante dans la base Boléro."
        )
    )
    def delete(self, id):
        """Permet de supprimer les données d'une recension"""
        return self._delete(id)


@ns_reviews.route("/recensions/export")
class ReviewsExport(ReviewsResource):
    @ns_reviews.expect(review_export_parser())
    @ns_reviews.produces(["text/csv"])
    @ns_reviews.response(200, "Fichier CSV généré avec succès (Content-Type: text/csv)")
    @ns_reviews.doc(
        description=(
            "Exporte les recensions au format CSV selon les critères de recherche spécifiés.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /recensions/export?titre=violence&annee=2023`\n\n"
            "**Contenu exporté :**\n"
            "- Toutes les colonnes de la table `recension`, sauf `cree_le` et `modifie_le`.\n"
            "- Les auteurs associés à chaque recension.\n"
            "- Les métadonnées obligatoires de chaque ouvrage lié (`titre`, `année`, `éditeur`).\n"
            "- Les auteurs associés à chaque ouvrage.\n\n"
            "**Remarques :**\n"
            "- Le fichier est retourné au format CSV, avec `;` comme séparateur.\n"
            "- Les champs texte sont encadrés de guillemets pour éviter les erreurs de format.\n"
            "- Plusieurs auteurs ou ouvrages sont séparés par `;` ou `|` selon le contexte.\n"
            "- Le paramètre `date_parution` accepte le format `YYYY-MM-DD` mais ne filtre que par année."
        )
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "titre": fields.String(required=False),
            "sous_titre": fields.String(required=False),
            "portail": fields.String(required=False),
            "titre_revue": fields.String(required=False),
            "annee": fields.String(required=False),
            "volume": fields.String(required=False),
            "numero": fields.String(required=False),
            "date_parution": fields.String(required=False),
            "url": fields.String(required=False),
            "auteur_nom": fields.String(required=False),
            "auteur_prenom": fields.String(required=False),
            "id_auteur": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
            "page": fields.Integer(required=False),
            "sort": fields.String(required=False),
            "order": fields.String(required=False),
            "id_proprio": fields.String(required=False),
            "traducteur": fields.String(required=False),
            "langue": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Exporte les rencensions filtrées au format CSV."""
        return self._export_csv(params)
