"""Factory classes for django models."""

import factory

from mork.edx.models.django import DjangoCommentClientRoleUsers

from .base import session


class EdxDjangoCommentClientRoleUsersFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `django_comment_client_role_users` table."""

    class Meta:
        """Factory configuration."""

        model = DjangoCommentClientRoleUsers
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    role_id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
