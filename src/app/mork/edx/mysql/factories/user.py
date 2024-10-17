"""Factory classes for user models."""

import factory

from mork.edx.mysql.models.user import UserApiUserpreference

from .base import BaseSQLAlchemyModelFactory


class EdxUserApiUserpreferenceFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `user_api_userpreference` table."""

    class Meta:
        """Factory configuration."""

        model = UserApiUserpreference

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    value = factory.Faker("pystr")

    @factory.lazy_attribute
    def key(self):
        """Pick a random key from the complete list of Open edX user preferences."""
        return ["account_privacy", "dark-lang", "pref-lang"][self.id % 3]
