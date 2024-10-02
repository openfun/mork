"""Factory classes for bulk models."""

import factory

from mork.edx.models.bulk import BulkEmailCourseemail, BulkEmailOptout

from .base import faker, session


class EdxBulkEmailCourseemailFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `bulk_email_courseemail` table."""

    class Meta:
        """Factory configuration."""

        model = BulkEmailCourseemail
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    sender_id = factory.Sequence(lambda n: n + 1)
    slug = factory.Faker("pystr")
    subject = factory.Faker("pystr")
    html_message = factory.Faker("pystr")
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    to_option = factory.Faker("word")
    text_message = factory.Faker("text")
    template_name = factory.Faker("text")
    from_addr = factory.Faker("text")


class EdxBulkEmailOptoutFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for the `bulk_email_optout` table."""

    class Meta:
        """Factory configuration."""

        model = BulkEmailOptout
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    user_id = factory.Sequence(lambda n: n + 1)
