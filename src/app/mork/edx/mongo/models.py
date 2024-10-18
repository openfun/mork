"""Mork edx MongoDB models."""

import mongoengine


class CommentBase(mongoengine.Document):
    """Base model for a forum comment document."""

    _id = mongoengine.ObjectIdField()
    votes = mongoengine.DictField()
    visible = mongoengine.BooleanField()
    abuse_flaggers = mongoengine.ListField()
    historical_abuse_flaggers = mongoengine.ListField()
    thread_type = mongoengine.StringField()
    context = mongoengine.StringField()
    comment_count = mongoengine.IntField()
    at_position_list = mongoengine.ListField()
    title = mongoengine.StringField()
    body = mongoengine.StringField()
    course_id = mongoengine.StringField()
    commentable_id = mongoengine.StringField()
    anonymous = mongoengine.BooleanField()
    anonymous_to_peers = mongoengine.BooleanField()
    closed = mongoengine.BooleanField()
    author_id = mongoengine.IntField()
    author_username = mongoengine.StringField()
    updated_at = mongoengine.DateField()
    created_at = mongoengine.DateField()
    last_activity_at = mongoengine.DateField()
    meta = {"abstract": True, "collection": "contents"}


class CommentThread(CommentBase):
    """Model for the `CommentThread` document type."""

    type = mongoengine.StringField(default="CommentThread", db_field="_type")


class Comment(CommentBase):
    """Model for the `Comment` document type."""

    type = mongoengine.StringField(default="Comment", db_field="_type")
