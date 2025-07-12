#!/usr/bin/env python
# pylint: disable=W0612
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship

# Import from local code
from core.models.mixins import CommonMixin, PasswordMixin


def setup(db):
    class Author(CommonMixin, db.Model):
        __tablename__ = "auteur"

        # Colonnes
        id_proprio = Column(
            String(128),
            unique=True,
            nullable=True,
            comment="ID en fonction des portails propriétaire",
        )
        id_ref = Column(
            String(30), unique=True, nullable=True, comment="ID REF des auteurs"
        )
        nom = Column(String(255), comment="Nom")
        prenom = Column(String(255), comment="Prénom")

        # Relationships
        authored_books = relationship("AuthorBook", back_populates="author")
        authored_reviews = relationship("AuthorReview", back_populates="author")

    class Book(CommonMixin, db.Model):
        __tablename__ = "ouvrage"

        id_proprio = Column(
            String(128),
            unique=True,
            nullable=True,
            comment="ID en fonction des portails propriétaire",
        )
        doi = Column(String(64), nullable=True)
        titre = Column(String(1024), nullable=False)
        sous_titre = Column(String(1024), nullable=True)
        traduit_par = Column(
            String(512),
            nullable=True,
            comment="Nom et Prénom du traducteur du texte intégral",
        )
        langue = Column(
            String(2), nullable=True, comment="Langue originale du texte intégral"
        )
        volume = Column(String(32), nullable=True)
        annee_parution = Column(String(4), nullable=False, comment="Année de parution")
        editeur = Column(String(128), nullable=False)
        ean = Column(String(20), nullable=False, comment="EAN")
        portail = Column(String(512), nullable=True, comment="Portail")
        url = Column(
            String(512), nullable=True, comment="Url de consultation de l'ouvrage"
        )

        # Relationships
        book_authors = relationship("AuthorBook", back_populates="book")
        book_reviews = relationship("BookReview", back_populates="book")

    class Review(CommonMixin, db.Model):
        __tablename__ = "recension"

        id_proprio = Column(
            String(128),
            unique=True,
            nullable=True,
            comment="ID en fonction des portails propriétaire",
        )
        titre = Column(String(1024), nullable=False)
        sous_titre = Column(String(1024), nullable=True)
        portail = Column(String(512), nullable=True, comment="Portail")
        traduit_par = Column(
            String(512),
            nullable=True,
            comment="Nom et Prénom du traducteur du texte intégral",
        )
        langue = Column(
            String(2), nullable=True, comment="Langue originale du texte intégral"
        )
        titre_revue = Column(
            String(1024),
            nullable=False,
            comment="Titre de la revue contenant la recension",
        )
        annee = Column(
            String(4), nullable=False, comment="Année de parution de la revue"
        )
        volume = Column(String(32), nullable=True, comment="Volume de la revue")
        numero = Column(String(32), nullable=True, comment="Numéro de revue")
        date_parution = Column(
            Date, nullable=True, comment="Date complète de la parution"
        )
        doi = Column(String(64), nullable=True)
        url = Column(String(512), nullable=False)

        # Relationships
        review_authors = relationship("AuthorReview", back_populates="review")
        review_books = relationship("BookReview", back_populates="review")

    class AuthorBook(CommonMixin, db.Model):
        __tablename__ = "auteur_ouvrage"

        id_auteur = Column(Integer, ForeignKey("auteur.id"), nullable=False)
        id_ouvrage = Column(Integer, ForeignKey("ouvrage.id"), nullable=False)

        # Relationships
        author = relationship("Author", back_populates="authored_books")
        book = relationship("Book", back_populates="book_authors")

    class AuthorReview(CommonMixin, db.Model):
        __tablename__ = "auteur_recension"

        id_auteur = Column(Integer, ForeignKey("auteur.id"), nullable=False)
        id_recension = Column(Integer, ForeignKey("recension.id"), nullable=False)

        # Relationships
        author = relationship("Author", back_populates="authored_reviews")
        review = relationship("Review", back_populates="review_authors")

    class BookReview(CommonMixin, db.Model):
        __tablename__ = "ouvrage_recension"

        id_ouvrage = Column(Integer, ForeignKey("ouvrage.id"), nullable=False)
        id_recension = Column(Integer, ForeignKey("recension.id"), nullable=False)

        # Relationships
        book = relationship("Book", back_populates="book_reviews")
        review = relationship("Review", back_populates="review_books")

    class User(CommonMixin, PasswordMixin, db.Model):
        __tablename__ = "user"

        username = Column(String(128), nullable=False)
        id_portail = Column(String(20), nullable=False)

    class Editor(CommonMixin, db.Model):
        __tablename__ = "editeur"

        nom = Column(String(256), nullable=False)

    class Journal(CommonMixin, db.Model):
        __tablename__ = "revue"

        titre = Column(String(256), nullable=False)
