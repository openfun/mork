"""Mork models."""

from enum import Enum, unique
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

from mork.celery.tasks.deletion import delete_inactive_users, delete_user
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
    DELETE_USER = "delete_user"


class TaskCreateBase(BaseModel):
    """Base model for creating a task."""

    model_config = ConfigDict(extra="ignore")
    dry_run: bool = True


class DeleteInactiveUsers(TaskCreateBase):
    """Model for creating a task to delete all inactive users."""

    type: Literal[TaskType.DELETE_INACTIVE_USERS]


class EmailInactiveUsers(TaskCreateBase):
    """Model for creating a task to email all inactive users."""

    type: Literal[TaskType.EMAIL_INACTIVE_USERS]


class DeleteUser(TaskCreateBase):
    """Model for creating a task to delete one user."""

    type: Literal[TaskType.DELETE_USER]
    email: EmailStr


class TaskResponse(BaseModel):
    """Model for a task response."""

    id: str
    status: TaskStatus


TASK_TYPE_TO_FUNC = {
    TaskType.EMAIL_INACTIVE_USERS: warn_inactive_users,
    TaskType.DELETE_INACTIVE_USERS: delete_inactive_users,
    TaskType.DELETE_USER: delete_user,
}
