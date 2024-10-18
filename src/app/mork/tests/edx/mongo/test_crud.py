"""Tests of the MongoDB related CRUD functions."""

from mork.edx.mongo import crud
from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.edx.mongo.models import Comment, CommentThread


def test_edx_mongo_crud_anonymize_comments(edx_mongo_db):
    """Test the `anonymize_comments` method."""
    username = "JohnDoe"

    CommentFactory.create_batch(3, author_username=username)
    CommentThreadFactory.create_batch(3, author_username=username)

    assert Comment.objects(author_username=username).count() > 0
    assert CommentThread.objects(author_username=username).count() > 0

    crud.anonymize_comments(username)

    assert Comment.objects(author_username=username).count() == 0
    assert CommentThread.objects(author_username=username).count() == 0
