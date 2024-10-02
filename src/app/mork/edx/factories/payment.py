"""Factory classes for payment models."""

import factory

from mork.edx.models.payment import PaymentUseracceptance

from .base import session


class EdxPaymentUseracceptanceFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `payment_useracceptance` table."""

    class Meta:
        """Factory configuration."""

        model = PaymentUseracceptance
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    terms_id = factory.Sequence(lambda n: n + 1)
    datetime = factory.Faker("date_time")
