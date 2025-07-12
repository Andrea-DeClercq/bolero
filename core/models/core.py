#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from types import MethodType

# Imports from external libraries
from box import Box, BoxList
from marshmallow import Schema, INCLUDE
from marshmallow_sqlalchemy import fields_for_model
from sqlalchemy import MetaData, inspect, Table, select, exc, DateTime
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.engine import make_url
from sqlalchemy.event import listens_for
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.clsregistry import _MultipleClassMarker
from sqlalchemy_utils import ArrowType
from sqlservice import (
    ModelBase,
    as_declarative,
    SQLClient as _SQLClient,
    SQLQuery as _SQLQuery,
)
from sqlservice.model import get_model_class_registry

# Import from local code
from .utils import normalize_column_name, normalize_table_name


def _normalize_table_name(base, tablename, table):
    return normalize_table_name(tablename)


class DeepAttributeException(Exception):
    pass


@listens_for(Table, "column_reflect")
def _normalize_column_name(inspector, table, column_info):
    # Normalisation du nom de la colonne
    column_info["key"] = normalize_column_name(column_info["name"])
    # Remplacement du type DateTime par un type Arrow systématiquement
    if isinstance(column_info["type"], DateTime):
        column_info["type"] = ArrowType()


class ModelReprMixin:
    __format__ = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.to_dict = MethodType(super().to_dict, instance)
        return instance

    @classmethod
    def to_dict(cls):
        """
        Fix dégoutant pour l'intégration avec le paquet Box qui appelle
        des méthodes .to_dict()
        """
        return cls

    def __repr__(self):
        format_ = self.__format__
        if format_ is None:
            format_ = inspect(self).identity
        repr_ = "<{} {}>".format(self.__class__.__name__, format_)
        repr_ = repr_.format(self=self)
        return repr_

    @classmethod
    def marshmallow(cls):
        fields = fields_for_model(cls)
        fields = {k: v for k, v in fields.items() if getattr(v, "OBJ_TYPE", None) not in ["datetime"]}
        return Schema.from_dict(fields)(unknown=INCLUDE)


class SQLQuery(_SQLQuery):
    def upsert(self, values, values_on_duplicate=None):
        """
        Permet de générer des requêtes INSERT ON DUPLICATE KEY
        Les requêtes doivent ensuite être exécutés dans un engine
        """
        if values_on_duplicate is None:
            values_on_duplicate = values
        return insert(self.model_class).values(values).on_duplicate_key_update(values_on_duplicate)


class SQLClient(_SQLClient):
    def __init__(self, *args, **kwargs):
        self._models = Box()
        self._queries = Box()
        self._tables = Box()
        self._enums = Box()
        self._setup_db = kwargs.pop("setup", None)
        self._bind_key = kwargs.pop("bind_key", None)
        self._module_key = kwargs.pop("module_key", None)
        self._format_tablename = kwargs.pop("table_case", "same")
        # On définit un modèle de base par défaut
        if "model_class" not in kwargs:
            kwargs["model_class"] = self._make_model_class(kwargs["database_uri"])
        # Définition d'une classe custom par défaut pour les requêtes
        kwargs.setdefault("query_class", SQLQuery)
        super().__init__(*args, **kwargs)
        # On ping à chaque fois qu'on crée une nouvelle session
        listens_for(self.engine, "engine_connect")(self.ping_connection)
        self._post_init_client()

    def _post_init_client(self):
        if not self._setup_db:
            return
        self._setup_db(self)
        self.update_models_registry()

    def _make_model_class(self, db_uri):
        """
        Retourne un modèle de base avec des mixins supplémentaires
        """
        db_uri = make_url(db_uri)
        metadata = MetaData(schema=db_uri.database)
        Model = type("Model", (ModelReprMixin, ModelBase), {"_bind_key": self.bind_key, "_bind_client": self})
        Model = as_declarative(metadata=metadata)(Model)
        return Model

    def ping_connection(self, connection, branch):
        # Voir https://docs.sqlalchemy.org/en/latest/core/pooling.html#custom-legacy-pessimistic-ping
        if branch:
            return
        save_should_close_with_result = connection.should_close_with_result
        connection.should_close_with_result = False

        try:
            connection.scalar(select([1]))
        except exc.DBAPIError as err:
            if err.connection_invalidated:
                connection.scalar(select([1]))
            else:
                raise
        finally:
            connection.should_close_with_result = save_should_close_with_result

    def save(self, models, *args, **kwargs):
        """
        Surcharge pour gérer les instances de la bibliothèque Box
        """
        if isinstance(models, BoxList):
            models = models.to_list()
        return super().save(models, *args, **kwargs)

    def format_tablename(self, tablename):
        if self._format_tablename == "same":
            return tablename
        elif self._format_tablename == "upper":
            return tablename.upper()
        elif self._format_tablename == "lower":
            return tablename.lower()
        raise NotImplementedError()

    @property
    def bind_key(self):
        return self._bind_key

    @property
    def Model(self):
        return self.model_class

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, models):
        if not isinstance(models, Box):
            models = Box(models)
        self._models = models
        self._tables = Box({k: m.__table__ for k, m in self._models.items()})
        # Les requêtes dépendant de la session actuelle, on ne peut pas enregistrer à l'avance
        # les instances query sous peine d'utiliser la même session partout
        Queries = type("Queries", (), {})
        for key, model in self._models.items():

            def get_property(db, Model):
                return property(lambda _: db.query(Model))

            setattr(Queries, key, get_property(self, model))
        self._queries = Queries()

    @property
    def queries(self):
        return self._queries

    @property
    def tables(self):
        return self._tables

    @property
    def enums(self):
        """
        Prévu pour être enrichi par les modules, permettant d'ajouter des instance de type enum.Enum
        """
        return self._enums

    def __getattr__(self, attr):
        """
        La récupération implicite des requêtes liées à une classe étant trop source de confusion,
        préférez utiliser les attributs models et queries
        """
        raise AttributeError(f"type object {self.__class__.__name__!r} has no attribute {attr!r}")


class SQLAutomapClient(SQLClient):
    def __init__(self, *args, **kwargs):
        self._has_been_reflect = False
        self._AutomapBase = None

        # Définition du modèle de base qui sera utilisé
        # Il ne peut pas être modifié dans le cas de l'automap
        if "model_class" in kwargs:
            raise AttributeError("Le paramètre model_class ne peut être redéfini")

        # Appel de la méthode parente
        # Il est important de le faire avant l'automap car il a besoin
        # de l'engine et des metadata.
        # Il est important de le faire après la définition du Model car
        # les mécaniques se feront par rapport à celui-ci
        super().__init__(*args, **kwargs)

        # Définition de l'automap
        self._AutomapBase = automap_base(
            bind=self.engine,
            metadata=self.metadata,
            cls=self.Model,
        )

    def _post_init_client(self):
        return

    def create_models_registry(self, model_class):
        """
        Surcharge de la méthode parente afin de pouvoir gérer les conflits entre les models récupérés
        directement depuis l'automap et ceux définis manuellement.
        """
        models = {}
        class_registry = get_model_class_registry(model_class)
        if not class_registry:
            return models

        registery = model_class.registry
        classes = class_registry
        subclasses = self.Base.__subclasses__()
        for name, model in class_registry.items():
            if name.startswith("_sa_"):
                continue

            if isinstance(model, _MultipleClassMarker):
                model = list(model)
                # Par défaut, sqlservice va ajouter le namespace du module à la clé du model si
                # une classe de l'automap est enrichie par héritage.
                # Suppression de la classe de l'automap pour corriger cela
                if len(model) > 1:
                    model_without_automap = [m for m in model if not issubclass(m, self._AutomapBase)]
                    if len(model_without_automap) == 1:
                        model = model_without_automap
                # Retour à la boucle normale de sqlservice
                if len(model) == 1:  # pragma: no cover
                    models[name] = model[0]
                else:
                    for obj in model:
                        modobj = f"{obj.__module__}.{obj.__name__}"
                        models[modobj] = obj
            else:
                models[name] = model

        return models

    def update_models_registry(self):
        super().update_models_registry()
        if not self._AutomapBase:
            return
        # On fusionne l'automap et ce qui est calculé par la classe parente
        models = self.create_models_registry(self._AutomapBase)
        models.update(self.models)
        self.models = models

    def reflect(self, *args, **kwargs):
        if self._has_been_reflect:
            # Je ne sais pas vraiment à quel moment il faut appeler
            # la fonction self.update_models_registry
            # Je l'ai foutu au cul du reflect, mais je n'ai pas encore
            # bien compris les effets que ça pouvoit avoir
            # si on l'appelle deux fois.
            # Par conséquent, par sécurité, je limite le nombre de fois
            # où on peut reflect
            raise NotImplementedError("La méthode reflect ne peut pas être appelé deux fois")
        self._has_been_reflect = True
        if self._setup_db:
            try:
                self._setup_db(self)
            except AttributeError as err:
                raise DeepAttributeException(f"{err!r}") from err
        self.models.update({c.__name__: c for c in self.Base.__subclasses__()})
        self.Base.prepare(
            autoload_with=self.engine,
            classname_for_table=_normalize_table_name,
            generate_relationship=lambda *args, **kwargs: None,
            reflection_options={"views": True},
        )
        super().reflect(*args, **kwargs)
        self.update_models_registry()

    @property
    def Base(self):
        return self._AutomapBase

    @property
    def models(self):
        if not self._has_been_reflect:
            self.reflect()
        return SQLClient.models.fget(self)

    @models.setter
    def models(self, models):
        SQLClient.models.fset(self, models)

    @property
    def queries(self):
        if not self._has_been_reflect:
            self.reflect()
        return self._queries

    @property
    def tables(self):
        if not self._has_been_reflect:
            self.reflect()
        return self._tables
