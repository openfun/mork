"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.verify import VerifyStudentHistoricalverificationdeadline

from .base import faker, session


class EdxVerifyStudentHistoricalverificationdeadlineFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    """Model for the `verify_student_historicalverificationdeadline` table."""

    class Meta:
        """Factory configuration."""

        model = VerifyStudentHistoricalverificationdeadline
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")
    course_key = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    deadline = factory.Faker("date_time")
    history_id = factory.Sequence(lambda n: n + 1)
    history_date = factory.Faker("date_time")
    history_user_id = factory.Sequence(lambda n: n + 1)
    history_type = factory.Faker("random_element", elements=["+", "-", "~"])
    deadline_is_explicit = factory.Faker("random_int", min=0, max=1)
