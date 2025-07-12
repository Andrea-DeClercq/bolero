#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
from flask import request, jsonify, make_response
from flask.json.provider import DefaultJSONProvider

# Import from local code
from core.services.tools_belt import humps
from core.services.jsonlib import default


###############################################################################
# Encodage des JSON
###############################################################################
class JSONProvider(DefaultJSONProvider):
    """
    Encodeur vers JSON
    """

    default = staticmethod(default)


####################################################################################################
# Normalisation des réponses
####################################################################################################
mapping_attributes_convention = {
    "camel-case": humps.camelize,
    "snake-case": humps.snakize,
    "dash-case": humps.dasherize,
    "without-convention": lambda d: d,
}


def normalize_json_response(data, code, headers=None):
    data = {
        "status": code,
        "type": "response" if code < 400 else "error",
        "data": data,
    }
    # Permet de formatter la réponse JSON suivant ce que l'on souhaite côté client
    # Très pratique pour utiliser du underscore dans le cas d'un appel python, du camelCase dans
    # le cas d'un client javascript, etc.
    attribute_convention = "dash-case"
    if request:
        attribute_convention = request.headers.get(
            "Attribute-Convention", attribute_convention
        )
        fn_convention = mapping_attributes_convention.get(
            request.headers.get("Attribute-Convention"),
            mapping_attributes_convention["dash-case"],
        )
        data = fn_convention(data)
    # Transformation de la réponse en JSON
    response = make_response(jsonify(data), code)
    # Ajouts d'informations supplémentaires dans la réponse
    response.headers["Content-Type"] = "application/json"
    response.headers["Attribute-Convention"] = attribute_convention
    response.status_code = code
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response


def normalize_json_error(name, description, code, headers=None):
    return normalize_json_response(
        {"name": name, "description": description}, code, headers
    )
