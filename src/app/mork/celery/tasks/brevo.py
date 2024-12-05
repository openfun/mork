"""Mork Celery brevo tasks."""

from logging import getLogger
from uuid import UUID

import httpx

from mork.celery.celery_app import app
from mork.celery.utils import (
    get_service_status,
    get_user_from_mork,
    update_status_in_mork,
)
from mork.conf import settings
from mork.exceptions import (
    UserDeleteError,
    UserNotFound,
    UserStatusError,
)
from mork.models.users import DeletionStatus, ServiceName

logger = getLogger(__name__)


@app.task(
    bind=True,
    retry_kwargs={"max_retries": settings.DELETE_MAX_RETRIES},
)
def delete_brevo_platform_user(self, user_id: UUID):
    """Task to delete user from the Brevo platform."""
    if not settings.BREVO_API_URL:
        logger.info("Brevo API URL not set, skipping deletion.")
        return

    user = get_user_from_mork(user_id)
    if not user:
        msg = f"User {user_id} could not be retrieved from Mork"
        logger.error(msg)
        raise UserNotFound(msg)

    status = get_service_status(user, ServiceName.BREVO)
    if status != DeletionStatus.TO_DELETE:
        msg = f"User {user_id} is not to be deleted. Status: {status}"
        logger.error(msg)
        raise UserStatusError(msg)

    try:
        delete_brevo_user(email=user.email)
    except UserDeleteError as exc:
        raise self.retry(exc=exc) from exc

    if not update_status_in_mork(
        user_id=user_id, service=ServiceName.BREVO, status=DeletionStatus.DELETED
    ):
        msg = f"Failed to update deletion status to deleted for user {user_id}"
        logger.error(msg)
        raise UserStatusError(msg)

    logger.info(f"Completed deletion process for user {user_id}")


def delete_brevo_user(email: str):
    """Delete user contact on Brevo."""
    logger.debug("Delete user contact on Brevo")

    try:
        response = httpx.delete(
            f"{settings.BREVO_API_URL}/contacts/{email}",
            headers={"api-key": f"{settings.BREVO_API_KEY}"},
        )
        response.raise_for_status()
    except httpx.RequestError as exc:
        msg = "Network error while deleting user contact on Brevo"
        logger.error(msg)
        raise UserDeleteError(msg) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == httpx.codes.NOT_FOUND:
            logger.info("User has no contact on Brevo")
            return

        msg = "Failed to delete user contact on Brevo"
        logger.error(msg)
        raise UserDeleteError(msg) from exc
