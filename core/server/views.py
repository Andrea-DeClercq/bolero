#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from collections import OrderedDict
from collections.abc import Iterable, Mapping
from functools import wraps
from secrets import token_hex
from typing import Union
from enum import Enum as _Enum
import inspect

# Imports from external libraries
from box import Box
from flask import request, Response
from flask_restx import Resource as _BaseResource, Api as _BaseApi
from marshmallow import Schema as _BaseSchema, pre_load, post_load, fields, validate
from marshmallow.utils import is_collection
from marshmallow_enum import EnumField
from werkzeug.datastructures import MultiDict
from werkzeug.wrappers.response import Response as WerkeugResponse

# Import from local code
from core.services.tools_belt import humps
from core.server.json_encoder import normalize_json_response
from core.server.error import app_handle_error


__all__ = [
    "Api",
    "fields",
    "req",
    "res",
    "Resource",
    "Schema",
    "validate",
]
# TODO: Je modifie marshmallow.fields directement, c'est dégoutant, il faudrait faire un truc plus propre


####################################################################################################
# Ajout de fields pour marshmallow
####################################################################################################
class ListOr(fields.List):
    """
    Les dictionnaires utilisés par werkzeug permettent de récupérer des paramètres sous forme
    de liste si une clé est passée consécutivement.
    Par exemple, dans l'url :
        http://localhost/?param=a&param=b&param=c
    On peut ainsi récupérer le param sous la forme d'une liste ['a', 'b', 'c'] dans marshmallow

    https://werkzeug.palletsprojects.com/en/1.0.x/datastructures/#werkzeug.datastructures.MultiDict.getlist
    """

    def _deserialize(self, value, *args, **kwargs):
        """
        Récupère une liste
        """
        if not is_collection(value):
            value = [value]
        return super()._deserialize(value, *args, **kwargs)


class NestedDict(fields.Nested):
    def __init__(self, nested, *args, **kwargs):
        if isinstance(nested, dict):
            nested = Schema.from_dict(nested)
        super().__init__(nested, *args, **kwargs)


class Enum(EnumField):
    def __init__(self, enum, *args, **kwargs):
        if isinstance(enum, _Enum):
            pass
        elif isinstance(enum, Mapping):
            enum = _Enum("SubEnum", enum)
        elif isinstance(enum, Iterable):
            enum = _Enum("SubEnum", {attr.name: attr for attr in enum})
        else:
            raise NotImplementedError()
        super().__init__(enum, *args, **kwargs)

    # def _deserialize_by_value(self, value, attr, data):
    #     try:
    #         breakpoint()
    #         return getattr(self.enum, value)
    #     except ValueError:
    #         return super()._deserialize_by_value(value, attr, data)


class _CustomString(fields.String):
    def _transform_string(self, string):
        raise NotImplementedError()

    def _serialize(self, *args, **kwargs):
        string = super()._serialize(*args, **kwargs)
        return self._transform_string(string)

    def _deserialize(self, *args, **kwargs):
        string = super()._serialize(*args, **kwargs)
        return self._transform_string(string)


class LowerString(fields.String):
    def _transform_string(self, string):
        return string.lower()


class UpperString(fields.String):
    def _transform_string(self, string):
        return string.upper()


fields.ListOr = ListOr
fields.NestedDict = NestedDict
fields.Enum = EnumField
fields.LowerString = LowerString
fields.UpperString = UpperString


####################################################################################################
# Validateurs
####################################################################################################


####################################################################################################
# Mécanique
####################################################################################################
class Schema(_BaseSchema):
    """
    Permet de normaliser les schémas marshmallow vers underscore_case
    """

    @pre_load
    def to_snake_case(self, data, **kwargs):
        if isinstance(data, MultiDict):
            # On formalise les peudo-listes dans les requêtes, Flask transformant ça en MultiDict.
            data = {k: (v[0] if len(v) == 1 else v) for k, v in data.lists()}
        return humps.snakize(data)

    @post_load
    def to_box(self, data, **kwargs):  # pylint: disable=W0613
        """Transforme un objet envoyé au schéma"""
        return Box(data)

    @classmethod
    def extend(cls, dict_fields=None, **kwargs):
        """
        Permet d'étendre un schéma via un dictionnaire
        """
        name = f"{cls.__name__}_{token_hex(4)}"
        fields = dict()
        if dict_fields:
            fields.update(dict_fields)
        fields.update(kwargs)
        return type(name, (cls,), fields)


class Api(_BaseApi):
    """API basée sur Flask-RESTX avec Swagger intégré"""

    def __init__(
        self,
        app=None,
        version="1.0",
        title="Boléro API",
        description="Documentation de l'API Boléro",
        *args,
        **kwargs,
    ):
        super().__init__(
            app, version=version, title=title, description=description, *args, **kwargs
        )

    def handle_error(self, e):
        """
        Laissons flask gérer, c'est déjà fait dans error.py
        """
        raise e


class Resource(_BaseResource):
    """
    Base pour toutes les ressources de l'API
    """

    def handle_error(self, e):
        """Laissons flask gérer, c'est déjà fait dans error.py"""
        return app_handle_error(e)


class req:  # pylint: disable=C0103
    """
    Permet de récupérer les données depuis flask.request et de leur appliquer un traitement
    via marshmallow.Schema.
    Les paramètres sont ensuite fournis en premier paramètre à la fonction décorée.

    TODO: Permettre d'auto-documenter l'api
    """

    def __init__(self, schema: Union[Schema, dict], source=None, **kwargs):
        if isinstance(schema, dict):
            schema = Schema.from_dict(schema)
        if inspect.isclass(schema):
            schema = schema(**kwargs)
        self._schema = schema
        self._source = source

    def _default_fetch_source(self, meth):
        if meth.__name__ in ["get", "head", "options", "trace", "connect", "delete"]:
            source = "args"
        elif meth.__name__ in ["post", "put", "patch"]:
            source = "json"
        else:
            raise NotImplementedError()
        return source

    def _default_fetch_params(self, request_, source):
        """
        Permet de récupérer la donnée précise dans l'objet requête (param GET, body, json, etc.)
        """
        if isinstance(source, list):
            # Permet de fusionner plusieurs sources en un seul dict de params
            # À utiliser avec parcimonie !
            params = dict()
            for subsource in source:
                params.update(self._default_fetch_params(request_, subsource))
            return params
        if isinstance(source, str):
            return getattr(request_, source)
        if callable(source):
            return source(request_)
        raise NotImplementedError()

    def _default_exc_meth(self, other, meth, *args, **kwargs):
        params = self._default_fetch_params(request, self._source)
        params = self._schema.load(params)
        return meth(other, params, *args, **kwargs)

    def __call__(self, meth):
        if self._source is None:
            self._source = self._default_fetch_source(meth)

        @wraps(meth)
        def inject_pre_schema(other, *args, **kwargs):
            return self._default_exc_meth(other, meth, *args, **kwargs)

        return inject_pre_schema


class res:  # pylint: disable=C0103
    """
    Formatte et vérifie les données renvoyées.

    TODO: autodocumenter la réponse
    """

    def __init__(self, schema: Union[Schema, dict], **kwargs):
        if isinstance(schema, dict):
            schema = Schema.from_dict(schema)
        if inspect.isclass(schema):
            schema = schema(**kwargs)
        self._schema = schema

    def __call__(self, meth):
        @wraps(meth)
        def inject_post_schema(*args, **kwargs):
            response = meth(*args, **kwargs)
            # Je me suis basé sur ça :
            # https://flask.palletsprojects.com/en/1.1.x/quickstart/#about-responses
            if isinstance(response, (str, int, Response, WerkeugResponse)):
                return response
            if isinstance(response, tuple):
                # TODO: Un peu dégueu, à refaire
                if 1 <= len(response) <= 3:
                    if isinstance(response[0], str):
                        return response
                    if isinstance(response[0], Response):
                        return response
                    return (self._schema.dump(response[0]),) + response[1:]
            response = self._schema.dump(response)
            return response

        return inject_post_schema
