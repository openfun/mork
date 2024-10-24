"""Mork edx MongoDB models."""

from mongoengine import (
    BooleanField,
    DateField,
    DictField,
    Document,
    IntField,
    ListField,
    ObjectIdField,
    StringField,
)
from mongoengine.queryset import queryset_manager


class ForumObject(Document):
    """Base model for a forum object document."""

    _id = ObjectIdField()
    votes = DictField()
    visible = BooleanField()
    abuse_flaggers = ListField()
    historical_abuse_flaggers = ListField()
    thread_type = StringField()
    context = StringField()
    comment_count = IntField()
    at_position_list = ListField()
    body = StringField()
    course_id = StringField()
    commentable_id = StringField()
    anonymous = BooleanField()
    anonymous_to_peers = BooleanField()
    closed = BooleanField()
    author_id = IntField()
    author_username = StringField()
    updated_at = DateField()
    created_at = DateField()
    last_activity_at = DateField()
    meta = {"abstract": True, "collection": "contents"}


class Comment(ForumObject):
    """Model for the `Comment` document type."""

    type = StringField(default="Comment", db_field="_type")

    @queryset_manager
    def objects(self, queryset):
        """Filter on the _type field."""
        return queryset.filter(type="Comment")


class CommentThread(ForumObject):
    """Model for the `CommentThread` document type."""

    type = StringField(default="CommentThread", db_field="_type")
    title = StringField()

    @queryset_manager
    def objects(self, queryset):
        """Filter on the _type field."""
        return queryset.filter(type="CommentThread")
