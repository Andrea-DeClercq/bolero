#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
import traceback

# Imports from external libraries
from box import Box

# Import from local code


class _BaseExceptionBox(Box):
    """
    Permet de sérialiser une erreur
    """

    @classmethod
    def err_to_dict(cls, err: BaseException):
        return {
            "type": err.__class__.__name__,
            "message": str(err),
        }

    def __init__(self, err: BaseException):
        super().__init__(self.err_to_dict(err))


class WithPrivacyExceptionBox(_BaseExceptionBox):
    """
    Sans inclure la traceback
    """

    @classmethod
    def err_to_dict(cls, err: BaseException):
        data = super().err_to_dict(err)
        data["traceback"] = None
        return data


class WithoutPrivacyExceptionBox(_BaseExceptionBox):
    """
    En incluant la traceback
    """

    @classmethod
    def err_to_dict(cls, err: BaseException):
        data = super().err_to_dict(err)
        data["traceback"] = "".join(traceback.format_tb(err.__traceback__))
        return data
