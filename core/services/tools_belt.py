#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from collections import UserDict
from collections.abc import Callable, Mapping
from functools import partial
from operator import attrgetter
from urllib import parse as url_parser
from typing import Iterable
import csv
import io
import mimetypes
import re

# Imports from external libraries
from marshmallow.utils import is_collection
from path import Path
import inflection

# Import from local code


__all__ = [
    "transform_collection",
    "humps",
]


####################################################################################################
# Export CSV
####################################################################################################
def generate_csv_stream(headers: list[str], rows: Iterable[Iterable]):
    """
    Génère un flux CSV ligne par ligne à partir des en-têtes et des lignes données.
    Utilise ; comme séparateur et gère les champs entre guillemets.
    """

    def generate():
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for row in rows:
            writer.writerow(row)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return generate()


def transform_collection(data, fn_key=None, fn_value=None):
    """
    Itère récursivement sur une collection (list, dict, etc.).
    Appelle fn_key sur chaque clé.
    Appelle fn_value sur tout autre chose.
    """
    if is_collection(data):
        return data.__class__(transform_collection(i, fn_key, fn_value) for i in data)
    if isinstance(data, Mapping):
        if not isinstance(fn_key, Callable):
            fn_key = lambda: data
        return {
            fn_key(k): transform_collection(v, fn_key, fn_value)
            for k, v in data.items()
        }
    if isinstance(fn_value, Callable):
        data = fn_value(data)
    return data


####################################################################################################
# Gestion des fichiers
####################################################################################################
def get_extensions_for_type(type_):
    mimetypes.init()
    extensions = list()
    for ext, mimetype in mimetypes.types_map.items():
        if type_ == mimetype.split("/")[0]:
            extensions.append(ext.lstrip("."))
    return extensions


IMAGE_EXTENSIONS = get_extensions_for_type("image")
AUDIO_EXTENSIONS = get_extensions_for_type("audio")
VIDEO_EXTENSIONS = get_extensions_for_type("video")


class FilesCollection(UserDict):
    """
    Depuis un dossier, génère un dictionnaire dont les clés sont les noms de fichiers et les valeurs
    des objets Path vers les fichiers.

    Ce dictionnaire n'accepte que des bytes comme valeurs, qui seront écrites sur le disque à l'emplacement
    défini par le dossier + clé. L'objet Path sera alors enregistré sous cette clé.
    """

    _validate_filename = re.compile(r"^[\w\s.-]+$")

    def __init__(self, directory):
        super().__init__()
        self._directory = Path(directory)
        if not self._directory.exists():
            return
        for path in self._directory.files(self._validate_path):
            self.data[str(path.name)] = path

    def __setitem__(self, key: str, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError("value must be a bytes")
        if not isinstance(key, str):
            raise TypeError("key must be a str")
        if not self._validate_filename.match(key):
            raise TypeError("key must be a valid filename without special character")
        self._directory.makedirs_p()
        path = self._directory / key
        path.write_bytes(value)
        super().__setitem__(key, path)

    def _validate_path(self, path):
        return True


class FilteredFilesCollection(FilesCollection):
    _allowed_extensions = []

    def _validate_path(self, path):
        ext = path.ext.lower().lstrip(".")
        if ext not in self._allowed_extensions:
            return False
        return super()._validate_path(path)


class ImagesCollection(FilteredFilesCollection):
    _allowed_extensions = IMAGE_EXTENSIONS


class AudioCollection(FilteredFilesCollection):
    _allowed_extensions = AUDIO_EXTENSIONS


class VideoCollection(FilteredFilesCollection):
    _allowed_extensions = VIDEO_EXTENSIONS


####################################################################################################
# Fonctions concernant la manipulation des strings et des clés de dict
####################################################################################################
class humps:
    """
    Inspiré de https://github.com/nficano/humps
    Mais je ne l'ai pas utilisé car elle a trop de défauts comme la conversion systématique depuis
    snake_case, ou des bogues dérangeants.
    """

    @classmethod
    def __transform(cls, data, fn):
        if isinstance(data, str):
            return fn(data)
        return transform_collection(data, fn)

    __camelize_string = partial(inflection.camelize, uppercase_first_letter=False)

    @classmethod
    def camelize(cls, data):
        return cls.__transform(data, cls.__camelize_string)

    __pascalize_string = partial(inflection.camelize, uppercase_first_letter=True)

    @classmethod
    def pascalize(cls, data):
        return cls.__transform(data, cls.__pascalize_string)

    @classmethod
    def dasherize(cls, data):
        return cls.__transform(data, inflection.dasherize)

    @classmethod
    def snakize(cls, data):
        return cls.__transform(data, inflection.underscore)

    @classmethod
    def humanize(cls, data):
        return cls.__transform(data, inflection.humanize)

    @classmethod
    def parameterize(cls, data):
        return cls.__transform(data, inflection.parameterize)

    @classmethod
    def tableize(cls, data):
        return cls.__transform(data, inflection.tableize)

    @classmethod
    def titleize(cls, data):
        return cls.__transform(data, inflection.titleize)

    @classmethod
    def transliterate(cls, data):
        return cls.__transform(data, inflection.transliterate)

    @classmethod
    def lowerize(cls, data):
        return cls.__transform(data, str.lower)

    @classmethod
    def upperize(cls, data):
        return cls.__transform(data, str.upper)

    @classmethod
    def striptize(cls, data):
        return cls.__transform(data, str.strip)

    @classmethod
    def ordinalize(cls, data):
        return cls.__transform(data, lambda string: [ord(c) for c in string])

    @classmethod
    def chralize(cls, data):
        return "".join(chr(int(i)) for i in data)

    @classmethod
    def urlize(cls, data):
        return cls.__transform(data, url_parser.quote)

    @classmethod
    def unurlize(cls, data):
        return cls.__transform(data, url_parser.unquote)

    @classmethod
    def urlize_plus(cls, data):
        return cls.__transform(data, url_parser.quote_plus)

    @classmethod
    def unurlize_plus(cls, data):
        return cls.__transform(data, url_parser.unquote_plus)

    @classmethod
    def chunkize(cls, data, size):
        return chunkize(data, size)


def uniq_dicts(collection):
    """
    Supprime les dictionnaires en doublon d'une collection
    """
    result = []
    index = set()
    for entry in collection:
        if not hasattr(entry, "items"):
            entry = dict(entry)
        key = tuple((k.lower(), v) for k, v in sorted(entry.items()))
        key = hash(key)
        if key in index:
            continue
        index.add(key)
        result.append(entry)
    return result


def chunkinze(collection, size):
    """Yield successive n-sized chunks from lst."""
    if not collection:
        return []
    chunks = []
    for index in range(0, len(collection), size):
        chunks.append(collection[index : index + size])
    return chunks


class Null:
    pass


def find_attr(obj, attrnames, default=Null):
    """
    Permet de retrouver un attribut en essayant les différents `attrnames`.

        >>> find_attr(str, ("lowwer", "lower"))
        <method 'lower' of 'str' objects>
        >>> find_attr(str, ("lowwer", "smaller"), "Yarien")
        'Yarien'
        >>> find_attr(str, ("lowwer", "smaller"))
        AttributeError: <class 'str'> object has no attributes in 'lowwer|smaller'
    """
    value = Null
    if isinstance(attrnames, str):
        attrnames = [attrnames]
    for attrname in attrnames:
        try:
            value = attrgetter(attrname)(obj)
        except AttributeError:
            value = Null
        if value is Null:
            continue
        break
    if value is Null:
        if default is Null:
            raise AttributeError(
                f"{obj!r} object has no attributes in {'|'.join(attrnames)!r}"
            )
        return default
    return value


####################################################################################################
# Utilitaires pour Flask
####################################################################################################
class RemapWsgiEnvMiddleware:
    """
    Permet de remapper des variables d'environnement wsgi.
    Par exemple, si l'adresse IP est bindé sur X-REAL-IP, on veut l'insérer sur REMOTE_ADDR
    pour qu'elle soit interpretée correctement dans le flux normal du programme.
    """

    def __init__(self, app, mapping, static_mapping=None):
        self.app = app
        self.mapping = mapping
        self.static_mapping = static_mapping or dict()

    def __call__(self, environ, start_response):
        for dest, orig in self.mapping.items():
            environ[dest] = environ.get(orig)
        for key, value in self.static_mapping.items():
            environ[key] = value
        return self.app(environ, start_response)
