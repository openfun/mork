"""Factory classes for generating fake data for testing."""

import factory

from mork import models


class EmailStatusFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating fake email status entries."""

    class Meta:
        """Factory configuration."""

        model = models.EmailStatus

    email = factory.Faker("email")
    sent_date = factory.Faker("date_time")
