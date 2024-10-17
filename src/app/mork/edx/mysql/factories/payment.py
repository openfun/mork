"""Factory classes for payment models."""

import factory

from mork.edx.mysql.models.payment import PaymentUseracceptance

from .base import BaseSQLAlchemyModelFactory


class EdxPaymentUseracceptanceFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `payment_useracceptance` table."""

    class Meta:
        """Factory configuration."""

        model = PaymentUseracceptance

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    terms_id = factory.Sequence(lambda n: n + 1)
    datetime = factory.Faker("date_time")
