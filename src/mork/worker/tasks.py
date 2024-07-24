"""Mork Celery tasks."""

from logging import getLogger

from mork.api.models import TaskType
from mork.worker.celery_app import app

logger = getLogger(__name__)


@app.task
def warn_inactive_users():
    """Celery task to warn inactive users by email."""
    pass


@app.task
def delete_inactive_users():
    """Celery task to delete inactive users accounts."""
    pass


TASK_TYPE_TO_FUNC = {
    TaskType.EMAILING: warn_inactive_users,
    TaskType.DELETION: delete_inactive_users,
}
