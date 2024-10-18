"""Module for MongoDB CRUD functions."""

from logging import getLogger

from mongoengine.queryset.visitor import Q

from mork.conf import settings
from mork.edx.mongo.models import Comment, CommentThread

logger = getLogger(__name__)


def anonymize_comments(username: str) -> None:
    """Anonymize user comments and threads.

    Parameters:
    username (str): The username of the user to delete comments from.
    """
    comments = Comment.objects(Q(type="Comment") & Q(author_username=username)).all()

    comment_count = comments.update(
        author_username="[deleted]",
        body="[deleted]",
        author_id=settings.EDX_FORUM_PLACEHOLDER_USER_ID,
        anonymous=True,
    )

    comment_threads = CommentThread.objects(
        Q(type="CommentThread") & Q(author_username=username)
    ).all()

    comment_count += comment_threads.update(
        author_username="[deleted]",
        title="[deleted]",
        body="[deleted]",
        author_id=settings.EDX_FORUM_PLACEHOLDER_USER_ID,
        anonymous=True,
    )

    logger.info(f"Anonymized {comment_count} comment(s) for user {username}")
