"""Factory classes for notify models."""

import factory

from mork.edx.mysql.models.notify import NotifySetting

from .base import BaseSQLAlchemyModelFactory


class EdxNotifySettingFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `notify_settings` table."""

    class Meta:
        """Factory configuration."""

        model = NotifySetting

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    interval = factory.Sequence(lambda n: n)
