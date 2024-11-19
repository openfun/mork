"""Mork Celery deletion tasks."""

from datetime import datetime
from logging import getLogger
from uuid import UUID

from celery import chain, group
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.celery_app import app
from mork.celery.tasks.edx import delete_edx_platform_user
from mork.conf import settings
from mork.db import MorkDB
from mork.edx.mysql import crud
from mork.edx.mysql.database import OpenEdxMySQLDB
from mork.exceptions import UserDeleteError
from mork.models.tasks import EmailStatus
from mork.models.users import (
    DeletionReason,
    DeletionStatus,
    ServiceName,
    User,
    UserServiceStatus,
)

logger = getLogger(__name__)


@app.task
def delete_inactive_users(limit: int = 0, dry_run: bool = True):
    """Celery task to delete inactive users accounts."""
    edx_db = OpenEdxMySQLDB()

    threshold_date = datetime.now() - settings.DELETION_PERIOD
    total = crud.get_inactive_users_count(edx_db.session, threshold_date)

    if limit:
        total = min(total, limit)

    for batch_offset in range(0, total, settings.EDX_MYSQL_QUERY_BATCH_SIZE):
        batch_limit = min(settings.EDX_MYSQL_QUERY_BATCH_SIZE, total - batch_offset)
        inactive_users = crud.get_inactive_users(
            edx_db.session,
            threshold_date,
            offset=batch_offset,
            limit=batch_limit,
        )

        delete_group = group(
            [
                delete_user.s(
                    email=user.email, reason=DeletionReason.GDPR, dry_run=dry_run
                )
                for user in inactive_users
            ]
        )
        delete_group.delay()

    edx_db.session.close()


@app.task
def delete_user(
    email: str,
    reason: DeletionReason = DeletionReason.USER_REQUESTED,
    dry_run: bool = True,
):
    """Celery task that deletes a specific user."""
    if dry_run:
        logger.info(f"Dry run: User with {email=} would have been deleted")
        return

    logger.info(f"Starting deletion of user with {email=}")

    delete_chain = chain(
        remove_email_status.si(email),
        mark_user_for_deletion.si(email=email, reason=reason),
        delete_edx_platform_user.s(),
    )

    delete_chain.delay()


@app.task
def mark_user_for_deletion(email: str, reason: DeletionReason) -> UUID:
    """Mark user for deletion across all services in Mork database."""
    logger.debug("Marking user for deletion")

    edx_mysql_db = OpenEdxMySQLDB()
    edx_mysql_db.session.expire_on_commit = False

    auth_user = crud.get_user(edx_mysql_db.session, email)

    edx_mysql_db.session.close()

    if not auth_user:
        msg = f"User with {email=} not found in edx database"
        logger.error(msg)
        raise UserDeleteError(msg)

    mork_db = MorkDB()

    # Check if user already exist in Mork database
    user_exist = mork_db.session.scalar(select(User).where(User.email == email))
    if user_exist:
        logger.info(f"User with {email=} is already marked for deletion")
        return user_exist.id

    # Add user to Mork database
    user_id = mork_db.session.scalar(
        insert(User)
        .returning(User.id)
        .values(
            username=auth_user.username,
            edx_user_id=auth_user.id,
            email=auth_user.email,
            reason=reason,
        )
    )

    # Mark for deletion across all services
    mork_db.session.execute(
        insert(UserServiceStatus),
        [
            {
                "user_id": user_id,
                "service_name": service,
                "status": DeletionStatus.TO_DELETE,
            }
            for service in ServiceName
        ],
    )

    try:
        mork_db.session.commit()
    except SQLAlchemyError as exc:
        mork_db.session.rollback()
        logger.error(f"Failed to mark user to be deleted - {exc}")
        raise UserDeleteError("Failed to mark user to be deleted") from exc
    finally:
        mork_db.session.close()

    return user_id


@app.task
def remove_email_status(email: str):
    """Delete the email status in the Mork database."""
    logger.debug("Removing user email status")
    mork_db = MorkDB()
    user_to_delete = (
        mork_db.session.query(EmailStatus).filter(EmailStatus.email == email).first()
    )
    if not user_to_delete:
        logger.warning("Email status - No user found with email %s for deletion", email)
        return

    mork_db.session.delete(user_to_delete)
    try:
        mork_db.session.commit()
    except SQLAlchemyError:
        mork_db.session.rollback()
        logger.error("Email status - Failed to delete user with email %s", email)
        return
    finally:
        mork_db.session.close()
