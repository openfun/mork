"""Mork models."""

from enum import Enum, unique

from pydantic import BaseModel

from mork.celery.tasks import delete_inactive_users, warn_inactive_users


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

    EMAILING = "emailing"
    DELETION = "deletion"


class TaskCreate(BaseModel):
    """Model for creating a new task."""

    type: TaskType


class TaskResponse(BaseModel):
    """Model for a task response."""

    id: str
    status: TaskStatus


TASK_TYPE_TO_FUNC = {
    TaskType.EMAILING: warn_inactive_users,
    TaskType.DELETION: delete_inactive_users,
}
