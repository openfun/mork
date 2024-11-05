"""Factory classes for tasks."""

import factory

from mork.models.tasks import EmailStatus


class EmailStatusFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating fake email status entries."""

    class Meta:
        """Factory configuration."""

        model = EmailStatus

    email = factory.Faker("email")
    sent_date = factory.Faker("date_time")
