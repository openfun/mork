"""Factory classes for course models."""

import factory

from mork.edx.mysql.models.course import (
    CourseActionStateCoursererunstate,
    CourseCreatorsCoursecreator,
    CourseGroupsCohortmembership,
    CourseGroupsCourseusergroupUsers,
)

from .base import BaseSQLAlchemyModelFactory, faker


class EdxCourseActionStateCoursererunstateFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `course_action_state_coursererunstate` table."""

    class Meta:
        """Factory configuration."""

        model = CourseActionStateCoursererunstate

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


class EdxCourseCreatorsCoursecreatorFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `course_creators_coursecreator` table."""

    class Meta:
        """Factory configuration."""

        model = CourseCreatorsCoursecreator

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    state_changed = factory.Faker("date_time")
    state = factory.Faker("word")
    note = factory.Faker("text")


class EdxCourseGroupsCourseusergroupUsersFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `course_groups_courseusergroup_users` table."""

    class Meta:
        """Factory configuration."""

        model = CourseGroupsCourseusergroupUsers

    id = factory.Sequence(lambda n: n + 1)
    courseusergroup_id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)


class EdxCourseGroupsCohortmembershipFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `course_groups_cohortmembership` table."""

    class Meta:
        """Factory configuration."""

        model = CourseGroupsCohortmembership

    id = factory.Sequence(lambda n: n + 1)
    course_user_group_id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
