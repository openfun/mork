"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.util import UtilRatelimitconfiguration

from .base import session


class EdxUtilRatelimitconfigurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Model for the `util_ratelimitconfiguration` table."""

    class Meta:
        """Factory configuration."""

        model = UtilRatelimitconfiguration
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = factory.Faker("random_int", min=0, max=1)