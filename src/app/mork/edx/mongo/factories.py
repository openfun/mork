"""Factory classes for MongoDB models."""

import factory

from mork.edx.mongo.models import Comment, CommentThread


class CommentBaseFactory(factory.mongoengine.MongoEngineFactory):
    """Base factory for MongoDB comment objects."""

    votes = {}
    visible = factory.Faker("pybool")
    abuse_flaggers = []
    historical_abuse_flaggers = []
    thread_type = factory.Faker("pystr")
    context = factory.Faker("pystr")
    comment_count = factory.Faker("pyint")
    at_position_list = []
    body = factory.Faker("text")
    course_id = factory.Faker("pystr")
    commentable_id = factory.Faker("pystr")
    anonymous = factory.Faker("pybool")
    anonymous_to_peers = factory.Faker("pybool")
    closed = factory.Faker("pybool")
    author_id = factory.Faker("pyint")
    author_username = factory.Faker("pystr")
    updated_at = factory.Faker("date_time")
    created_at = factory.Faker("date_time")
    last_activity_at = factory.Faker("date_time")


class CommentFactory(CommentBaseFactory):
    """Factory for the `Comment` document type."""

    class Meta:
        """Factory configuration."""

        model = Comment

    type = "Comment"


class CommentThreadFactory(CommentBaseFactory):
    """Factory for the `CommentThread` document type."""

    class Meta:
        """Factory configuration."""

        model = CommentThread

    type = "CommentThread"
    title = factory.Faker("sentence")
