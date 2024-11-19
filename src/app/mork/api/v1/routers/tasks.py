"""API tasks router."""

import logging
from typing import Union

from celery.result import AsyncResult
from fastapi import APIRouter, Body, Depends, Response, status

from mork.auth import authenticate_api_key
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
    """Create a new task."""
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
    """Get available tasks that can be created."""
    response.headers["allow"] = "POST"
    return {"task_types": list(TaskType)}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> TaskResponse:
    """Get the task status for `task_id`."""
    status = AsyncResult(task_id).state

    return TaskResponse(id=task_id, status=status)
