"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.courseware import (
    CoursewareOfflinecomputedgrade,
    CoursewareStudentmodule,
    CoursewareXmodulestudentinfofield,
    CoursewareXmodulestudentprefsfield,
)

from .base import faker, session


class EdxCoursewareOfflinecomputedgradeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `courseware_offlinecomputedgrade` table."""

    class Meta:
        """Factory configuration."""

        model = CoursewareOfflinecomputedgrade
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    created = factory.Faker("date_time")
    updated = factory.Faker("date_time")
    gradeset = factory.Faker("json")


class EdxCoursewareStudentmoduleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `courseware_studentmodule` table."""

    class Meta:
        """Factory configuration."""

        model = CoursewareStudentmodule
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    module_type = factory.Faker(
        "random_element", elements=["course", "sequential", "problem", "chapter"]
    )
    module_id = factory.Faker("pystr")
    student_id = factory.Sequence(lambda n: n + 1)
    state = factory.Faker("json")
    grade = factory.Faker("pyfloat")
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")
    max_grade = factory.Faker("pyfloat")
    done = factory.Faker("pystr", max_chars=8)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")


class EdxCoursewareXmodulestudentinfofieldFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    """Factory for the `courseware_xmodulestudentinfofield` table."""

    class Meta:
        """Factory configuration."""

        model = CoursewareXmodulestudentinfofield
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    field_name = factory.Faker("word")
    value = factory.Faker("random_element", elements=["true", "false"])
    student_id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")


class EdxCoursewareXmodulestudentprefsfieldFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    """Factory for the `courseware_xmodulestudentprefsfield` table."""

    class Meta:
        """Factory configuration."""

        model = CoursewareXmodulestudentprefsfield
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    field_name = factory.Faker("word")
    module_type = factory.Faker("word")
    value = factory.Faker("pystr")
    student_id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")
