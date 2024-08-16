"""Mork Celery deletion tasks."""

from mork.celery.celery_app import app


@app.task
def delete_inactive_users():
    """Celery task to delete inactive users accounts."""


pass
