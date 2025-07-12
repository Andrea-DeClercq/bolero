#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commandes CLI pour gérer les utilisateurs.
"""

# Import from stdlib


# Imports from external libraries
import click

# Import from local code
from bolero.models import databases
from bolero.server import app


def setup(app, cli_group):
    @cli_group.command("create-user")
    @click.option("--username", prompt=True, help="Identifiant de l'utilisateur")
    @click.option(
        "--password",
        prompt=True,
        hide_input=False,
        confirmation_prompt=True,
        help="Mot de passe de l'utilisateur",
    )
    @click.option(
        "--id-portail",
        prompt="ID Portail",
        help="Identifiant du portail de l'utilisateur",
    )
    def create_user(username, password, id_portail):
        """
        Commande pour créer un utilisateur avec un mot de passe hashé.
        """
        with app.app_context():
            # Créer une nouvelle session SQLAlchemy
            session = databases.bolero.session
            user = databases.bolero.models.User

            # Vérifier si un utilisateur avec le même username existe déjà
            existing_user = session.query(user).filter_by(username=username).first()
            if existing_user:
                click.echo("Un utilisateur avec ce username existe déjà.")
                return

            new_user = user(
                username=username,
                password=password,
                id_portail=id_portail,
            )

            try:
                session.add(new_user)
                session.commit()
                click.echo(f"Utilisateur '{username}' créé avec succès.")
            except Exception as e:
                session.rollback()
                click.echo(f"Erreur lors de la création de l'utilisateur : {e}")
            finally:
                session.close()