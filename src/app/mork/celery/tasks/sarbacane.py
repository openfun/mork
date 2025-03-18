"""Mork Celery sarbacane tasks."""

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
def delete_sarbacane_platform_user(self, user_id: UUID):
    """Task to delete user from the Sarbacane platform."""
    if not settings.SARBACANE_API_URL:
        logger.info("Sarbacane API URL not set, skipping deletion.")
        return

    user = get_user_from_mork(user_id)
    if not user:
        msg = f"User {user_id} could not be retrieved from Mork"
        logger.error(msg)
        raise UserNotFound(msg)

    status = get_service_status(user, ServiceName.SARBACANE)

    if status == DeletionStatus.DELETED:
        logger.warning(f"User {user_id} has already been deleted.")
        return

    if status != DeletionStatus.TO_DELETE:
        msg = f"User {user_id} cannot be deleted. Status: {status}"
        logger.error(msg)
        raise UserStatusError(msg)

    try:
        delete_sarbacane_user(email=user.email)
    except UserDeleteError as exc:
        raise self.retry(exc=exc) from exc

    if not update_status_in_mork(
        user_id=user_id, service=ServiceName.SARBACANE, status=DeletionStatus.DELETED
    ):
        msg = f"Failed to update deletion status to 'DELETED' for user {user_id}"
        logger.error(msg)
        raise UserStatusError(msg)

    logger.info(f"Completed deletion process for user {user_id}")


def delete_sarbacane_user(email: str):
    """Delete user contact on Sarbacane."""
    logger.debug("Delete user contact on Sarbacane")

    headers = {
        "accountId": f"{settings.SARBACANE_ACCOUNT_ID}",
        "apiKey": f"{settings.SARBACANE_API_KEY}",
    }

    with httpx.Client(base_url=settings.SARBACANE_API_URL, headers=headers) as client:
        try:
            lists_response = client.get("/lists")
            blacklists_response = client.get("/blacklists")
        except httpx.RequestError as exc:
            msg = "Network error while retrieving lists of contacts"
            logger.error(msg)
            raise UserDeleteError(msg) from exc

        list_ids = {contact_list["id"] for contact_list in lists_response.json()}
        blacklist_ids = {blacklist["id"] for blacklist in blacklists_response.json()}

        for list_id in list_ids:
            _delete_contact(client, f"/lists/{list_id}/contacts", email)

        for blacklist_id in blacklist_ids:
            _delete_contact(client, f"/blacklists/{blacklist_id}/unsubscribers", email)
            _delete_contact(client, f"/blacklists/{blacklist_id}/complaints", email)


def _delete_contact(client: httpx.Client, endpoint: str, email: str):
    """Delete a contact from a given endpoint."""
    try:
        response = client.delete(f"{endpoint}?email={email}")
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        data = exc.response.json() if exc.response.content else {}
        if data.get("message") == "No contacts versions to delete":
            logger.info(f"User not found at {endpoint}")
        else:
            msg = f"Failed to delete user contact at {endpoint}"
            logger.error(msg)
            raise UserDeleteError(msg) from exc
    except httpx.RequestError as exc:
        msg = f"Network error while deleting user contact at {endpoint}"
        logger.error(msg)
        raise UserDeleteError(msg) from exc
