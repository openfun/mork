"""Factory classes for contentstore models."""

import factory

from mork.edx.mysql.models.contentstore import ContentstoreVideouploadconfig

from .base import BaseSQLAlchemyModelFactory


class EdxContentstoreVideouploadconfigFactory(BaseSQLAlchemyModelFactory):
    """Model for the `contentstore_videouploadconfig` table."""

    class Meta:
        """Factory configuration."""

        model = ContentstoreVideouploadconfig

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = factory.Faker("random_int", min=0, max=1)
    profile_whitelist = factory.Faker("pystr")
