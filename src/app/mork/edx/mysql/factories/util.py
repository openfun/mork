"""Factory classes for util models."""

import factory

from mork.edx.mysql.models.util import UtilRatelimitconfiguration

from .base import BaseSQLAlchemyModelFactory


class EdxUtilRatelimitconfigurationFactory(BaseSQLAlchemyModelFactory):
    """Model for the `util_ratelimitconfiguration` table."""

    class Meta:
        """Factory configuration."""

        model = UtilRatelimitconfiguration

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = factory.Faker("random_int", min=0, max=1)
