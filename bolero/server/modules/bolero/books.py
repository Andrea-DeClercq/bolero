#!/usr/bin/env python
"""
Module de gestion des ouvrages.
"""

# Import from stdlib

# Imports from external libraries

# Import from local code
from bolero.server.modules.bolero._common import BooksResource
from core.server.views import req, fields
from core.server.documentation.models import (
    ns_books,
    book_model,
    create_response,
)
from core.server.documentation.parsers import (
    book_get_parser,
    book_post_parser,
    book_put_parser,
    book_export_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_books.route("/ouvrages")
class Books(BooksResource):
    @ns_books.expect(book_get_parser())
    @ns_books.response(200, "Liste des ouvrages récupérés avec succès", [book_model])
    @ns_books.response(404, "Aucun ouvrage trouvé")
    @ns_books.doc(
        description=(
            "Récupère la liste des ouvrages en fonction des critères de recherche spécifiés.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /ouvrages?titre=Exemple&annee_parution=2020`\n\n"
            "**Remarques :**\n"
            "- Tous les paramètres sont facultatifs.\n"
            "- Le paramètre `limit` définit le nombre maximal de résultats.\n"
            "- Si un ouvrage n’a aucune relation, il apparaîtra avec des listes vides."
        )
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "titre": fields.String(required=False),
            "sous_titre": fields.String(required=False),
            "volume": fields.String(required=False),
            "annee_parution": fields.String(required=False),
            "editeur": fields.String(required=False),
            "ean": fields.String(required=False),
            "portail": fields.String(required=False),
            "auteur_nom": fields.String(required=False),
            "auteur_prenom": fields.String(required=False),
            "id_auteur": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
            "page": fields.Integer(required=False),
            "sort": fields.String(required=False),
            "order": fields.String(required=False),
            "id_proprio": fields.String(required=False),
            "traduit_par": fields.String(required=False),
            "langue": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Récupère la liste des ouvrages à l’aide de filtres optionnels."""
        return self._get(params)

    @ns_books.expect(book_post_parser())
    @ns_books.response(201, "Ouvrage créé avec succès", create_response(ns_books))
    @ns_books.response(409, "L'ouvrage existe déjà")
    @ns_books.response(422, "Champs manquants ou invalides")
    @ns_books.doc(
        description=(
            "Ajoute un nouvel ouvrage à la base de données Boléro.\n\n"
            "**Exemple d'utilisation :**\n"
            "Envoyez un formulaire avec les champs obligatoires suivants :\n"
            "- `titre`, `annee_parution`, `editeur`, `ean`\n\n"
            "**Remarque :**\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def post(self):
        """Ajoute un nouvel ouvrage à la base de données Boléro."""
        return self._post()


@ns_books.route("/ouvrages/by-proprio/<string:id_proprio>")
@ns_books.param(
    "id_proprio", "Identifiant propriétaire unique de l'ouvrage", _in="path"
)
class BookByIdProprio(BooksResource):
    @ns_books.response(200, "Détails de l’ouvrage récupérés avec succès", book_model)
    @ns_books.response(404, "Ouvrage non trouvé")
    @ns_books.doc(
        description=(
            "Récupère les détails d’un ouvrage à partir de son identifiant unique dans la base Boléro.\n\n"
        ),
    )
    def get(self, id_proprio):
        """Récupère les détails d’un ouvrage à partir de son identifiant propriétaire unique."""
        return self._get_book_by_id_proprio(id_proprio)


@ns_books.route("/ouvrages/by-ean/<string:ean>")
@ns_books.param("ean", "EAN de l'ouvrage", _in="path")
class BookByIdProprio(BooksResource):
    @ns_books.response(200, "Détails de l’ouvrage récupérés avec succès", book_model)
    @ns_books.response(404, "Ouvrage non trouvé")
    @ns_books.doc(
        description=(
            "Récupère les détails d’un ouvrage à partir de son EAN dans la base Boléro.\n\n"
        ),
    )
    def get(self, ean):
        """Récupère les détails d’un ouvrage à partir de son EAN."""
        return self._get_book_by_ean(ean)


@ns_books.route("/ouvrages/<int:id>")
@ns_books.param("id", "Identifiant unique de l'ouvrage", _in="path")
class Book(BooksResource):
    @ns_books.response(200, "Détails de l’ouvrage récupérés avec succès", book_model)
    @ns_books.response(404, "Ouvrage non trouvé")
    @ns_books.doc(
        description=(
            "Récupère les détails d’un ouvrage à partir de son identifiant unique dans la base Boléro.\n\n"
        ),
    )
    def get(self, id):
        """Récupère les détails d’un ouvrage à partir de son identifiant unique."""
        return self._get_book_by_id(id)

    @ns_books.response(200, "Ouvrage mis à jour avec succès", create_response(ns_books))
    @ns_books.response(404, "Ouvrage non trouvé")
    @ns_books.response(400, "Champs manquants ou invalides")
    @ns_books.expect(book_put_parser())
    @ns_books.doc(
        description=(
            "Met à jour les informations d’un ouvrage existant dans la base Boléro.\n\n"
            "**Remarque :**\n"
            "- La mise à jour est partielle : les champs laissés vides ne seront pas modifiés.\n"
            "- Cette route accepte uniquement les requêtes au format `multipart/form-data`."
        )
    )
    def put(self, id):
        """Met à jour les informations d’un ouvrage, partiellement ou intégralement."""
        return self._put(id)

    @ns_books.response(204, "Ouvrage supprimé avec succès")
    @ns_books.response(404, "Ouvrage non trouvé")
    @ns_books.doc(
        description=("Supprime définitivement un ouvrage existant dans la base Boléro.")
    )
    def delete(self, id):
        """Supprime définitivement un ouvrage de la base de données Boléro."""
        return self._delete(id)


@ns_books.route("/ouvrages/export")
class BooksExport(BooksResource):
    @ns_books.expect(book_export_parser())
    @ns_books.produces(["text/csv"])
    @ns_books.response(200, "Fichier CSV généré avec succès (Content-Type: text/csv)")
    @ns_books.doc(
        description=(
            "Exporte les ouvrages au format CSV selon les critères de recherche spécifiés.\n\n"
            "**Exemple d'utilisation :**\n"
            "`GET /ouvrages/export?titre=philosophie&auteur_nom=Descartes`\n\n"
            "**Contenu exporté :**\n"
            "- Toutes les colonnes de la table `ouvrage`, sauf `cree_le` et `modifie_le`.\n"
            "- Les auteurs associés à chaque ouvrage (concaténés dans une colonne `auteurs`).\n"
            "- Le nombre total de recensions associées à chaque ouvrage (colonne `nb_recensions`).\n\n"
            "**Remarques :**\n"
            "- Le fichier est retourné au format CSV, avec `;` comme séparateur.\n"
            "- Les champs texte sont automatiquement encadrés de guillemets.\n"
            "- Plusieurs auteurs sont séparés par `;` dans une seule cellule.\n"
            "- Tous les paramètres de recherche classiques sont disponibles, y compris ceux liés aux auteurs.\n"
            "- Le fichier CSV est directement téléchargeable via le navigateur ou un outil de requêtage."
        )
    )
    @req(
        {
            "id": fields.Integer(required=False),
            "titre": fields.String(required=False),
            "sous_titre": fields.String(required=False),
            "volume": fields.String(required=False),
            "annee_parution": fields.String(required=False),
            "editeur": fields.String(required=False),
            "ean": fields.String(required=False),
            "portail": fields.String(required=False),
            "auteur_nom": fields.String(required=False),
            "auteur_prenom": fields.String(required=False),
            "id_auteur": fields.Integer(required=False),
            "limit": fields.Integer(required=False),
            "page": fields.Integer(required=False),
            "sort": fields.String(required=False),
            "order": fields.String(required=False),
            "id_proprio": fields.String(required=False),
            "traduit_par": fields.String(required=False),
            "langue": fields.String(required=False),
        },
        source="args",
    )
    def get(self, params):
        """Exporte les ouvrages filtrés au format CSV."""
        return self._export_csv(params)
