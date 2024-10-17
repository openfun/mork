"""Factory classes for verify models."""

import factory

from mork.edx.mysql.models.verify import (
    VerifyStudentHistoricalverificationdeadline,
    VerifyStudentSoftwaresecurephotoverification,
)

from .base import BaseSQLAlchemyModelFactory, faker


class EdxVerifyStudentHistoricalverificationdeadlineFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `verify_student_historicalverificationdeadline` table."""

    class Meta:
        """Factory configuration."""

        model = VerifyStudentHistoricalverificationdeadline

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


class EdxVerifyStudentSoftwaresecurephotoverificationFactory(
    BaseSQLAlchemyModelFactory
):
    """Factory for the `verify_student_softwaresecurephotoverification` table."""

    class Meta:
        """Factory configuration."""

        model = VerifyStudentSoftwaresecurephotoverification

    id = factory.Sequence(lambda n: n + 1)
    status = factory.Faker("pystr")
    status_changed = factory.Faker("date_time")
    user_id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("pystr")
    face_image_url = factory.Faker("url")
    photo_id_image_url = factory.Faker("url")
    receipt_id = factory.Faker("pystr")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    submitted_at = factory.Faker("date_time")
    reviewing_user_id = factory.Sequence(lambda n: n + 1)
    reviewing_service = factory.Faker("pystr")
    error_msg = factory.Faker("text")
    error_code = factory.Faker("pystr")
    photo_id_key = factory.Faker("text")
    display = factory.Faker("random_int", min=0, max=1)
    copy_id_photo_from_id = factory.Sequence(lambda n: n + 1)
