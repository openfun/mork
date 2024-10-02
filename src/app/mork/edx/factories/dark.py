"""Factory classes for dark models."""

import factory

from mork.edx.models.dark import DarkLangDarklangconfig

from .base import session


class EdxDarkLangDarklangconfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `dark_lang_darklangconfig` table."""

    class Meta:
        """Factory configuration."""

        model = DarkLangDarklangconfig
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = factory.Faker("random_int", min=0, max=1)
    released_languages = factory.Faker("pystr")
