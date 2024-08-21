"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.notify import NotifySetting

from .base import session


class EdxNotifySettingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `notify_settings` table."""

    class Meta:
        """Factory configuration."""

        model = NotifySetting
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    interval = factory.Sequence(lambda n: n)
