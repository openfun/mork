"""API routes related to tasks."""

import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Response, status

from mork.api.auth import authenticate_api_key
from mork.api.models import TaskCreate, TaskResponse, TaskStatus, TaskType
from mork.worker.tasks import TASK_TYPE_TO_FUNC

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", dependencies=[Depends(authenticate_api_key)])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_task(task_in: TaskCreate, response: Response) -> TaskResponse:
    """Create a new task."""
    celery_task = TASK_TYPE_TO_FUNC[task_in.type]
    result = celery_task.delay()

    task = TaskResponse(id=result.task_id, status=TaskStatus.PENDING)
    response.headers["location"] = router.url_path_for(
        "get_task_status", **{"task_id": task.id}
    )
    return task


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
