"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.student import (
    StudentAnonymoususerid,
    StudentCourseaccessrole,
    StudentCourseenrollment,
    StudentHistoricalcourseenrollment,
    StudentLoginfailure,
    StudentPendingemailchange,
    StudentUserstanding,
)

from .base import faker, session


class EdxStudentAnonymoususeridFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `student_anonymoususerid` table."""

    class Meta:
        """Factory configuration."""

        model = StudentAnonymoususerid
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    anonymous_user_id = factory.Faker("hexify", text="^" * 32)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")


class EdxStudentCourseaccessroleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `student_courseaccessrole` table."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseaccessrole
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    org = factory.Faker("word")
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    role = factory.Faker("word")


class EdxStudentCourseEnrollmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating fake Open edX enrollments."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseenrollment
        sqlalchemy_session = session

    user_id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    created = factory.Faker("date_time")
    is_active = True
    mode = factory.Faker("word")


class EdxStudentHistoricalcourseenrollmentFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    """Factory for the `student_historicalcourseenrollment` table."""

    class Meta:
        """Factory configuration."""

        model = StudentHistoricalcourseenrollment
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    created = factory.Faker("date_time")
    is_active = factory.Faker("random_int", min=0, max=1)
    mode = factory.Faker("word")
    history_id = factory.Sequence(lambda n: n + 1)
    history_date = factory.Faker("date_time")
    history_type = factory.Faker("random_element", elements=["+", "-", "~"])


class EdxStudentLoginfailureFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `student_loginfailure` table."""

    class Meta:
        """Factory configuration."""

        model = StudentLoginfailure
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    failure_count = factory.Sequence(lambda n: n)
    lockout_until = factory.Faker("date_time")


class EdxStudentPendingemailchangeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `student_pendingemailchange` table."""

    class Meta:
        """Factory configuration."""

        model = StudentPendingemailchange
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    new_email = factory.Faker("email")
    activation_key = factory.Faker("hexify", text="^" * 32)


class EdxStudentUserstandingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `student_userstanding` table."""

    class Meta:
        """Factory configuration."""

        model = StudentUserstanding
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    account_status = factory.Faker("word")
    standing_last_changed_at = factory.Faker("date_time")
