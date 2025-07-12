#!/usr/bin/env python
"""
Module de gestion des relations entre les auteurs, ouvrages et recensions.
"""

# Import from stdlib

# Imports from external libraries

# Import from local code
from bolero.server.modules.bolero._common import RelationResource
from core.server.documentation.models import (
    ns_relations,
    relation_auteur_ouvrage,
    relation_auteur_recension,
    relation_ouvrage_recension,
    create_response,
    relation_batch_model,
    relation_delete_batch_model,
)
from core.server.documentation.parsers import (
    relation_post_parser,
    author_book_get_parser,
    author_review_get_parser,
    book_review_get_parser,
    author_book_put_parser,
    author_review_put_parser,
    book_review_put_parser,
)

####################################################################################################
# Routes
####################################################################################################


@ns_relations.route("/relations")
class Relations(RelationResource):

    @ns_relations.expect(relation_post_parser())
    @ns_relations.response(
        201, "Relation créée avec succès", create_response(ns_relations)
    )
    @ns_relations.response(409, "La relation existe déjà")
    @ns_relations.response(422, "Champs manquants ou invalides")
    @ns_relations.doc(
        description=(
            "Cette route permet de créer une relation entre deux entités.\n\n"
            "**Remarques :**\n"
            "- `id_auteur` et `id_ouvrage` permettent de créer une relation Auteur-Ouvrage.\n"
            "- `id_auteur` et `id_recension` permettent de créer une relation Auteur-Recension.\n"
            "- `id_ouvrage` et `id_recension` permettent de créer une relation Ouvrage-Recension."
        )
    )
    def post(self):
        """Permet de créer une relation entre deux objets."""
        return self._add_relation()


####################################################################################################
# POST MULTIPLES
####################################################################################################


@ns_relations.route("/relations/batch")
class RelationBatchResource(RelationResource):
    @ns_relations.expect(relation_batch_model)
    @ns_relations.response(201, "Relations créées avec succès")
    @ns_relations.response(207, "Certaines relations n'ont pas pu être créées")
    @ns_relations.response(400, "Requête invalide")
    def post(self):
        """
        Crée plusieurs relations entre auteurs, ouvrages et recensions.
        """
        return self.post_batch()


####################################################################################################
# RELATIONS AUTEUR OUVRAGE
####################################################################################################


@ns_relations.route("/relations/auteurs-ouvrages")
class RelationsAuteurOuvrageList(RelationResource):
    @ns_relations.expect(author_book_get_parser())
    @ns_relations.response(
        200,
        "Liste des relations Auteur-Ouvrage récupérée avec succès",
        [relation_auteur_ouvrage],
    )
    @ns_relations.doc(
        description=(
            "Permet de récupérer la liste des relations entre les auteurs et les ouvrages."
        )
    )
    def get(self):
        """Permet de récupérer la liste des relations Auteur-Ouvrage"""
        return self._get_relation()


@ns_relations.route("/relations/auteurs-ouvrages/<int:id>")
@ns_relations.param("id", "Identifiant unique de la relation Auteur-Ouvrage")
class RelationsAuteurOuvrage(RelationResource):
    @ns_relations.response(
        200, "Relation Auteur-Ouvrage récupérée avec succès", [relation_auteur_ouvrage]
    )
    @ns_relations.doc(
        description="Permet de récupérer le détail d’une relation entre un auteur et un ouvrage."
    )
    def get(self, id):
        """Permet de récupérer le détail d'une relation Auteur-Ouvrage"""
        return self._get_relation(id)

    @ns_relations.expect(author_book_put_parser())
    @ns_relations.response(
        200, "Relation mise à jour avec succès", create_response(ns_relations)
    )
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Met à jour une relation Auteur-Ouvrage existante dans la base Boléro.\n\n"
            "**Remarques :**\n"
            "- La mise à jour est partielle : les champs non renseignés ne seront pas modifiés.\n"
            "- Cette route accepte uniquement des requêtes en `multipart/form-data`."
        )
    )
    def put(self, id):
        """Permet la mise à jour d'une relation Auteur-Ouvrage"""
        return self._put_relation(id)

    @ns_relations.response(204, "Relation supprimée avec succès")
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Supprime une relation auteur-ouvrage existante dans la base Boléro."
        )
    )
    def delete(self, id):
        """Permet la suppression d'une relation Auteur-Ouvrage"""
        return self._delete_relation(id)


####################################################################################################
# RELATIONS AUTEUR RECENSION
####################################################################################################


@ns_relations.route("/relations/auteurs-recensions")
class RelationsAuteurRecensionList(RelationResource):
    @ns_relations.expect(author_review_get_parser())
    @ns_relations.response(
        200,
        "Liste des relations Auteur-Recension récupérée avec succès",
        [relation_auteur_recension],
    )
    @ns_relations.doc(
        description=(
            "Permet de récupérer la liste des relations entre les auteurs et les recensions.\n"
        )
    )
    def get(self):
        """Permet de récupérer la liste des relations Auteur-Recension"""
        return self._get_relation()


@ns_relations.route("/relations/auteurs-recensions/<int:id>")
@ns_relations.param("id", "Identifiant unique de la relation Ouvrage-Recension")
class RelationsAuteurRecension(RelationResource):
    @ns_relations.response(
        200,
        "Relation Auteur-Recension récupérée avec succès",
        [relation_auteur_recension],
    )
    @ns_relations.doc(
        description=(
            "Permet de récupérer le détail d'une relation entre un auteur et une recension.\n"
        )
    )
    def get(self, id):
        """Permet de récupérer le détail d'une relation Auteur-Recension"""
        return self._get_relation(id)

    @ns_relations.expect(author_review_put_parser())
    @ns_relations.response(
        200, "Relation mise à jour avec succès", create_response(ns_relations)
    )
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Met à jour la relation auteur-recension existante dans la base Boléro.\n\n"
            "**Remarques :**\n"
            "- L'enregistrement se fait partiellement, si le champ est vide, il ne sera pas modifié.\n"
            "- Cette route accepte uniquement des données multipart/form-data."
        )
    )
    def put(self, id):
        """Permet la mise à jour d'une relation Auteur-Recension"""
        return self._put_relation(id)

    @ns_relations.response(204, "Relation supprimée avec succès")
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Supprime la relation auteur-recension existante dans la base Boléro.\n\n"
        )
    )
    def delete(self, id):
        """Permet la suppression d'une relation Auteur-Recension"""
        return self._delete_relation(id)


####################################################################################################
# RELATIONS OUVRAGE RECENSION
####################################################################################################


@ns_relations.route("/relations/ouvrages-recensions")
class RelationsOuvrageRecensionList(RelationResource):
    @ns_relations.expect(book_review_get_parser())
    @ns_relations.response(
        200,
        "Liste des relations Ouvrage-Recension récupérée avec succès",
        [relation_ouvrage_recension],
    )
    @ns_relations.doc(
        description=(
            "Permet de récupérer la liste des relations entre les ouvrages et les recensions.\n"
        )
    )
    def get(self):
        """Permet de récupérer la liste des relations Ouvrage-Recension"""
        return self._get_relation()


@ns_relations.route("/relations/ouvrages-recensions/<int:id>")
@ns_relations.param("id", "Identifiant unique de la relation Ouvrage-Recension")
class RelationsOuvrageRecension(RelationResource):
    @ns_relations.response(
        200,
        "Relation Ouvrage-Recension récupérée avec succès",
        [relation_ouvrage_recension],
    )
    @ns_relations.doc(
        description=(
            "Permet de récupérer le détail d'une relation entre un ouvrage et une recension.\n"
        )
    )
    def get(self, id):
        """Permet de récupérer le détail d'une relation Ouvrage-Recension"""
        return self._get_relation(id)

    @ns_relations.expect(book_review_put_parser())
    @ns_relations.response(
        200, "Relation mise à jour avec succès", create_response(ns_relations)
    )
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Met à jour la relation ouvrage-recension existante dans la base Boléro.\n\n"
            "**Remarques :**\n"
            "- L'enregistrement se fait partiellement, si le champ est vide, il ne sera pas modifié.\n"
            "- Cette route accepte uniquement des données multipart/form-data."
        )
    )
    def put(self, id):
        """Permet la mise à jour d'une relation Ouvrage-Recension"""
        return self._put_relation(id)

    @ns_relations.response(204, "Relation supprimée avec succès")
    @ns_relations.response(404, "Relation non trouvée")
    @ns_relations.doc(
        description=(
            "Supprime la relation ouvrage-recension existante dans la base Boléro.\n\n"
        )
    )
    def delete(self, id):
        """Permet la suppression d'une relation Ouvrage-Recension"""
        return self._delete_relation(id)


####################################################################################################
# DELETE MULTIPLES PAR RELATION
####################################################################################################
@ns_relations.route("/relations/auteurs-ouvrages/batch")
class RelationsAuteurOuvrageBatchDelete(RelationResource):
    @ns_relations.expect(relation_delete_batch_model)
    @ns_relations.response(200, "Relations supprimées avec succès")
    @ns_relations.response(404, "Aucune relation supprimée")
    @ns_relations.response(400, "Requête invalide")
    @ns_relations.doc(
        description="Supprime plusieurs relations Auteur-Ouvrage via une liste d'identifiants."
    )
    def delete(self):
        """Suppression batch des relations Auteur-Ouvrage"""
        return self.delete_batch()


@ns_relations.route("/relations/auteurs-recensions/batch")
class RelationsAuteurRecensionBatchDelete(RelationResource):
    @ns_relations.expect(relation_delete_batch_model)
    @ns_relations.response(200, "Relations supprimées avec succès")
    @ns_relations.response(404, "Aucune relation supprimée")
    @ns_relations.response(400, "Requête invalide")
    @ns_relations.doc(
        description="Supprime plusieurs relations Auteur-Recension via une liste d'identifiants."
    )
    def delete(self):
        """Suppression batch des relations Auteur-Recension"""
        return self.delete_batch()


@ns_relations.route("/relations/ouvrages-recensions/batch")
class RelationsOuvrageRecensionBatchDelete(RelationResource):
    @ns_relations.expect(relation_delete_batch_model)
    @ns_relations.response(200, "Relations supprimées avec succès")
    @ns_relations.response(404, "Aucune relation supprimée")
    @ns_relations.response(400, "Requête invalide")
    @ns_relations.doc(
        description="Supprime plusieurs relations Ouvrage-Recension via une liste d'identifiants."
    )
    def delete(self):
        """Suppression batch des relations Ouvrage-Recension"""
        return self.delete_batch()
