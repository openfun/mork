"""Mork Celery deletion tasks."""

from datetime import datetime
from logging import getLogger

from celery import group
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.celery_app import app
from mork.conf import settings
from mork.database import MorkDB
from mork.edx import crud
from mork.edx.database import OpenEdxDB
from mork.exceptions import UserDeleteError
from mork.models import EmailStatus

logger = getLogger(__name__)


@app.task
def delete_inactive_users():
    """Celery task to delete inactive users accounts."""
    db = OpenEdxDB()
    threshold_date = datetime.now() - settings.DELETION_PERIOD

    total = crud.get_inactive_users_count(db.session, threshold_date)
    for batch_offset in range(0, total, settings.EDX_QUERY_BATCH_SIZE):
        inactive_users = crud.get_inactive_users(
            db.session,
            threshold_date,
            offset=batch_offset,
            limit=settings.EDX_QUERY_BATCH_SIZE,
        )
        delete_group = group([deletion_task.s(user.email) for user in inactive_users])
        delete_group.delay()


@app.task(
    bind=True,
    retry_kwargs={"max_retries": settings.DELETE_MAX_RETRIES},
)
def deletion_task(self, email: str):
    """Celery task that delete a specified user."""
    try:
        delete_user(email)
    except UserDeleteError as exc:
        logger.exception(exc)
        raise self.retry(exc=exc) from exc

    # Delete email status flag in mork database
    delete_email_status(email)


def delete_user(email):
    """Delete user from edX database."""
    db = OpenEdxDB()

    # Delete user from edX database
    crud.delete_user(db.session, email=email)
    try:
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.error(f"Failed to delete user with {email=}: {exc}")
        raise UserDeleteError("Failed to delete user.") from exc
    finally:
        db.session.close()


def delete_email_status(email: str):
    """Delete the email status in the Mork database."""
    # Delete user from Mork email status database
    mork_db = MorkDB()
    user_to_delete = (
        mork_db.session.query(EmailStatus).filter(EmailStatus.email == email).first()
    )
    if not user_to_delete:
        logger.warning(f"Mork DB - No user found with {email=} for deletion")
        return

    mork_db.session.delete(user_to_delete)
    try:
        mork_db.session.commit()
    except SQLAlchemyError as exc:
        mork_db.session.rollback()
        logger.error(f"Mork DB - Failed to delete user with {email=}: {exc}")
        return
    finally:
        mork_db.session.close()
