"""Factory classes for django models."""

import factory

from mork.edx.mysql.models.django import DjangoCommentClientRoleUsers

from .base import BaseSQLAlchemyModelFactory


class EdxDjangoCommentClientRoleUsersFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `django_comment_client_role_users` table."""

    class Meta:
        """Factory configuration."""

        model = DjangoCommentClientRoleUsers

    id = factory.Sequence(lambda n: n + 1)
    role_id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
