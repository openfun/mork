"""Factory classes for student models."""

import factory

from mork.edx.mysql.models.student import (
    StudentAnonymoususerid,
    StudentCourseaccessrole,
    StudentCourseenrollment,
    StudentCourseenrollmentallowed,
    StudentCourseenrollmentattribute,
    StudentHistoricalcourseenrollment,
    StudentLanguageproficiency,
    StudentLoginfailure,
    StudentManualenrollmentaudit,
    StudentPendingemailchange,
    StudentUserstanding,
)

from .base import BaseSQLAlchemyModelFactory, faker


class EdxStudentAnonymoususeridFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_anonymoususerid` table."""

    class Meta:
        """Factory configuration."""

        model = StudentAnonymoususerid

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    anonymous_user_id = factory.Faker("hexify", text="^" * 32)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")


class EdxStudentCourseaccessroleFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_courseaccessrole` table."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseaccessrole

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    org = factory.Faker("word")
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    role = factory.Faker("word")


class EdxStudentCourseenrollmentallowedFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_courseenrollmentallowed` table."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseenrollmentallowed

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker("email")
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    created = factory.Faker("date_time")
    auto_enroll = factory.Faker("random_int", min=0, max=1)


class EdxStudentCourseenrollmentattributeFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_courseenrollmentattribute` table."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseenrollmentattribute

    id = factory.Sequence(lambda n: n + 1)
    enrollment_id = factory.Sequence(lambda n: n + 1)
    namespace = factory.Faker("pystr")
    name = factory.Faker("pystr")
    value = factory.Faker("pystr")


class EdxStudentHistoricalcourseenrollmentFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_historicalcourseenrollment` table."""

    class Meta:
        """Factory configuration."""

        model = StudentHistoricalcourseenrollment

    id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    created = factory.Faker("date_time")
    is_active = factory.Faker("random_int", min=0, max=1)
    mode = factory.Faker("pystr")
    user_id = factory.Sequence(lambda n: n + 1)
    history_id = factory.Sequence(lambda n: n + 1)
    history_date = factory.Faker("date_time")
    history_user_id = factory.Sequence(lambda n: n + 1)
    history_type = factory.Faker("random_letter")


class EdxStudentLanguageproficiencyFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_languageproficiency` table."""

    class Meta:
        """Factory configuration."""

        model = StudentLanguageproficiency

    id = factory.Sequence(lambda n: n + 1)
    user_profile_id = factory.Sequence(lambda n: n + 1)
    code = factory.Faker("pystr", max_chars=16)


class EdxStudentLoginfailureFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_loginfailure` table."""

    class Meta:
        """Factory configuration."""

        model = StudentLoginfailure

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    failure_count = factory.Sequence(lambda n: n)
    lockout_until = factory.Faker("date_time")


class EdxStudentManualenrollmentauditFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_manualenrollmentaudit` table."""

    class Meta:
        """Factory configuration."""

        model = StudentManualenrollmentaudit

    id = factory.Sequence(lambda n: n + 1)
    enrollment_id = factory.Sequence(lambda n: n + 1)
    enrolled_by_id = factory.Sequence(lambda n: n + 1)
    enrolled_email = factory.Faker("email")
    time_stamp = factory.Faker("date_time")
    state_transition = factory.Faker("pystr")
    reason = factory.Faker("text")


class EdxStudentCourseenrollmentFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_courseenrollment` table."""

    class Meta:
        """Factory configuration."""

        model = StudentCourseenrollment

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    is_active = factory.Faker("random_int", min=0, max=1)
    mode = factory.Faker("word")
    created = factory.Faker("date_time")

    student_courseenrollmentattribute = factory.RelatedFactoryList(
        EdxStudentCourseenrollmentattributeFactory,
        "enrollment",
        size=3,
        enrollment_id=factory.SelfAttribute("..id"),
    )
    student_manualenrollmentaudit = factory.RelatedFactoryList(
        EdxStudentManualenrollmentauditFactory,
        "enrollment",
        size=3,
        enrollment_id=factory.SelfAttribute("..id"),
        enrolled_by_id=factory.SelfAttribute("..user_id"),
    )


class EdxStudentPendingemailchangeFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_pendingemailchange` table."""

    class Meta:
        """Factory configuration."""

        model = StudentPendingemailchange

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    new_email = factory.Faker("email")
    activation_key = factory.Faker("hexify", text="^" * 32)


class EdxStudentUserstandingFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `student_userstanding` table."""

    class Meta:
        """Factory configuration."""

        model = StudentUserstanding

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    account_status = factory.Faker("word")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    standing_last_changed_at = factory.Faker("date_time")
