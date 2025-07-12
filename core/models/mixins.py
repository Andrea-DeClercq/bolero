#!/usr/bin/env python
"""
Source pour le timestamp :
    https://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/models.html#Timestamp
"""
# Import from stdlib

# Imports from external libraries
from flask_jwt_extended import current_user
from sqlalchemy import Column, String, Integer, DDL
from sqlalchemy.event import listen, listens_for
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates, deferred
from sqlalchemy_utils import ArrowType
from werkzeug.security import check_password_hash, generate_password_hash

# Import from local code


####################################################################################################
# Tracking
####################################################################################################
class TimestampMixin:
    """
    Ajout de deux colonnes temporelles permettant de suivre les modifications.
    Ici, c'est en declared_attr juste pour forcer ces deux colonnes à être en fin de table dans
    l'ordre des colonnes. C'est purement cosmétique.
    """

    @declared_attr
    def cree_le(self):
        """ Création de la ligne """
        return Column(
            ArrowType,
            comment="Datetime UTC de création",
        )

    @declared_attr
    def modifie_le(self):
        """ Dernière modification de la ligne """
        return Column(
            ArrowType,
            comment="Datetime UTC de dernière modification",
        )


@listens_for(TimestampMixin, "instrument_class", propagate=True)
def instrument_timestamp_class(mapper, _):
    """
    Permet d'ajouter un trigger sur les colonnes d'horodatages
    """
    if mapper.local_table is None:
        return
    listen(
        mapper.local_table,
        "after_create",
        DDL(
            """
                CREATE TRIGGER %(before_insert_trigger)s BEFORE INSERT ON %(table)s
                 FOR EACH ROW BEGIN
                    SET new.cree_le = UTC_TIMESTAMP(), new.modifie_le = UTC_TIMESTAMP();
                END;
                CREATE TRIGGER %(before_update_trigger)s BEFORE UPDATE ON %(table)s
                 FOR EACH ROW BEGIN
                    SET new.modifie_le = UTC_TIMESTAMP();
                END;
        """,
            context={
                "before_insert_trigger": f"before_insert_{mapper.local_table.name}",
                "before_update_trigger": f"before_update_{mapper.local_table.name}",
            },
        ),
    )


class PeoplestampMixin:
    @declared_attr
    def created_by(self):
        return Column(String(255), comment="Le créateur")

    @declared_attr
    def modified_by(self):
        return Column(String(255), comment="Le modeleur")


@listens_for(PeoplestampMixin, "before_insert", propagate=True)
def before_insert(mapper, connection, target):
    if not current_user:
        return
    target.created_by = current_user.id
    target.modified_by = current_user.id


@listens_for(PeoplestampMixin, "before_update", propagate=True)
def before_update(mapper, connection, target):
    if not current_user:
        return
    target.modified_by = current_user.id


class TrackingMixin(TimestampMixin):
    pass


####################################################################################################
# Mot de passe
####################################################################################################
class PasswordMixin:
    """
    Gestion d'un mot de passe
    """

    @declared_attr
    def password(self):
        """
        En declared_attr pour qu'il soit pas la première colonne.
        Purement cosmétique.
        Cette colonne contenant une donnée sensible, on la charge seulement à l'utilisation.
        to_dict() sans utiliser l'attribut password directement renverra un utilisateur sans mdp.
        """
        return deferred(Column(String(255), nullable=False))

    # TODO: Peut être faire plutôt un type Password
    @validates("password")
    def validate_password(self, _, password):
        """
        Enregistre l'empreinte du mot de passe.
        """
        return generate_password_hash(password)

    def check_password(self, password):
        """
        Vérifie le mot de passe en clair fourni par rapport à l'empreinte du mot de passe enregistré
        """
        return check_password_hash(self.password, password)


####################################################################################################
# Classe de base
####################################################################################################
class CommonMixin(TrackingMixin):
    """
    Parce que la plupart des nouveaux modèles ont au moins des colonnes en commun
    """

    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)


class ManyToManyMixin(TrackingMixin):
    """
    Les clés primaires varient sur les tables many-to-many
    """

    @declared_attr
    def __table_args__(self):
        return {
            "extend_existing": True,
        }
