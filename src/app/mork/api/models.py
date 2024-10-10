"""Mork models."""

from enum import Enum, unique

from pydantic import BaseModel

from mork.celery.tasks.deletion import delete_inactive_users
from mork.celery.tasks.emailing import warn_inactive_users


@unique
class TaskStatus(str, Enum):
    """Task statuses."""

    FAILURE = "FAILURE"
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    RETRY = "RETRY"
    REVOKED = "REVOKED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"


@unique
class TaskType(str, Enum):
    """Possible task types."""

    EMAIL_INACTIVE_USERS = "email_inactive_users"
    DELETE_INACTIVE_USERS = "delete_inactive_users"


class TaskCreate(BaseModel):
    """Model for creating a new task."""

    type: TaskType


class TaskResponse(BaseModel):
    """Model for a task response."""

    id: str
    status: TaskStatus


TASK_TYPE_TO_FUNC = {
    TaskType.EMAIL_INACTIVE_USERS: warn_inactive_users,
    TaskType.DELETE_INACTIVE_USERS: delete_inactive_users,
}
