#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib

# Imports from external libraries
from flask import g, request
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
import vakt

# Import from local code
from .auth import current_user


__all__ = [
    "RbacUserMixin",
    "RbacRoleMixin",
    "RbacUserRoleAssociationMixin",
]


####################################################################################################
# Mixins modèles sql
####################################################################################################
class RbacUserMixin:
    # Relations
    @declared_attr
    def assoc_roles(self):
        return relationship("UserRoleAssociation", back_populates="user")

    @declared_attr
    def roles(self):
        return association_proxy("assoc_roles", "role")


class RbacRoleMixin:
    # Colonnes
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="L'identifiant textuel alternatif du rôle",
    )
    # Relations
    @declared_attr
    def assoc_users(self):
        return relationship("UserRoleAssociation", back_populates="role")

    @declared_attr
    def users(self):
        return association_proxy("assoc_users", "user")


class RbacUserRoleAssociationMixin:
    # Clés étrangères
    @declared_attr
    def id_user(self):
        return Column(Integer, ForeignKey("user.id"))

    @declared_attr
    def id_role(self):
        return Column(Integer, ForeignKey("role.id"))

    # Relations
    @declared_attr
    def user(self):
        return relationship("User", back_populates="assoc_roles")

    @declared_attr
    def role(self):
        return relationship("Role", back_populates="assoc_users")


####################################################################################################
# Mécanique pour utiliser le module rbac
####################################################################################################
class role_required:
    def __init__(self, role):
        self.role = role

    def __call__(self, func):
        print(func.__qualname__)

        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped_func


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from vakt.storage.sql import SQLStorage
# from vakt.storage.sql.migrations import SQLMigrationSet
# from vakt.storage.migration import Migrator

# engine = create_engine("mysql://root:221182@localhost/vakt")
# # rbac_storage = vakt.MemoryStorage()
# rbac_storage = SQLStorage(scoped_session=scoped_session(sessionmaker(bind=engine)))
# migrator = Migrator(SQLMigrationSet(rbac_storage))
# migrator.up()

# rbac_guard = vakt.Guard(rbac_storage, vakt.RulesChecker())
# from uuid import uuid4

# admin_policy = vakt.PolicyAllow(
#     str(uuid4()),
#     description="Accès administrateur",
#     actions=[
#         vakt.rules.Any(),
#     ],
#     resources=[
#         vakt.rules.Any(),
#     ],
#     subjects=[
#         {
#             "user": vakt.rules.In(1),
#         }
#     ],
# )
# rbac_storage.add(admin_policy)


# def setup_resources(api, app):
#     @app.before_request
#     def is_authorized():
#         breakpoint()
#         inquiry = vakt.Inquiry(
#             action=request.method.lower(),
#             resource={"endpoint": request.endpoint},
#             subject={"user": g.current_user},
#         )
#         if rbac_guard.is_allowed(inquiry):
#             return
#         return "Forbidden", 403
