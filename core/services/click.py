#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
import click

# Import from local code


class CommaListParamType(click.ParamType):
    name = "commalist"

    def convert(self, value, param, ctx):
        return [s for s in value.split(",") if s]


COMMA_LIST = CommaListParamType()
