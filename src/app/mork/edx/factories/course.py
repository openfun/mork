"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.course import (
    CourseActionStateCoursererunstate,
    CourseCreatorsCoursecreator,
)

from .base import faker, session


class EdxCourseActionStateCoursererunstateFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    """Factory for the `course_action_state_coursererunstate` table."""

    class Meta:
        """Factory configuration."""

        model = CourseActionStateCoursererunstate
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    created_time = factory.Faker("date_time")
    updated_time = factory.Faker("date_time")
    course_key = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    action = factory.Faker("word")
    state = factory.Faker("word")
    should_display = factory.Faker("random_int", min=0, max=1)
    message = factory.Faker("text")
    source_course_key = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    display_name = factory.Faker("text")


class EdxCourseCreatorsCoursecreatorFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `course_creators_coursecreator` table."""

    class Meta:
        """Factory configuration."""

        model = CourseCreatorsCoursecreator
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    state_changed = factory.Faker("date_time")
    state = factory.Faker("word")
    note = factory.Faker("text")
