"""Celery utils functions."""

from logging import getLogger
from uuid import UUID

import httpx

from mork.conf import settings
from mork.models.users import DeletionStatus, ServiceName
from mork.schemas.users import UserRead

logger = getLogger(__name__)


def get_user_from_mork(user_id: UUID) -> UserRead | None:
    """Retrieve user from Mork by ID."""
    logger.debug("Get user from Mork")
    logger.debug(f"API URL: {settings.SERVER_URL}")

    try:
        response = httpx.get(
            f"{settings.SERVER_URL}/v1/users/{user_id}",
            headers={"X-API-Key": f"{settings.API_KEYS[0]}"},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(f"Failed to retrieve user from Mork API: {exc}")
        return None

    return UserRead.model_validate(response.json())


def get_service_status(user: UserRead, service: ServiceName) -> DeletionStatus | None:
    """Find the service status entry for a user."""
    service_status = next(
        (status for status in user.service_statuses if status.service_name == service),
        None,
    )
    return service_status.status if service_status else None


def update_status_in_mork(
    user_id: UUID, service: ServiceName, status: DeletionStatus
) -> bool:
    """Update the user deletion status in Mork."""
    logger.debug(f"Updating deletion status for user {user_id} in Mork to {status}")
    logger.debug(f"API URL: {settings.SERVER_URL}")

    try:
        response = httpx.patch(
            f"{settings.SERVER_URL}/v1/users/{user_id}/status/{service.value}",
            headers={"X-API-Key": f"{settings.API_KEYS[0]}"},
            json={"deletion_status": status.value},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(f"Failed to update user status with Mork API: {exc}")
        return False

    return True
