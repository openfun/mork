"""Factory classes for generating fake data for testing."""

import factory

from mork.edx.models.instructor import InstructorTaskInstructortask

from .base import faker, session


class EdxInstructorTaskInstructortaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `instructor_task_instructortask` table."""

    class Meta:
        """Factory configuration."""

        model = InstructorTaskInstructortask
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    task_type = factory.Faker("word")
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    task_key = factory.Faker("hexify", text="^" * 20)
    task_input = factory.Faker("pystr", max_chars=255)
    task_id = factory.Faker("uuid4")
    task_state = factory.Faker("word")
    task_output = factory.Faker("json")
    requester_id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")
    updated = factory.Faker("date_time")
    subtasks = factory.Faker("json")