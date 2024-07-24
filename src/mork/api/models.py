"""Mork models."""

from enum import Enum, unique

from pydantic import BaseModel


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
