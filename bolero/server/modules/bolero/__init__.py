#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
# Import from stdlib

# Imports from external libraries

# Import from local code
from .authors import Authors
from .books import Books
from .reviews import Reviews
from .relations import Relations
from .editors import Editors
from .journals import Journals
from core.server.documentation.models import (
    ns_authors,
    ns_books,
    ns_reviews,
    ns_relations,
    ns_editors,
    ns_journals,
)


def setup_resources(api, app):
    api.add_namespace(ns_authors, path=f"/bolero")
    api.add_namespace(ns_books, path=f"/bolero")
    api.add_namespace(ns_reviews, path=f"/bolero")
    api.add_namespace(ns_relations, path=f"/bolero")
    api.add_namespace(ns_editors, path=f"/bolero")
    api.add_namespace(ns_journals, path=f"/bolero")
