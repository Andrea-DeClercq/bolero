#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from flask import Response, request
from datetime import datetime
from werkzeug.exceptions import BadRequest
from collections import defaultdict
from math import ceil

# Imports from external libraries
from sqlalchemy import extract, func
from sqlalchemy.orm import joinedload
from marshmallow import Schema

# Import from local code
from bolero.models import databases
from core.server.modules.auth import auth_required
from core.server.views import Resource
from ._schema import (
    AuthorResponseSchema,
    BookResponseSchema,
    ReviewReponseSchema,
    AuthorBookResponseSchema,
    AuthorReviewResponseSchema,
    BookReviewResponseSchema,
    EditorResponseSchema,
    JournalResponseSchema,
)
from core.services.tools_belt import humps, generate_csv_stream


class BaseResource(Resource):

    @property
    def db(self):
        return databases.bolero

    @property
    def Author(self):
        return self.db.models.Author

    @property
    def Book(self):
        return self.db.models.Book

    @property
    def Review(self):
        return self.db.models.Review

    @property
    def AuthorBook(self):
        return self.db.models.AuthorBook

    @property
    def AuthorReview(self):
        return self.db.models.AuthorReview

    @property
    def BookReview(self):
        return self.db.models.BookReview

    @property
    def Editor(self):
        return self.db.models.Editor

    @property
    def Journal(self):
        return self.db.models.Journal

    @property
    def query_author(self):
        return self.db.queries.Author

    @property
    def query_book(self):
        return self.db.queries.Book

    @property
    def query_review(self):
        return self.db.queries.Review

    @property
    def query_author_book(self):
        return self.db.queries.AuthorBook

    @property
    def query_author_review(self):
        return self.db.queries.AuthorReview

    @property
    def query_book_review(self):
        return self.db.queries.BookReview

    @property
    def query_editor(self):
        return self.db.queries.Editor

    @property
    def query_journal(self):
        return self.db.queries.Journal

    @property
    def author_filters_map(self):
        return {
            "id": self.Author.id,
            "id_ref": self.Author.id_ref,
            "nom": self.Author.nom,
            "prenom": self.Author.prenom,
            "id_proprio": self.Author.id_proprio,
        }

    @property
    def book_filters_map(self):
        return {
            "id": self.Book.id,
            "doi": self.Book.doi,
            "titre": self.Book.titre,
            "sous_titre": self.Book.sous_titre,
            "traduit_par": self.Book.traduit_par,
            "langue": self.Book.langue,
            "volume": self.Book.volume,
            "annee_parution": self.Book.annee_parution,
            "editeur": self.Book.editeur,
            "ean": self.Book.ean,
            "portail": self.Book.portail,
            "url": self.Book.url,
            "auteur_nom": self.Author.nom,
            "auteur_prenom": self.Author.prenom,
            "id_auteur": self.Author.id,
            "id_proprio": self.Book.id_proprio,
        }

    @property
    def review_filters_map(self):
        return {
            "id": self.Review.id,
            "titre": self.Review.titre,
            "sous_titre": self.Review.sous_titre,
            "traduit_par": self.Review.traduit_par,
            "langue": self.Review.langue,
            "portail": self.Review.portail,
            "titre_revue": self.Review.titre_revue,
            "annee": self.Review.annee,
            "volume": self.Review.volume,
            "numero": self.Review.numero,
            "date_parution": self.Review.date_parution,
            "doi": self.Review.doi,
            "url": self.Review.url,
            "auteur_nom": self.Author.nom,
            "auteur_prenom": self.Author.prenom,
            "id_auteur": self.Author.id,
            "id_proprio": self.Review.id_proprio,
        }

    @classmethod
    def _validate_schema(self, model, partial):
        params = request.form
        params = humps.snakize(params)
        if partial == True:
            fields = {
                field_name: field
                for field_name, field in model.marshmallow().fields.items()
                if field_name in params
            }
            validation_schema = Schema.from_dict(fields)()
            validate = validation_schema.validate(params)
        else:
            validation_schema = Schema.from_dict({**model.marshmallow().fields})()
            validate = validation_schema.validate(params)
        if validate != {}:
            raise Exception(validate)

        return params

    @classmethod
    def _create_item(self, db, model, message):
        params = self._validate_schema(model, False)
        new_item = model(**params)
        db.add(new_item)
        db.commit()
        new_item_id = new_item.id
        return {"message": message, "id": new_item_id}, 201

    @classmethod
    def _update_item(self, item_id, db, model, item, validation_partial=True):
        params = self._validate_schema(model, validation_partial)
        existing_item = db.query(model).get(item_id)
        if existing_item:
            for key, value in params.items():
                setattr(existing_item, key, value)
            db.save(existing_item)
            db.commit()
            return {
                "message": f"{item} mis à jour avec succès",
                "id": existing_item.id,
            }, 200
        else:
            return {"message": f"{item} introuvable"}, 404

    @classmethod
    def _delete_item(self, id, db, model, item, relations=[]):
        existing_item = db.query(model).get(id)
        if existing_item:
            for relation in relations:
                relation_fields = relation.__table__.columns.keys()

                matching_column = None
                if model.__name__ == "Author" and "id_auteur" in relation_fields:
                    matching_column = relation.id_auteur
                elif model.__name__ == "Book" and "id_ouvrage" in relation_fields:
                    matching_column = relation.id_ouvrage
                elif model.__name__ == "Review" and "id_recension" in relation_fields:
                    matching_column = relation.id_recension

                if matching_column:
                    db.query(relation).filter(
                        matching_column == existing_item.id
                    ).delete()

            db.delete(existing_item)
            db.commit()
            return "", 204
        else:
            return {"message": f"{item} introuvable"}, 404

    def _get_item_by_id(self, id: int, item_type, query_model, schema):
        item = query_model.get(id)
        if item:
            item_schema = schema(many=False)
            item_data = item_schema.dump(item)
            return item_data
        else:
            return {"message": f"{item_type} introuvable"}, 404

    def _get_item_by_proprio_id(self, model, query, schema, id_proprio, item_type):
        item = query.filter(model.id_proprio == id_proprio).first()
        if item:
            return schema().dump(item), 200
        return {"message": f"{item_type} introuvable"}, 404

    @staticmethod
    def authorize(method):
        """
        Restriction d'authentification sur les méthodes POST, PUT & DELETE.
        """

        def wrapper(*args, **kwargs):
            if request.method in ["POST", "PUT", "DELETE"]:
                return auth_required()(method)(*args, **kwargs)
            return method(*args, **kwargs)

        return wrapper


class AuthorsResource(BaseResource):
    def _get(self, params):
        limit = request.args.get("limit", default=100, type=int)
        page = request.args.get("page", default=1, type=int)
        sort = request.args.get("sort", default=None, type=str)
        order = request.args.get("order", default="asc", type=str)
        offset = (page - 1) * limit

        sortable_columns = {
            "id": self.Author.id,
            "id-ref": self.Author.id_ref,
            "nom": self.Author.nom,
            "prenom": self.Author.prenom,
            "id-proprio": self.Author.id_proprio,
        }

        query = self.query_author.options(
            joinedload(self.Author.authored_books)
            .joinedload(self.AuthorBook.book)
            .joinedload(self.Book.book_reviews)
        )

        for param, value in params.items():
            if param in self.author_filters_map and param not in [
                "limit",
                "page",
                "sort",
                "order",
            ]:
                if "nom" in param:
                    author_column = getattr(self.Author, param)
                    query = query.filter(author_column.contains(value))
                else:
                    column = self.author_filters_map[param]
                    query = query.filter(column == value)
        if sort in sortable_columns:
            column_to_sort = sortable_columns[sort]
            if order == "desc":
                query = query.order_by(column_to_sort.desc())
            else:
                query = query.order_by(column_to_sort.asc())

        total_items = query.count()
        query = query.limit(limit).offset(offset)
        authors = query.all()
        author_schema = AuthorResponseSchema(many=True)
        author_data = author_schema.dump(authors)
        return {
            "auteurs": author_data,
            "limit": limit,
            "page": page,
            "total": total_items,
        }

    def _get_author_by_id(self, id):
        return self._get_item_by_id(
            id, "Auteur", self.query_author, AuthorResponseSchema
        )

    def _get_author_by_proprio_id(self, id_proprio: str):
        return self._get_item_by_proprio_id(
            self.Author, self.query_author, AuthorResponseSchema, id_proprio, "Auteur"
        )

    @BaseResource.authorize
    def _post(self):
        return self._create_item(self.db, self.Author, "Auteur créé avec succès")

    @BaseResource.authorize
    def _put(self, author_id):
        return self._update_item(author_id, self.db, self.Author, "Auteur")

    @BaseResource.authorize
    def _delete(self, author_id):
        return self._delete_item(
            author_id,
            self.db,
            self.Author,
            "Auteur",
            relations=[self.AuthorBook, self.AuthorReview],
        )

    def _export_csv(self, params):
        db = self.db

        author_ouvrage_count = (
            db.session.query(
                self.AuthorBook.id_auteur,
                func.count(self.AuthorBook.id).label("nb_ouvrages"),
            )
            .group_by(self.AuthorBook.id_auteur)
            .subquery()
        )

        author_recension_count = (
            db.session.query(
                self.AuthorReview.id_auteur,
                func.count(self.AuthorReview.id).label("nb_recensions"),
            )
            .group_by(self.AuthorReview.id_auteur)
            .subquery()
        )

        recensions_sur_ouvrages = (
            db.session.query(
                self.AuthorBook.id_auteur,
                func.count(self.BookReview.id).label("nb_rec_ouvrages"),
            )
            .join(self.Book, self.Book.id == self.AuthorBook.id_ouvrage)
            .join(self.BookReview, self.BookReview.id_ouvrage == self.Book.id)
            .group_by(self.AuthorBook.id_auteur)
            .subquery()
        )

        query = (
            db.session.query(
                self.Author.id,
                self.Author.nom,
                self.Author.prenom,
                self.Author.id_ref,
                self.Author.id_proprio,
                func.coalesce(author_ouvrage_count.c.nb_ouvrages, 0),
                func.coalesce(author_recension_count.c.nb_recensions, 0),
                func.coalesce(recensions_sur_ouvrages.c.nb_rec_ouvrages, 0),
            )
            .outerjoin(
                author_ouvrage_count, author_ouvrage_count.c.id_auteur == self.Author.id
            )
            .outerjoin(
                author_recension_count,
                author_recension_count.c.id_auteur == self.Author.id,
            )
            .outerjoin(
                recensions_sur_ouvrages,
                recensions_sur_ouvrages.c.id_auteur == self.Author.id,
            )
            .order_by(self.Author.nom)
        )

        for param, value in params.items():
            if param in self.author_filters_map:
                column = self.author_filters_map[param]
                if "nom" in param:
                    query = query.filter(column.contains(value))
                else:
                    query = query.filter(column == value)

        headers = [
            "id",
            "nom",
            "prenom",
            "id_ref",
            "id_proprio",
            "nb_ouvrages",
            "nb_recensions",
            "nb_rec_ouvrages",
        ]
        return Response(
            generate_csv_stream(headers, query.yield_per(500)), mimetype="text/csv"
        )


class BooksResource(BaseResource):
    def _get(self, params):
        limit = request.args.get("limit", default=100, type=int)
        page = request.args.get("page", default=1, type=int)
        sort = request.args.get("sort", default=None, type=str)
        order = request.args.get("order", default="asc", type=str)
        offset = (page - 1) * limit

        sortable_columns = {
            "id": self.Book.id,
            "titre": self.Book.titre,
            "ean": self.Book.ean,
            "doi": self.Book.doi,
            "editeur": self.Book.doi,
            "annee_parution": self.Book.annee_parution,
        }

        query = self.query_book.outerjoin(self.Book.book_authors)
        query = query.outerjoin(self.Author)
        for param, value in params.items():
            if param in self.book_filters_map and param not in ["limit", "page"]:
                column = self.book_filters_map[param]
                if param.startswith("auteur_"):
                    author_column = getattr(self.Author, param[len("auteur_") :])
                    query = query.filter(author_column.contains(value))
                elif "titre" == param or "editeur" == param or "traduit_par" == param:
                    book_column = getattr(self.Book, param)
                    query = query.filter(book_column.contains(value))
                else:
                    query = query.filter(column == value)

        if sort in sortable_columns:
            column_to_sort = sortable_columns[sort]
            if order == "desc":
                query = query.order_by(column_to_sort.desc())
            else:
                query = query.order_by(column_to_sort.asc())
        total_items = query.count()
        query = query.limit(limit).offset(offset)
        books = query.all()
        book_schema = BookResponseSchema(many=True)
        book_data = book_schema.dump(books)
        return {
            "ouvrages": book_data,
            "limit": limit,
            "page": page,
            "total": total_items,
        }

    def _get_book_by_id(self, id):
        return self._get_item_by_id(id, "Ouvrage", self.query_book, BookResponseSchema)

    def _get_book_by_id_proprio(self, id_proprio: str):
        return self._get_item_by_proprio_id(
            self.Book, self.query_book, BookResponseSchema, id_proprio, "Ouvrage"
        )

    def _get_book_by_ean(self, ean: str):
        book = self.query_book.filter(self.Book.ean == ean).first()
        if book:
            return BookResponseSchema().dump(book), 200
        return {"message": "Ouvrage introuvable"}, 404

    @BaseResource.authorize
    def _post(self):
        return self._create_item(self.db, self.Book, "Ouvrage créé avec succès")

    @BaseResource.authorize
    def _put(self, book_id):
        return self._update_item(book_id, self.db, self.Book, "Ouvrage")

    @BaseResource.authorize
    def _delete(self, book_id):
        return self._delete_item(
            book_id,
            self.db,
            self.Book,
            "Ouvrage",
            relations=[self.AuthorBook, self.BookReview],
        )

    def _export_csv(self, params):
        db = self.db

        excluded_columns = {"cree_le", "modifie_le"}
        book_columns = [
            getattr(self.Book, col.name)
            for col in self.Book.__table__.columns
            if col.name not in excluded_columns
        ]

        review_count_subquery = (
            db.session.query(
                self.BookReview.id_ouvrage,
                func.count(self.BookReview.id).label("nb_recensions"),
            )
            .group_by(self.BookReview.id_ouvrage)
            .subquery()
        )

        query = (
            db.session.query(
                *book_columns,
                func.coalesce(review_count_subquery.c.nb_recensions, 0).label(
                    "nb_recensions"
                ),
            )
            .outerjoin(
                review_count_subquery,
                review_count_subquery.c.id_ouvrage == self.Book.id,
            )
            .outerjoin(self.Book.book_authors)
            .outerjoin(self.Author)
        ).distinct(self.Book.id)

        for param, value in params.items():
            if param in self.book_filters_map:
                column = self.book_filters_map[param]
                if param.startswith("auteur_"):
                    author_column = getattr(self.Author, param[len("auteur_") :])
                    query = query.filter(author_column.contains(value))
                elif param in ["titre", "editeur", "traduit_par"]:
                    query = query.filter(column.contains(value))
                else:
                    query = query.filter(column == value)

        books = list(query.yield_per(500))
        book_ids = [book.id for book in books]

        authors_map = (
            db.session.query(
                self.AuthorBook.id_ouvrage,
                self.Author.nom,
                self.Author.prenom,
            )
            .join(self.Author, self.Author.id == self.AuthorBook.id_auteur)
            .filter(self.AuthorBook.id_ouvrage.in_(book_ids))
            .all()
        )

        authors_by_book = defaultdict(list)
        for id_ouvrage, nom, prenom in authors_map:
            authors_by_book[id_ouvrage].append(f"{nom},{prenom}")

        headers = [
            col.name
            for col in self.Book.__table__.columns
            if col.name not in excluded_columns
        ]
        headers += ["auteurs(nom,prenom)", "nb_recensions"]

        rows = []
        for book in books:
            row = [
                getattr(book, field)
                for field in headers
                if field not in ["auteurs(nom,prenom)", "nb_recensions"]
            ]
            row.append(";".join(authors_by_book.get(book.id, [])))
            row.append(book.nb_recensions)
            rows.append(row)

        return Response(generate_csv_stream(headers, rows), mimetype="text/csv")


class ReviewsResource(BaseResource):
    def _get(self, params):
        limit = request.args.get("limit", default=100, type=int)
        page = request.args.get("page", default=1, type=int)
        sort = request.args.get("sort", default=None, type=str)
        order = request.args.get("order", default="asc", type=str)
        offset = (page - 1) * limit

        sortable_columns = {
            "id": self.Review.id,
            "titre": self.Review.titre,
            "titre_revue": self.Review.titre_revue,
            "annee": self.Review.annee,
            "volume": self.Review.volume,
            "numero": self.Review.numero,
            "portail": self.Review.portail,
            "date_parution": self.Review.date_parution,
        }

        query = self.query_review.outerjoin(self.Review.review_authors)
        query = query.outerjoin(self.Author)
        for param, value in params.items():
            if param in self.review_filters_map:
                column = self.review_filters_map[param]
                if param.startswith("auteur_"):
                    author_column = getattr(self.Author, param[len("auteur_") :])
                    query = query.filter(author_column.contains(value))
                elif "titre" in param:
                    review_column = getattr(self.Review, param)
                    query = query.filter(review_column.contains(value))
                elif "date_parution" == param:
                    try:
                        date_value = datetime.strptime(value, "%Y-%m-%d")
                        year_value = date_value.year
                        query = query.filter(
                            extract("year", self.Review.date_parution) == year_value
                        )
                    except ValueError:
                        raise ValueError(
                            "Le format attendu pour 'date_parution' est YYYY-MM-DD"
                        )
                else:
                    query = query.filter(column == value)
            if sort in sortable_columns:
                column_to_sort = sortable_columns[sort]
                if order == "desc":
                    query = query.order_by(column_to_sort.desc())
                else:
                    query = query.order_by(column_to_sort.asc())
        total_items = query.count()
        query = query.limit(limit).offset(offset)
        reviews = query.all()
        review_schema = ReviewReponseSchema(many=True)
        review_data = review_schema.dump(reviews)
        return {
            "recensions": review_data,
            "limit": limit,
            "page": page,
            "total": total_items,
        }

    def _get_review_by_id(self, id):
        return self._get_item_by_id(
            id, "Recension", self.query_review, ReviewReponseSchema
        )

    def _get_review_by_id_proprio(self, id_proprio: str):
        return self._get_item_by_proprio_id(
            self.Review, self.query_review, ReviewReponseSchema, id_proprio, "Recension"
        )

    @BaseResource.authorize
    def _post(self):
        return self._create_item(self.db, self.Review, "Recension créée avec succès")

    @BaseResource.authorize
    def _put(self, review_id):
        return self._update_item(review_id, self.db, self.Review, "Recension")

    @BaseResource.authorize
    def _delete(self, review_id):
        return self._delete_item(
            review_id,
            self.db,
            self.Review,
            "Recension",
            relations=[self.AuthorReview, self.BookReview],
        )

    def _export_csv(self, params):
        db = self.db

        excluded_columns = {"cree_le", "modifie_le"}
        review_columns = [
            getattr(self.Review, col.name)
            for col in self.Review.__table__.columns
            if col.name not in excluded_columns
        ]

        query = (
            db.session.query(*review_columns)
            .outerjoin(self.Review.review_authors)
            .outerjoin(self.Author)
            .outerjoin(self.Review.review_books)
            .outerjoin(self.Book)
        )

        for param, value in params.items():
            if param in self.review_filters_map:
                column = self.review_filters_map[param]
                if param.startswith("auteur_"):
                    author_column = getattr(self.Author, param[len("auteur_") :])
                    query = query.filter(author_column.contains(value))
                elif "titre" in param:
                    review_column = getattr(self.Review, param)
                    query = query.filter(review_column.contains(value))
                elif param == "date_parution":
                    try:
                        date_value = datetime.strptime(value, "%Y-%m-%d")
                        query = query.filter(
                            extract("year", self.Review.date_parution)
                            == date_value.year
                        )
                    except ValueError:
                        continue
                else:
                    query = query.filter(column == value)

        recensions = list(query.distinct().yield_per(500))
        review_ids = [r.id for r in recensions]

        authors_map = (
            db.session.query(
                self.AuthorReview.id_recension, self.Author.nom, self.Author.prenom
            )
            .join(self.Author)
            .filter(self.AuthorReview.id_recension.in_(review_ids))
            .all()
        )

        authors_by_review = defaultdict(list)
        for rec_id, nom, prenom in authors_map:
            authors_by_review[rec_id].append(f"{nom},{prenom}")

        books_links = (
            db.session.query(
                self.BookReview.id_recension,
                self.Book.id,
                self.Book.titre,
                self.Book.annee_parution,
                self.Book.editeur,
            )
            .join(self.Book)
            .filter(self.BookReview.id_recension.in_(review_ids))
            .all()
        )

        ouvrages_by_review = defaultdict(list)
        book_ids = set()
        for rec_id, book_id, titre, annee, editeur in books_links:
            ouvrages_by_review[rec_id].append((book_id, titre, annee, editeur))
            book_ids.add(book_id)

        book_authors_map = (
            db.session.query(
                self.AuthorBook.id_ouvrage, self.Author.nom, self.Author.prenom
            )
            .join(self.Author)
            .filter(self.AuthorBook.id_ouvrage.in_(book_ids))
            .all()
        )

        authors_by_book = defaultdict(list)
        for book_id, nom, prenom in book_authors_map:
            authors_by_book[book_id].append(f"{nom},{prenom}")

        headers = [
            col.name
            for col in self.Review.__table__.columns
            if col.name not in excluded_columns
        ]
        headers += ["auteurs(nom,prenom)", "ouvrages"]

        rows = []
        for review in recensions:
            row = [
                getattr(review, field)
                for field in headers
                if field not in ["auteurs(nom,prenom)", "ouvrages"]
            ]
            row.append(";".join(authors_by_review.get(review.id, [])))

            ouvrages = []
            for book_id, titre, annee, editeur in ouvrages_by_review.get(review.id, []):
                auteurs = authors_by_book.get(book_id, [])
                meta = f"{titre} ({annee}, {editeur})"
                if auteurs:
                    meta += f" - {'; '.join(auteurs)}"
                ouvrages.append(meta)
            row.append(" | ".join(ouvrages))
            rows.append(row)

        return Response(generate_csv_stream(headers, rows), mimetype="text/csv")


class RelationResource(BaseResource):
    def _get_relation_model_from_url(self, url):
        if "auteurs-ouvrages" in url:
            return self.AuthorBook
        elif "auteurs-recensions" in url:
            return self.AuthorReview
        elif "ouvrages-recensions" in url:
            return self.BookReview
        return None

    def _create_relation_from_params(self, params):
        if len(params) != 2:
            return {
                "message": "Deux champs doivent être fournis pour établir une relation"
            }, 422

        relations_map = {
            ("id_auteur", "id_ouvrage"): {
                "entity1": "author",
                "entity2": "book",
                "message": "Relation entre l’auteur et l’ouvrage ajoutée avec succès",
                "relation_class": self.AuthorBook,
            },
            ("id_auteur", "id_recension"): {
                "entity1": "author",
                "entity2": "review",
                "message": "Relation entre l’auteur et la recension ajoutée avec succès",
                "relation_class": self.AuthorReview,
            },
            ("id_ouvrage", "id_recension"): {
                "entity1": "book",
                "entity2": "review",
                "message": "Relation entre l’ouvrage et la recension ajoutée avec succès",
                "relation_class": self.BookReview,
            },
        }

        for (key1, key2), relation_info in relations_map.items():
            if key1 in params and key2 in params:
                entity1_id = int(params[key1])
                entity2_id = int(params[key2])

                entity1 = getattr(self, f"query_{relation_info['entity1']}").get(
                    entity1_id
                )
                entity2 = getattr(self, f"query_{relation_info['entity2']}").get(
                    entity2_id
                )

                if not entity1 or not entity2:
                    return {
                        "message": f"{relation_info['entity1']} ou {relation_info['entity2']} introuvable"
                    }, 404

                if self._relation_exists(
                    relation_info["relation_class"],
                    {key1: entity1_id, key2: entity2_id},
                ):
                    return {
                        "message": "Cette relation entre ces deux objets existe déjà"
                    }, 409

                relation = relation_info["relation_class"](
                    **{
                        relation_info["entity1"]: entity1,
                        relation_info["entity2"]: entity2,
                    }
                )
                self.db.add(relation)
                self.db.commit()
                return {"message": relation_info["message"], "id": relation.id}, 201

        return {"message": "Données insuffisantes pour établir une relation"}, 422

    def _relation_exists(self, relation_class, filter_criteria):
        return (
            self.db.query(relation_class).filter_by(**filter_criteria).first()
            is not None
        )

    def _add_relation_from_dict(self, data: dict):
        return self._create_relation_from_params(data)

    def _relation_data(self, query, model, response_schema, id=None):
        limit = request.args.get("limit", default=100, type=int)
        page = request.args.get("page", default=1, type=int)
        offset = (page - 1) * limit

        params = request.args.to_dict()
        params = humps.snakize(params)

        for key, value in params.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        if id:
            query = query.filter(model.id == id)
        query = query.limit(limit).offset(offset)
        relations = query.all()
        if not relations:
            return {"message": f"Relation introuvable"}, 404
        relation_schema = response_schema
        relation_data = relation_schema.dump(relations)
        return relation_data

    def _delete_relation_by_id(self, relation_id, model):
        relation = self.db.query(model).filter_by(id=relation_id).first()
        if relation:
            self.db.delete(relation)
            self.db.commit()
            return True
        return False

    ####################################################################################################
    #   Méthode relation
    ####################################################################################################
    def _get_relation(self, id=None):
        url = request.url
        if "auteurs-ouvrages" in url:
            return self._relation_data(
                self.query_author_book,
                self.AuthorBook,
                AuthorBookResponseSchema(many=True),
                id,
            )
        if "auteurs-recensions" in url:
            return self._relation_data(
                self.query_author_review,
                self.AuthorReview,
                AuthorReviewResponseSchema(many=True),
                id,
            )
        if "ouvrages-recensions" in url:
            return self._relation_data(
                self.query_book_review,
                self.BookReview,
                BookReviewResponseSchema(many=True),
                id,
            )
        else:
            return {"message": "Aucune relation trouvée"}, 404

    @BaseResource.authorize
    def _add_relation(self):
        params = request.form.to_dict()
        params = humps.snakize(params)
        return self._create_relation_from_params(params)

    @BaseResource.authorize
    def post_batch(self):
        try:
            data = request.json
            relations = data.get("relations", [])

            if not isinstance(relations, list):
                raise BadRequest(
                    "Le corps de la requête doit être une liste de relations"
                )

            results = []
            for entry in relations:
                try:
                    result, status = self._add_relation_from_dict(entry)
                    results.append({"input": entry, "status": status, "result": result})
                except Exception as e:
                    results.append({"input": entry, "status": 400, "error": str(e)})

            success_count = len([r for r in results if r["status"] == 201])
            if success_count == len(results):
                return {
                    "message": f"{success_count} relations créées",
                    "results": results,
                }, 201
            else:
                return {
                    "message": f"{success_count} relations créées, erreurs sur {len(results) - success_count}",
                    "results": results,
                }, 207
        except Exception as e:
            return {
                "message": "Erreur lors du traitement du batch",
                "error": str(e),
            }, 400

    @BaseResource.authorize
    def _put_relation(self, relation_id):
        url = request.url
        params = request.form
        params = humps.snakize(params)

        relation_model = self._get_relation_model_from_url(url)
        if not relation_model:
            return {"message": "Aucune relation trouvée"}, 404

        author_id = params.get("id_auteur")
        book_id = params.get("id_ouvrage")
        review_id = params.get("id_recension")
        # Check if the relation already exist
        relation = self.db.query(relation_model).filter_by(id=relation_id).first()
        if relation:
            if author_id is not None:
                relation.id_auteur = int(author_id)
            if book_id is not None:
                relation.id_ouvrage = int(book_id)
            if review_id is not None:
                relation.id_recension = int(review_id)
            self.db.commit()
            return {
                "message": f"Relation {relation_model.__name__} mise à jour avec succès",
                "id": relation_id,
            }, 200
        else:
            return {"message": f"Relation {relation_model.__name__} introuvable"}, 404

    @BaseResource.authorize
    def _delete_relation(self, relation_id):
        url = request.url
        model = self._get_relation_model_from_url(url)
        if not model:
            return {"message": "Aucune relation trouvée"}, 404

        if self._delete_relation_by_id(relation_id, model):
            return "", 204
        else:
            return {"message": f"Relation {model.__name__} introuvable"}, 404

    @BaseResource.authorize
    def delete_batch(self):
        try:
            data = request.json
            relation_list = data.get("relations", [])

            if not isinstance(relation_list, list):
                raise BadRequest(
                    "Le corps de la requête doit être une liste d'objets contenant des IDs"
                )

            ids = [entry["id"] for entry in relation_list if "id" in entry]
            if not ids:
                raise BadRequest("Aucun identifiant valide fourni")

            url = request.url
            model = self._get_relation_model_from_url(url)
            if not model:
                return {"message": "Type de relation non reconnu dans l'URL"}, 400

            deleted, not_found = 0, []
            for relation_id in ids:
                if not self._delete_relation_by_id(relation_id, model):
                    not_found.append(relation_id)
                else:
                    deleted += 1

            return {
                "message": f"{deleted} relations supprimées",
                "non_trouvees": not_found,
            }, (200 if deleted > 0 else 404)

        except Exception as e:
            return {
                "message": "Erreur lors de la suppression des relations",
                "error": str(e),
            }, 400


class EditorsResource(BaseResource):
    def _get(self, params):
        limit = params.get("limit", 100)
        page = params.get("page", 1)
        offset = (page - 1) * limit

        query = self.query_editor

        if nom := params.get("nom"):
            query = query.filter(self.Editor.nom.ilike(f"%{nom}%"))

        query = query.order_by(self.Editor.nom.asc())

        total = query.count()
        results = query.limit(limit).offset(offset).all()

        editor_schema = EditorResponseSchema(many=True)
        return {
            "editeurs": editor_schema.dump(results),
            "page": page,
            "limit": limit,
            "total": total,
            "pages": ceil(total / limit),
        }

    @BaseResource.authorize
    def _post(self):
        params = self._validate_schema(self.Editor, False)
        new_editor = self.Editor(**params)
        self.db.add(new_editor)
        self.db.commit()
        new_editeur_id = new_editor.id
        new_editeur_nom = new_editor.nom

        return {
            "message": "Editeur crée avec succès",
            "id": new_editeur_id,
            "nom": new_editeur_nom,
        }, 201


class JournalResource(BaseResource):
    def _get(self, params):
        limit = params.get("limit", 100)
        page = params.get("page", 1)
        offset = (page - 1) * limit

        query = self.query_journal

        if titre := params.get("titre"):
            query = query.filter(self.Journal.titre.ilike(f"%{titre}%"))

        query = query.order_by(self.Journal.titre.asc())

        total = query.count()
        results = query.limit(limit).offset(offset).all()

        journal_schema = JournalResponseSchema(many=True)
        return {
            "revues": journal_schema.dump(results),
            "page": page,
            "limit": limit,
            "total": total,
            "pages": ceil(total / limit),
        }

    @BaseResource.authorize
    def _post(self):
        params = self._validate_schema(self.Journal, False)
        new_journal = self.Journal(**params)
        self.db.add(new_journal)
        self.db.commit()
        new_journal_id = new_journal.id
        new_journal_titre = new_journal.titre

        return {
            "message": "Revue crée avec succès",
            "id": new_journal_id,
            "titre": new_journal_titre,
        }, 201
