#!/usr/bin/env python
"""
Module de définition des modèles pour Swagger.
"""
# Import from stdlib

# Imports from external libraries
from flask_restx import Namespace, fields

# Import from local code

####################################################################################################
# Fonction création model des relations
####################################################################################################


# TODO: Placer les modèles de réponse dans la réponse de base, personnalisé le message model lorsqu'il s'agit des objets


def create_response(ns):
    return ns.model("CreateResponse", {"message": fields.String, "id": fields.Integer})


def create_model_relation_auteur(ns_name, name):
    return ns_name.model(
        name,
        {
            "id": fields.Integer(description="ID unique de l'auteur"),
            "nom": fields.String(description="Nom de famille de l'auteur"),
            "prenom": fields.String(description="Prénom de l'auteur"),
            "id_ref": fields.String(description="ID Ref de l'auteur"),
        },
    )


def create_model_relation_ouvrage(ns_name, name):
    return ns_name.model(
        name,
        {
            "id": fields.Integer(description="ID de l'ouvrage"),
            "id_proprio": fields.String(
                description="ID du portail propriétaire de l'ouvrage"
            ),
            "titre": fields.String(description="Titre de l'ouvrage"),
            "annee_parution": fields.String(
                description="Année de parution de l'ouvrage"
            ),
            "editeur": fields.String(description="Éditeur de l'ouvrage"),
            "ean": fields.String(description="EAN de l'ouvrage"),
            "doi": fields.String(description="DOI de l'ouvrage"),
            "url": fields.String(description="URL de l'ouvrage"),
            "portail": fields.String(description="Portail de l'ouvrage"),
            "langue": fields.String(description="Langue de l'ouvrage"),
        },
    )


def create_model_relation_recension(ns_name, name):
    return ns_name.model(
        name,
        {
            "id": fields.Integer(description="ID de la recension"),
            "id_proprio": fields.String(
                description="ID portail propriétaire de la recension"
            ),
            "titre": fields.String(description="Titre de la recension"),
            "titre_revue": fields.String(description="Titre de la revue"),
            "annee": fields.String(description="Année de la revue"),
            "volume": fields.String(description="Volume de la recension"),
            "numero": fields.String(description="Numéro de la recension"),
            "url": fields.String(description="URL de la recension"),
            "portail": fields.String(description="Portail de la recension"),
            "date_parution": fields.String(
                description="Date de parution de la recension"
            ),
            "langue": fields.String(description="Langue de la recension"),
        },
    )


####################################################################################################
# Model & Namespace Éditeurs
####################################################################################################

ns_editors = Namespace(
    "Éditeurs",
    description="Ce module gère les éditeurs disponibles pour les ouvrages.",
    path="/bolero",
)

editor_model = ns_editors.model(
    "editeur",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de l'éditeur"),
        "nom": fields.String(required=True, description="Nom de l'éditeur"),
    },
)

####################################################################################################
# Model & Namespace Revue
####################################################################################################

ns_journals = Namespace(
    "Revues",
    description="Ce module gère les revues disponibles pour les ouvrages.",
    path="/bolero",
)

journal_model = ns_journals.model(
    "revue",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de la revue"),
        "titre": fields.String(required=True, description="Titre de la revue"),
    },
)

####################################################################################################
# Model & Namespace Auteurs
####################################################################################################

ns_authors = Namespace(
    "Auteurs",
    description=(
        "Ce module gère toutes les opérations liées aux auteurs dans le système Boléro."
    ),
    path="/bolero",
)

# Modèle des relations
author_books = create_model_relation_ouvrage(ns_authors, "auteur-ouvrages")

author_reviews = create_model_relation_recension(ns_authors, "auteur-recensions")

# Modèle pour Swagger/Documentation Auteur
author_model = ns_authors.model(
    "auteur",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de l'auteur"),
        "nom": fields.String(required=True, description="Nom de famille de l'auteur"),
        "prenom": fields.String(required=True, description="Prénom de l'auteur"),
        "id_ref": fields.String(description="ID Ref de l'auteur"),
        "id_proprio": fields.String(
            description="ID de l'auteur du portail propriétaire"
        ),
        # Relations (optionnelles si nécessaires)
        "auteur-ouvrages": fields.Nested(
            author_books, description="Liste des ouvrages de l'auteur"
        ),
        "auteur-recensions": fields.Nested(
            author_reviews, description="Liste des recensions de l'auteur"
        ),
        "nb_recensions_sur_ouvrages": fields.Integer(
            required=False,
            description="Nombre de recensions liées aux ouvrages de l’auteur",
        ),
    },
)

####################################################################################################
# Model & Namespace Ouvrages
####################################################################################################

ns_books = Namespace(
    "Ouvrages",
    description=(
        "Ce module gère toutes les opérations liées aux ouvrages dans le système Boléro."
    ),
    path="/bolero",
)

# Modèle des relations

book_authors = create_model_relation_auteur(ns_books, "ouvrage-auteurs")
book_reviews = create_model_relation_recension(ns_books, "ouvrage-recensions")

# Modèle pour Swagger/Documentation
book_model = ns_books.model(
    "ouvrage",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de l'ouvrage"),
        "id_proprio": fields.String(
            description="ID en fonction des portails propriétaire"
        ),
        "doi": fields.String(description="DOI de l'ouvrage"),
        "titre": fields.String(required=True, description="Titre de l'ouvrage"),
        "sous_titre": fields.String(
            description="Sous-titre complémentaire de l'ouvrage"
        ),
        "traduit_par": fields.String(description="Nom et prénom du traducteur"),
        "langue": fields.String(description="Langue originale du texte"),
        "volume": fields.String(description="Numéro du volume"),
        "annee_parution": fields.String(required=True, description="Année de parution"),
        "editeur": fields.String(required=True, description="Nom de l'éditeur"),
        "ean": fields.String(required=True, description="EAN de l'ouvrage"),
        "portail": fields.String(description="Portail où l'ouvrage est disponible"),
        "url": fields.String(description="URL de consultation de l'ouvrage"),
        # Relations (optionnelles si nécessaires)
        "ouvrage-auteurs": fields.Nested(
            book_authors, description="Liste des auteurs associés à l'ouvrage"
        ),
        "ouvrage-recensions": fields.Nested(
            book_reviews, description="Liste des recensions associés à l'ouvrage"
        ),
    },
)

####################################################################################################
# Model & Namespace Recensions
####################################################################################################

ns_reviews = Namespace(
    "Recensions",
    description=(
        "Ce module gère toutes les opérations liées aux recensions dans le système Boléro."
    ),
    path="/bolero",
)

# Modèle des relations
review_authors = create_model_relation_auteur(ns_reviews, "recension-auteurs")
review_books = create_model_relation_ouvrage(ns_reviews, "recension-ouvrages")

review_model = ns_reviews.model(
    "recension",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de la recension"),
        "id_proprio": fields.String(
            description="ID unique attribué par le portail propriétaire"
        ),
        "titre": fields.String(required=True, description="Titre de la recension"),
        "sous_titre": fields.String(description="Sous-titre de la recension"),
        "portail": fields.String(description="Portail associé à la recension"),
        "traduit_par": fields.String(
            description="Nom et prénom du traducteur du texte intégral"
        ),
        "langue": fields.String(
            description="Langue originale du texte intégral (code ISO 639-1, ex. 'fr', 'en')"
        ),
        "titre_revue": fields.String(
            required=True,
            description="Titre de la revue dans laquelle la recension est publiée",
        ),
        "annee": fields.String(
            required=True, description="Année de parution de la revue"
        ),
        "volume": fields.String(description="Volume de la revue"),
        "numero": fields.String(description="Numéro de revue"),
        "date_parution": fields.String(
            description="Date complète de la parution au format AAAA-MM-JJ"
        ),
        "doi": fields.String(
            description="DOI (Digital Object Identifier) de la recension"
        ),
        "url": fields.String(
            required=True,
            description="URL de consultation de la recension",
        ),
        # Relations (optionnelles si nécessaires)
        "review_authors": fields.Nested(
            review_authors,
            description="Liste des auteurs associés à la recension",
        ),
        "review_books": fields.Nested(
            review_books,
            description="Liste des ouvrages associés à la recension",
        ),
    },
)

####################################################################################################
# Model & Namespace Relations
####################################################################################################

ns_relations = Namespace(
    "Relations",
    description=(
        "Ce module gère toutes les opérations liées aux relations dans le système Boléro."
    ),
    path="/bolero",
)

# Modèle des relations
# TODO: Améliorer l'exemple de la réponse, car redondance
relation_author = create_model_relation_auteur(ns_relations, "relation-auteur")
relation_book = create_model_relation_ouvrage(ns_relations, "relation-ouvrage")
relation_review = create_model_relation_recension(ns_relations, "relation-recension")
relation_auteur_ouvrage = ns_relations.model(
    "relation-auteur-ouvrage",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de la recension"),
        "auteur": fields.Nested(relation_author),
        "ouvrage": fields.Nested(relation_book),
        "cree-le": fields.DateTime(
            description="Horodatage de la création de la relation",
            example="2024-11-28T15:30:00",
        ),
        "modifie-le": fields.DateTime(
            description="Horodatage de la dernière modification de la relation",
            example="2024-11-28T15:30:00",
        ),
    },
)

relation_auteur_recension = ns_relations.model(
    "relation-auteur-recension",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de la recension"),
        "auteur": fields.Nested(relation_author),
        "recension": fields.Nested(relation_review),
        "cree-le": fields.DateTime(
            description="Horodatage de la création de la relation",
            example="2024-11-28T15:30:00",
        ),
        "modifie-le": fields.DateTime(
            description="Horodatage de la dernière modification de la relation",
            example="2024-11-28T15:30:00",
        ),
    },
)

relation_ouvrage_recension = ns_relations.model(
    "relation-ouvrage-recension",
    {
        "id": fields.Integer(readOnly=True, description="ID unique de la recension"),
        "ouvrage": fields.Nested(relation_book),
        "recension": fields.Nested(relation_review),
        "cree-le": fields.DateTime(
            description="Horodatage de la création de la relation",
            example="2024-11-28T15:30:00",
        ),
        "modifie-le": fields.DateTime(
            description="Horodatage de la dernière modification de la relation",
            example="2024-11-28T15:30:00",
        ),
    },
)

relation_entry_model = ns_relations.model(
    "RelationEntry",
    {
        "id_auteur": fields.Integer(
            required=False,
            description="ID de l’auteur. À combiner avec id_ouvrage ou id_recension.",
            example=123,
        ),
        "id_ouvrage": fields.Integer(
            required=False,
            description="ID de l’ouvrage. À combiner avec id_auteur ou id_recension.",
            example=456,
        ),
        "id_recension": fields.Integer(
            required=False,
            description="ID de la recension. À combiner avec id_auteur ou id_ouvrage.",
            example=789,
        ),
    },
)

relation_batch_model = ns_relations.model(
    "RelationBatchWrapper",
    {
        "relations": fields.List(
            fields.Nested(relation_entry_model),
            required=True,
            description="Liste des relations à créer",
            example=[
                {"id_auteur": 123, "id_ouvrage": 456},
                {"id_ouvrage": 456, "id_recension": 789},
            ],
        )
    },
)

relation_delete_entry_model = ns_relations.model(
    "RelationDeleteEntry",
    {
        "id": fields.Integer(
            required=True,
            description="Identifiant de la relation à supprimer",
            example=1,
        )
    },
)

relation_delete_batch_model = ns_relations.model(
    "RelationDeleteBatchWrapper",
    {
        "relations": fields.List(
            fields.Nested(relation_delete_entry_model),
            required=True,
            description="Liste des relations à supprimer",
            example=[{"id": 1}, {"id": 2}],
        )
    },
)
