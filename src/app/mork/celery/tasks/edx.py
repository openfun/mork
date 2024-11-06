"""Mork Celery edx tasks."""

from logging import getLogger
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from mork.celery.celery_app import app
from mork.celery.utils import (
    get_service_status,
    get_user_from_mork,
    update_status_in_mork,
)
from mork.conf import settings
from mork.edx.mysql import crud as mysql
from mork.edx.mysql.database import OpenEdxMySQLDB
from mork.exceptions import (
    UserDeleteError,
    UserNotFound,
    UserProtected,
    UserStatusError,
)
from mork.models.users import DeletionStatus, ServiceName

logger = getLogger(__name__)


@app.task(
    bind=True,
    retry_kwargs={"max_retries": settings.DELETE_MAX_RETRIES},
)
def delete_edx_platform_user(self, user_id: UUID):
    """Task to delete user from the edX platform."""
    user = get_user_from_mork(user_id)
    if not user:
        msg = f"User {user_id} could not be retrieved from Mork"
        logger.error(msg)
        raise UserNotFound(msg)

    status = get_service_status(user, ServiceName.EDX)
    if status != DeletionStatus.TO_DELETE:
        msg = f"User {user_id} is not to be deleted. Status: {status}"
        logger.error(msg)
        raise UserStatusError(msg)

    try:
        delete_edx_mysql_user(email=user.email)
        delete_edx_mongo_user(username=user.username)
    except UserDeleteError as exc:
        raise self.retry(exc=exc) from exc

    if not update_status_in_mork(
        user_id=user_id, service=ServiceName.EDX, status=DeletionStatus.DELETED
    ):
        msg = f"Failed to update deletion status to deleted for user {user_id}"
        logger.error(msg)
        raise UserStatusError(msg)

    logger.info(f"Completed deletion process for user {user_id}")


def delete_edx_mysql_user(email: str):
    """Delete user's data from edX MySQL database."""
    logger.debug("Deleting user's data from edX MySQL")

    db = OpenEdxMySQLDB()
    try:
        mysql.delete_user(db.session, email=email)
        db.session.commit()
    except (UserProtected, UserNotFound) as exc:
        db.session.rollback()
        logger.info(f"Skipping MySQL deletion for user with {email=} : {exc}")
    except SQLAlchemyError as exc:
        db.session.rollback()
        msg = f"Failed to delete user with {email=} from edX MySQL"
        logger.error(msg)
        raise UserDeleteError(msg) from exc
    finally:
        db.session.close()


def delete_edx_mongo_user(username: str):  # noqa: ARG001
    """Delete user's data from edX MongoDB database."""
    logger.debug("Deleting user's data from edX MongoDB")
    pass
