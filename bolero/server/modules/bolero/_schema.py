#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, post_dump

# Import from local code
from bolero.models import databases


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        exclude = (
            "cree_le",
            "modifie_le",
        )


class AuthorResponseSchema(BaseSchema):
    """
    Schema response for the Author model.
    """

    class Meta(BaseSchema.Meta):
        model = databases.bolero.models.Author
        fields = (
            "id",
            "id_ref",
            "id_proprio",
            "nom",
            "prenom",
            "authored_books",
            "authored_reviews",
            "cree_le",
            "modifie_le",
        )

    authored_books = fields.Nested(
        "AuthorBookResponseSchema",
        many=True,
        only=["book", "id_relation"],
        data_key="auteur_ouvrages",
    )
    authored_reviews = fields.Nested(
        "AuthorReviewResponseSchema",
        many=True,
        only=["review", "id_relation"],
        data_key="auteur_recensions",
    )

    nb_recensions_sur_ouvrages = fields.Int(dump_only=True)

    @post_dump(pass_original=True)
    def add_nb_recensions(self, data, original, **kwargs):
        count = 0
        for ab in getattr(original, "authored_books", []):
            book = getattr(ab, "book", None)
            if book:
                recs = getattr(book, "book_reviews", [])
                count += len(recs)
        data["nb_recensions_sur_ouvrages"] = count
        return data


class BookResponseSchema(BaseSchema):
    """
    Schema response for the Book model.
    """

    class Meta(BaseSchema.Meta):
        model = databases.bolero.models.Book
        fields = (
            "id",
            "id_proprio",
            "doi",
            "titre",
            "sous_titre",
            "traduit_par",
            "langue",
            "volume",
            "annee_parution",
            "editeur",
            "ean",
            "portail",
            "url",
            "book_authors",
            "book_reviews",
            "cree_le",
            "modifie_le",
        )

    book_authors = fields.Nested(
        "AuthorBookResponseSchema",
        many=True,
        only=["author", "id_relation"],
        data_key="ouvrage_auteurs",
    )
    book_reviews = fields.Nested(
        "BookReviewResponseSchema",
        many=True,
        only=["review", "id_relation"],
        data_key="ouvrage_recensions",
    )


class ReviewReponseSchema(BaseSchema):
    """
    Schema response for the Review model.
    """

    class Meta(BaseSchema.Meta):
        model = databases.bolero.models.Review
        fields = (
            "id",
            "id_proprio",
            "titre",
            "sous_titre",
            "portail",
            "traduit_par",
            "langue",
            "titre_revue",
            "annee",
            "volume",
            "numero",
            "date_parution",
            "doi",
            "url",
            "review_authors",
            "review_books",
            "cree_le",
            "modifie_le",
        )

    review_authors = fields.Nested(
        "AuthorReviewResponseSchema",
        many=True,
        only=["author", "id_relation"],
        data_key="recension_auteurs",
    )
    review_books = fields.Nested(
        "BookReviewResponseSchema",
        many=True,
        only=["book", "id_relation"],
        data_key="recension_ouvrages",
    )


####################################################################################################
#   Schema Relation, display only the importants fields
####################################################################################################


class AuthorRelationSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the Author model when it is called from relation
    """

    class Meta:
        model = databases.bolero.models.Author
        exclude = ("cree_le", "modifie_le", "authored_books", "authored_reviews")


class BookRelationSchema(SQLAlchemyAutoSchema):
    """
    Schema response for models Book when it is called from relation
    """

    class Meta:
        model = databases.bolero.models.Book
        exclude = ("cree_le", "modifie_le", "book_reviews", "book_authors")


class ReviewRelationSchema(SQLAlchemyAutoSchema):
    """
    Schema response for model Review when it is called from relation
    """

    class Meta:
        model = databases.bolero.models.Review
        exclude = ("cree_le", "modifie_le", "review_authors", "review_books")


class AuthorBookResponseSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the AuthorBook model.
    """

    class Meta:
        model = databases.bolero.models.AuthorBook

    id_relation = fields.Int(attribute="id")
    author = fields.Nested(
        AuthorRelationSchema,
        only=[
            "id",
            "id_ref",
            "nom",
            "prenom",
        ],
        data_key="auteur",
    )
    book = fields.Nested(
        BookRelationSchema,
        only=[
            "id",
            "titre",
            "annee_parution",
            "editeur",
            "ean",
            "doi",
            "url",
            "id_proprio",
            "portail",
            "langue",
        ],
        data_key="ouvrage",
    )


class AuthorReviewResponseSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the AuthorReview model.
    """

    class Meta:
        model = databases.bolero.models.AuthorReview

    id_relation = fields.Int(attribute="id")
    author = fields.Nested(
        AuthorRelationSchema,
        only=[
            "id",
            "id_ref",
            "nom",
            "prenom",
        ],
        data_key="auteur",
    )
    review = fields.Nested(
        ReviewRelationSchema,
        only=[
            "id",
            "titre",
            "titre_revue",
            "annee",
            "volume",
            "numero",
            "url",
            "id_proprio",
            "portail",
            "date_parution",
            "langue",
        ],
        data_key="recension",
    )


class BookReviewResponseSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the BookReview model.
    """

    class Meta:
        model = databases.bolero.models.BookReview

    id_relation = fields.Int(attribute="id")
    book = fields.Nested(
        BookRelationSchema,
        only=[
            "id",
            "titre",
            "annee_parution",
            "editeur",
            "ean",
            "doi",
            "url",
            "id_proprio",
            "portail",
            "langue",
        ],
        data_key="ouvrage",
    )
    review = fields.Nested(
        ReviewRelationSchema,
        only=[
            "id",
            "titre",
            "titre_revue",
            "annee",
            "volume",
            "numero",
            "url",
            "id_proprio",
            "portail",
            "langue",
            "date_parution",
        ],
        data_key="recension",
    )


class EditorResponseSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the Editor model.
    """

    class Meta(BaseSchema.Meta):
        model = databases.bolero.models.Editor

    fields = (
        "id",
        "nom",
    )


class JournalResponseSchema(SQLAlchemyAutoSchema):
    """
    Schema response for the Journal model.
    """

    class Meta(BaseSchema.Meta):
        model = databases.bolero.models.Journal

    fields = (
        "id",
        "titre",
    )
