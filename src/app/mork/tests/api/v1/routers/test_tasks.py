"""Tests for the Mork API '/tasks/' endpoints."""

from unittest.mock import Mock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_tasks_auth(http_client: AsyncClient):
    """Test required authentication for tasks endpoints."""
    # FastAPI returns a 403 error (instead of a 401 error) if no API token is given
    # see https://github.com/tiangolo/fastapi/discussions/9130
    assert (await http_client.post("/v1/tasks/")).status_code == 403
    assert (await http_client.options("/v1/tasks/")).status_code == 403
    assert (await http_client.get("/v1/tasks/status/1234")).status_code == 403


@pytest.mark.anyio
@pytest.mark.parametrize(
    "body_params",
    [
        {"type": "email_inactive_users", "dry_run": False},
        {"type": "email_inactive_users", "limit": 100, "dry_run": False},
        {
            "type": "email_user",
            "email": "johndoe@example.com",
            "username": "JohnDoe",
            "dry_run": False,
        },
        {"type": "delete_inactive_users", "dry_run": False},
        {"type": "delete_inactive_users", "limit": 100, "dry_run": False},
        {"type": "delete_user", "email": "johndoe@example.com", "dry_run": False},
        {"type": "email_inactive_users", "dry_run": True},
        {
            "type": "email_user",
            "email": "johndoe@example.com",
            "username": "JohnDoe",
            "dry_run": True,
        },
        {"type": "delete_inactive_users", "dry_run": True},
        {"type": "delete_user", "email": "johndoe@example.com", "dry_run": True},
    ],
)
@pytest.mark.parametrize(
    "tasks_endpoint",
    ["/v1/tasks/", "/v1/tasks"],
)
async def test_create_task(
    http_client: AsyncClient, auth_headers: dict, body_params: str, tasks_endpoint: str
):
    """Test creating a task with valid data."""

    celery_task = Mock()
    celery_task.delay.return_value.task_id = "1234"

    with patch.dict(
        "mork.api.v1.tasks.TASK_TYPE_TO_FUNC", {body_params["type"]: celery_task}
    ):
        response = await http_client.post(
            tasks_endpoint, headers=auth_headers, json=body_params
        )
        response_data = response.json()

        assert response.status_code == 202
        assert response_data.get("id")
        assert response_data.get("status") == "PENDING"
        assert (
            response.headers["location"] == f"/tasks/status/{response_data.get("id")}"
        )

        expected_params = {
            key: value for key, value in body_params.items() if key != "type"
        }
        celery_task.delay.assert_called_with(**expected_params)


@pytest.mark.anyio
async def test_create_task_invalid_type(http_client: AsyncClient, auth_headers: dict):
    """Test creating a task with an invalid type."""

    # Without a type
    with patch.dict("mork.api.v1.tasks.TASK_TYPE_TO_FUNC"):
        response = await http_client.post("/v1/tasks/", headers=auth_headers)

        assert response.status_code == 422

    # With a wrong type
    mock_task_create = {"type": "wrong_type"}

    celery_task = Mock()
    celery_task.delay.return_value.task_id = "1234"

    with patch.dict("mork.api.v1.tasks.TASK_TYPE_TO_FUNC"):
        response = await http_client.post(
            "/v1/tasks/", headers=auth_headers, json=mock_task_create
        )

        assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "task_type, params",
    [
        ("delete_user", {}),
        ("email_user", {"email": "johndoe@example.com"}),
        ("email_user", {"username": "JohnDoe"}),
    ],
)
async def test_create_task_missing_param(
    http_client: AsyncClient, auth_headers: dict, task_type: str, params: dict
):
    """Test creating a task with a missing parameter."""

    mock_task_create = {"type": task_type, **params}

    celery_task = Mock()
    celery_task.delay.return_value.task_id = "1234"

    with patch.dict("mork.api.v1.tasks.TASK_TYPE_TO_FUNC", {task_type: celery_task}):
        response = await http_client.post(
            "/v1/tasks/", headers=auth_headers, json=mock_task_create
        )
        response_data = response.json()

        assert response.status_code == 422
        assert response_data["detail"][0]["msg"] == "Field required"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "tasks_endpoint",
    ["/v1/tasks/", "/v1/tasks"],
)
async def test_get_available_tasks(
    http_client: AsyncClient, auth_headers: dict, tasks_endpoint: str
):
    """Test getting available tasks."""
    response = await http_client.options(tasks_endpoint, headers=auth_headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response.headers["allow"] == "POST"
    assert sorted(response_data.get("task_types")) == [
        "delete_inactive_users",
        "delete_user",
        "email_inactive_users",
        "email_user",
    ]


@pytest.mark.anyio
async def test_get_task_status(http_client: AsyncClient, auth_headers: dict):
    """Test getting task status."""

    task_id = "1234"
    celery_result = Mock(task_id)
    celery_result(task_id).state = "SUCCESS"

    with patch("mork.api.v1.tasks.AsyncResult", celery_result):
        response = await http_client.get(
            f"/v1/tasks/status/{task_id}",
            headers=auth_headers,
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data.get("status") == "SUCCESS"
