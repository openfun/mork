"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.contentstore import ContentstoreVideouploadconfig

from .base import session


class EdxContentstoreVideouploadconfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Model for the `contentstore_videouploadconfig` table."""

    class Meta:
        """Factory configuration."""

        model = ContentstoreVideouploadconfig
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = factory.Faker("random_int", min=0, max=1)
    profile_whitelist = factory.Faker("pystr")
