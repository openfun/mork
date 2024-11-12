"""Factory classes for users."""

import factory

from mork.models.users import (
    DeletionReason,
    DeletionStatus,
    ServiceName,
    User,
    UserServiceStatus,
)


class UserServiceStatusFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating UserServiceStatus instances."""

    class Meta:
        """Factory configuration."""

        model = UserServiceStatus

    user_id = factory.Sequence(lambda n: n + 1)
    service_name = ServiceName
    status = DeletionStatus.TO_DELETE


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating fake users."""

    class Meta:
        """Factory configuration."""

        model = User

    username = factory.Faker("pystr", max_chars=15)
    edx_user_id = factory.Sequence(lambda n: n)
    email = factory.Faker("email")
    reason = DeletionReason.GDPR

    @factory.post_generation
    def service_statuses(
        self,
        create: bool,
        extracted: dict[ServiceName, DeletionStatus] | None,
        **kwargs,
    ):
        """Post-generation hook to create UserServiceStatus for all services."""
        if not create:
            return

        service_states = {service: DeletionStatus.TO_DELETE for service in ServiceName}

        if isinstance(extracted, dict):
            service_states.update(extracted)

        for service, status in service_states.items():
            UserServiceStatusFactory(
                user=self,
                service_name=service,
                status=status,
                **kwargs,
            )
