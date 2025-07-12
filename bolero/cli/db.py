#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
import click

# Import from local code
from bolero.models import databases
from bolero.server import app


def setup(app, cli_group):
    # Revoir la création, si base non créer cela fonctionne pas
    @cli_group.command("create")
    def create_db():
        """Create database and tables"""
        with app.app_context():
            engine = databases.bolero.engine
            session = databases.bolero.session

            engine.execute("CREATE DATABASE IF NOT EXISTS bolero")
            session.execute("USE bolero")
            databases.bolero.create_all()

        print("Database and tables successfully created.")
