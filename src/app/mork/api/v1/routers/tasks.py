"""API task router.

This module handles the creation and tracking of asynchronous tasks via Celery.
"""

import logging
from typing import Union

from celery.result import AsyncResult
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from mork.auth import authenticate_api_key
from mork.db import get_session
from mork.edx.mysql.models.auth import AuthUser
from mork.models.users import User as MorkUser
from mork.schemas.tasks import (
    TASK_TYPE_TO_FUNC,
    DeleteInactiveUsers,
    DeleteUser,
    EmailInactiveUsers,
    EmailUser,
    TaskResponse,
    TaskStatus,
    TaskType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", dependencies=[Depends(authenticate_api_key)])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    response: Response,
    task: Union[DeleteInactiveUsers, EmailInactiveUsers, DeleteUser, EmailUser] = Body(
        discriminator="type"
    ),
) -> TaskResponse:
    """Creates a new asynchronous task based on the provided type.

    Returns the task ID and its initial status.
    """
    celery_task = TASK_TYPE_TO_FUNC[task.type]
    celery_params = task.model_dump(exclude="type", exclude_none=True)

    result = celery_task.delay(**celery_params)

    task_response = TaskResponse(id=result.task_id, status=TaskStatus.PENDING)
    response.headers["location"] = router.url_path_for(
        "get_task_status", **{"task_id": task_response.id}
    )
    return task_response


@router.options("")
@router.options("/")
async def get_available_tasks(response: Response) -> dict:
    """Returns the list of available task types for creation."""
    response.headers["allow"] = "POST"
    return {"task_types": list(TaskType)}


@router.get("/{task_id}/status")
async def get_task_status(task_id: str) -> TaskResponse:
    """Retrieves the status of a task from its ID."""
    status = AsyncResult(task_id).state

    return TaskResponse(id=task_id, status=status)


@router.post("/user-status-by-email", status_code=200)
async def user_status_by_email(
    email: str = Body(..., embed=True, description="User email to search for"),
    session: Session = Depends(get_session),
) -> dict:
    """Searches for a user by email and returns.

    - edx info (id, username, first_name, last_name, email, etc.)
    - Mork deletion status (service_statuses)
    """
    # Search in edx (auth_user)
    edx_user = session.execute(
        select(AuthUser).where(AuthUser.email == email)
    ).scalar_one_or_none()

    # Search in Mork (User)
    mork_user = session.execute(
        select(MorkUser).where(MorkUser.email == email)
    ).scalar_one_or_none()

    # Build response
    result = {"email": email}

    if edx_user:
        result["edx_user"] = {
            "id": edx_user.id,
            "username": edx_user.username,
            "first_name": edx_user.first_name,
            "last_name": edx_user.last_name,
            "is_active": bool(edx_user.is_active),
            "date_joined": (
                edx_user.date_joined.isoformat() if edx_user.date_joined else None
            ),
            "last_login": (
                edx_user.last_login.isoformat() if edx_user.last_login else None
            ),
        }
    else:
        result["edx_user"] = None

    if mork_user:
        # Deletion status for each service
        service_statuses = [
            {"service_name": s.service_name.value, "status": s.status.value}
            for s in mork_user.service_statuses
        ]
        result["mork_status"] = {
            "id": str(mork_user.id),
            "service_statuses": service_statuses,
            "reason": mork_user.reason.value,
            "created_at": (
                mork_user.created_at.isoformat()
                if hasattr(mork_user, "created_at") and mork_user.created_at
                else None
            ),
            "updated_at": (
                mork_user.updated_at.isoformat()
                if hasattr(mork_user, "updated_at") and mork_user.updated_at
                else None
            ),
        }
    else:
        result["mork_status"] = None

    if not edx_user and not mork_user:
        raise HTTPException(status_code=404, detail="No user found for this email.")

    return result
