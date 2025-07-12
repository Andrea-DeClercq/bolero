#!/usr/bin/env python
"""
Parsers des différentes routes pour la documentation.
"""

# Import from stdlib

# Imports from external libraries
from flask_restx import reqparse

# Import from local code


####################################################################################################
# Utils
####################################################################################################
def build_parser(fields, location="args", required_fields=None):
    parser = reqparse.RequestParser()
    for name, spec in fields.items():
        parser.add_argument(
            name,
            type=spec.get("type", str),
            help=spec.get("help", ""),
            required=name in (required_fields or []),
            location=location,
        )
    return parser


####################################################################################################
# Parser Éditeurs
####################################################################################################
def common_editor_fields(location="args", include_id=True):
    fields = {
        "nom": {"type": str, "help": "Nom de l'éditeur"},
    }
    if include_id:
        fields["id"] = {"type": int, "help": "ID unique de l'éditeur"}

    return fields


def editor_get_parser():
    fields = common_editor_fields(location="args", include_id=True)
    parser = build_parser(fields, location="args")
    parser.add_argument(
        "limit", type=int, help="Nombre de résultats par page", location="args"
    )
    parser.add_argument("page", type=int, help="Numéro de la page", location="args")
    return parser


def editor_post_parser():
    fields = common_editor_fields(location="form", include_id=False)
    return build_parser(fields, location="form", required_fields=["nom"])


####################################################################################################
# Parser Revues
####################################################################################################
def common_journal_fields(location="args", include_id=True):
    fields = {
        "titre": {"type": str, "help": "Titre de la revue"},
    }
    if include_id:
        fields["id"] = {"type": int, "help": "ID unique de la revue"}

    return fields


def journal_get_parser():
    fields = common_journal_fields(location="args", include_id=True)
    parser = build_parser(fields, location="args")
    parser.add_argument(
        "limit", type=int, help="Nombre de résultats par page", location="args"
    )
    parser.add_argument("page", type=int, help="Numéro de la page", location="args")
    return parser


def journal_post_parser():
    fields = common_journal_fields(location="form", include_id=False)
    return build_parser(fields, location="form", required_fields=["titre"])


####################################################################################################
# Parser Auteur
####################################################################################################
def common_author_fields(location="args", include_id=True, required_fields=None):
    fields = {
        "nom": {"type": str, "help": "Nom de l'auteur"},
        "prenom": {"type": str, "help": "Prénom de l'auteur"},
        "id_ref": {"type": str, "help": "ID ref de l'auteur"},
        "id_proprio": {"type": str, "help": "ID du propriétaire"},
    }
    if include_id:
        fields["id"] = {"type": int, "help": "ID unique de l'auteur"}

    return build_parser(fields, location=location, required_fields=required_fields)


def author_get_parser():
    parser = common_author_fields(location="args", include_id=True)
    parser.add_argument(
        "limit", type=int, help="Nombre de résultats par page", location="args"
    )
    parser.add_argument("page", type=int, help="Numéro de la page", location="args")
    return parser


def author_post_parser():
    return common_author_fields(
        "form", include_id=False, required_fields=["nom", "prenom"]
    )


def author_put_parser():
    return common_author_fields(location="form", include_id=False)


def author_export_parser():
    return common_author_fields(location="args", include_id=True)


####################################################################################################
# Parser Ouvrages
####################################################################################################
def common_book_fields(location="args", include_id=True, include_author_filters=False):
    fields = {
        "titre": {"type": str, "help": "Titre de l'ouvrage"},
        "sous_titre": {"type": str, "help": "Sous-titre de l'ouvrage"},
        "volume": {"type": str, "help": "Volume"},
        "annee_parution": {"type": str, "help": "Année de parution"},
        "editeur": {"type": str, "help": "Éditeur"},
        "ean": {"type": str, "help": "EAN de l'ouvrage"},
        "portail": {"type": str, "help": "Portail"},
        "traduit_par": {"type": str, "help": "Traducteur"},
        "langue": {
            "type": str,
            "help": "Langue originale du texte intégral (code ISO 639-1, par ex. 'fr', 'en')",
        },
        "id_proprio": {
            "type": str,
            "help": "ID unique en fonction des portails propriétaires",
        },
        "doi": {"type": str, "help": "DOI de l'ouvrage"},
        "url": {"type": str, "help": "URL de l'ouvrage"},
    }
    if include_author_filters:
        fields.update(
            {
                "auteur_nom": {"type": str, "help": "Nom de l'auteur"},
                "auteur_prenom": {"type": str, "help": "Prénom de l'auteur"},
                "id_auteur": {"type": int, "help": "ID de l'auteur"},
            }
        )
    if include_id:
        fields["id"] = {"type": int, "help": "ID unique de l'ouvrage"}
    return fields


def book_get_parser():
    fields = common_book_fields(
        location="args", include_id=True, include_author_filters=True
    )
    parser = build_parser(fields, location="args")
    parser.add_argument(
        "limit", type=int, help="Nombre de résultats par page", location="args"
    )
    parser.add_argument("page", type=int, help="Numéro de la page", location="args")
    return parser


def book_post_parser():
    fields = common_book_fields(location="form", include_id=False)
    required = ["titre", "annee_parution", "editeur", "ean"]
    return build_parser(fields, location="form", required_fields=required)


def book_put_parser():
    fields = common_book_fields(location="form", include_id=False)
    return build_parser(fields, location="form")


def book_export_parser():
    fields = common_book_fields(
        location="args", include_id=True, include_author_filters=True
    )
    return build_parser(fields, location="args")


####################################################################################################
# Parser Recensions
####################################################################################################
def common_review_fields(
    location="args", include_id=True, include_author_filters=False
):
    fields = {
        "titre": {"type": str, "help": "Titre de la recension"},
        "sous_titre": {"type": str, "help": "Sous-titre de la recension"},
        "traduit_par": {"type": str, "help": "Traducteur"},
        "langue": {
            "type": str,
            "help": "Langue originale du texte intégral (code ISO 639-1, par ex. 'fr', 'en')",
        },
        "portail": {"type": str, "help": "Portail"},
        "titre_revue": {"type": str, "help": "Titre de la revue"},
        "annee": {"type": str, "help": "Année de parution"},
        "volume": {"type": str, "help": "Volume"},
        "numero": {"type": str, "help": "Numéro"},
        "date_parution": {"type": str, "help": "Date de parution (YYYY-MM-DD)"},
        "doi": {"type": str, "help": "DOI de la recension"},
        "url": {"type": str, "help": "URL de la recension"},
        "id_proprio": {
            "type": str,
            "help": "ID unique en fonction des portails propriétaires",
        },
    }
    if include_author_filters:
        fields.update(
            {
                "auteur_nom": {"type": str, "help": "Nom de l'auteur"},
                "auteur_prenom": {"type": str, "help": "Prénom de l'auteur"},
                "id_auteur": {"type": int, "help": "ID de l'auteur"},
            }
        )
    if include_id:
        fields["id"] = {"type": int, "help": "ID unique de la recension"}
    return fields


def review_get_parser():
    fields = common_review_fields("args", include_id=True, include_author_filters=True)
    parser = build_parser(fields, location="args")
    parser.add_argument(
        "limit", type=int, help="Nombre de résultats par page", location="args"
    )
    parser.add_argument("page", type=int, help="Numéro de la page", location="args")
    return parser


def review_post_parser():
    fields = common_review_fields("form", include_id=False)
    required = ["titre", "titre_revue", "annee", "url"]
    return build_parser(fields, location="form", required_fields=required)


def review_put_parser():
    fields = common_review_fields("form", include_id=False)
    return build_parser(fields, location="form")


def review_export_parser():
    fields = common_review_fields("args", include_id=True, include_author_filters=True)
    parser = build_parser(fields, location="args")
    return parser


####################################################################################################
# Parser Relation
####################################################################################################


def relation_post_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "id_auteur",
        type=int,
        required=False,
        help="Identifiant unique de l'auteur",
        location="form",
    )
    parser.add_argument(
        "id_ouvrage",
        type=int,
        required=False,
        help="Identifiant unique de l'ouvrage",
        location="form",
    )
    parser.add_argument(
        "id_recension",
        type=int,
        required=False,
        help="Identifiant unique de la recension",
        location="form",
    )
    return parser


def author_book_get_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "limit",
        type=int,
        help="Limite de relation Auteur-Ouvrage à afficher",
        location="args",
    )
    parser.add_argument(
        "page",
        type=int,
        help="Page de la liste des relations Auteur-Ouvrage",
        location="args",
    )
    return parser


def author_book_put_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "id_auteur", type=int, help="Identifiant unique de l'auteur", location="form"
    )
    parser.add_argument(
        "id_ouvrage", type=int, help="Identifiant unique de l'ouvrage", location="form"
    )
    return parser


def author_review_get_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "limit",
        type=int,
        help="Limite de relation Auteur-Recension à afficher",
        location="args",
    )
    parser.add_argument(
        "page",
        type=int,
        help="Page de la liste des relations Auteur-Recension",
        location="args",
    )
    return parser


def author_review_put_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "id_auteur", type=int, help="Identifiant unique de l'auteur", location="form"
    )
    parser.add_argument(
        "id_recension",
        type=int,
        help="Identifiant unique de la recension",
        location="form",
    )
    return parser


def book_review_get_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "limit",
        type=int,
        help="Limite de relation Ouvrage-Recension à afficher",
        location="args",
    )
    parser.add_argument(
        "page",
        type=int,
        help="Page de la liste des relations Ouvrage-Recension",
        location="args",
    )
    return parser


def book_review_put_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "id_ouvrage", type=int, help="Identifiant unique de l'ouvrage", location="form"
    )
    parser.add_argument(
        "id_recension",
        type=int,
        help="Identifiant unique de la recension",
        location="form",
    )
    return parser
