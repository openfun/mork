"""Tests for the Mork API '/users/' endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from mork.factories.users import (
    UserFactory,
    UserServiceStatusFactory,
)
from mork.models.users import (
    DeletionStatus,
    ServiceName,
    User,
    UserServiceStatus,
)


@pytest.mark.anyio
async def test_users_auth(http_client: AsyncClient):
    """Test required authentication for deletions endpoints."""
    # FastAPI returns a 403 error (instead of a 401 error) if no API token is given
    # see https://github.com/tiangolo/fastapi/discussions/9130
    assert (await http_client.get("/v1/users")).status_code == 403
    assert (await http_client.get("/v1/users/foo")).status_code == 403
    assert (await http_client.get("/v1/users/foo/status/bar")).status_code == 403
    assert (await http_client.patch("/v1/users/foo/status/bar")).status_code == 403


@pytest.mark.anyio
async def test_users_read_default(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the behavior of retrieving the list of users to be deleted."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create 200 users that need to be deleted on all services
    number_users = 200
    UserFactory.create_batch(number_users)

    response = await http_client.get("/v1/users", headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 200

    # Assert that the number of users matches the default limit (100)
    assert len(response_data) == 100

    # Assert that all users are unique
    assert len({user["id"] for user in response_data}) == len(response_data)

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize(
    "offset, limit, number_users",
    [
        (10, 100, 50),
        (0, 75, 100),
        (100, 75, 100),
        (100, 100, 200),
        (0, 0, 100),
        (50, 0, 10),
    ],
)
async def test_users_read_pagination(  # noqa: PLR0913
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    offset: int,
    limit: int,
    number_users: int,
):
    """Test the pagination behavior of retrieving users."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some user requests in the database
    UserFactory.create_batch(number_users)

    # Assert the expected number of users have been created
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users

    # Get users with pagination
    response = await http_client.get(
        "/v1/users",
        headers=auth_headers,
        params={
            "deletion_status": "to_delete",
            "service": "ashley",
            "offset": offset,
            "limit": limit,
        },
    )
    response_data = response.json()
    assert response.status_code == 200

    # Assert that the number of users matches the pagination params
    expected_count = min(limit, max(0, number_users - offset))
    assert len(response_data) == expected_count

    # Assert that all user IDs are unique
    assert len({user["id"] for user in response_data}) == len(response_data)

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_params",
    [
        {"deletion_status": "wrong_status", "service": "ashley"},
        {"deletion_status": "to_delete", "service": "wrong_service"},
        {"deletion_status": "to_delete", "service": "ashley", "limit": 1001},
        {"deletion_status": "to_delete", "service": "ashley", "offset": -1},
    ],
)
async def test_users_read_invalid_params(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    invalid_params: dict,
):
    """Test scenarios with invalid query params when retrieving users."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users
    number_users = 10
    UserFactory.create_batch(number_users)

    # Read users with invalid query parameters
    response = await http_client.get(
        "/v1/users", headers=auth_headers, params=invalid_params
    )

    # Assert the request fails
    assert response.status_code == 422

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({"deletion_status": "to_delete"}, 5),
        ({"deletion_status": "deleted"}, 6),
        ({"deletion_status": "to_delete", "service": "ashley"}, 3),
        ({"deletion_status": "to_delete", "service": "joanie"}, 2),
        ({"deletion_status": "to_delete", "service": "brevo"}, 0),
    ],
)
async def test_users_read_filter(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    params: dict,
    expected_count: int,
):
    """Test scenarios with valid query parameters when retrieving users."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Attempt to retrieve users when the database is empty
    # with valid query parameters
    response = await http_client.get("/v1/users", headers=auth_headers, params=params)
    assert response.status_code == 200
    assert response.json() == []

    # Create 3 users to be deleted for Ashley
    UserFactory.create_batch(
        3,
        service_statuses={
            ServiceName.ASHLEY: DeletionStatus.TO_DELETE,
            ServiceName.BREVO: DeletionStatus.DELETED,
            ServiceName.EDX: DeletionStatus.DELETED,
            ServiceName.JOANIE: DeletionStatus.DELETED,
        },
    )
    # Create 2 users to be deleted for Joanie
    UserFactory.create_batch(
        2,
        service_statuses={
            ServiceName.ASHLEY: DeletionStatus.DELETED,
            ServiceName.BREVO: DeletionStatus.DELETED,
            ServiceName.EDX: DeletionStatus.DELETED,
            ServiceName.JOANIE: DeletionStatus.TO_DELETE,
        },
    )
    # Create 1 user deleted from all services
    UserFactory.create_batch(
        1,
        service_statuses={
            ServiceName.ASHLEY: DeletionStatus.DELETED,
            ServiceName.BREVO: DeletionStatus.DELETED,
            ServiceName.EDX: DeletionStatus.DELETED,
            ServiceName.JOANIE: DeletionStatus.DELETED,
        },
    )

    # Read users with valid query parameters
    response = await http_client.get(
        "/v1/users",
        headers=auth_headers,
        params=params,
    )

    response_data = response.json()
    assert response.status_code == 200

    # Verify we have the expected count
    assert len(response_data) == expected_count

    # Verify all IDs are unique
    assert len({user["id"] for user in response_data}) == expected_count

    # Verify the total count in database hasn't changed
    total_requests = (
        db_session.execute(
            select(User)
            .join(UserServiceStatus)
            .where(UserServiceStatus.status == DeletionStatus.TO_DELETE)
        )
        .scalars()
        .all()
    )
    assert len(total_requests) == 5


@pytest.mark.anyio
async def test_user_read(db_session, http_client: AsyncClient, auth_headers: dict):
    """Test the behavior of retrieving one user."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user that needs to be deleted on all services
    user = UserFactory.create()

    # Get id of newly created user
    user_id = db_session.scalar(select(User.id))

    response = await http_client.get(f"/v1/users/{str(user_id)}", headers=auth_headers)

    assert response.status_code == 200

    # Verify the retrieved data matches the expected format
    assert response.json() == {
        "id": str(user_id),
        "username": user.username,
        "edx_user_id": user.edx_user_id,
        "email": user.email,
        "reason": user.reason.value,
        "service_statuses": [
            {
                "service_name": "ashley",
                "status": "to_delete",
            },
            {
                "service_name": "edx",
                "status": "to_delete",
            },
            {
                "service_name": "brevo",
                "status": "to_delete",
            },
            {
                "service_name": "joanie",
                "status": "to_delete",
            },
        ],
    }


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_read_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of retrieving one user with an invalid id."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users in the database
    number_users = 10
    UserFactory.create_batch(number_users)

    # Attempt to read a user with an invalid ID
    response = await http_client.get(f"/v1/users/{invalid_id}", headers=auth_headers)

    assert response.status_code == 422

    # Attempt to read an user with a nonexistent ID
    nonexistent_id = uuid4().hex
    response = await http_client.get(
        f"/v1/users/{nonexistent_id}", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
async def test_user_read_invalid_params(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
):
    """Test the behavior of retrieving one user with invalid query params."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user
    UserFactory.create()

    # Get id of newly created user
    user_id = db_session.scalar(select(User.id))

    # Read user with invalid query parameters
    response = await http_client.get(
        f"/v1/users/{user_id}",
        headers=auth_headers,
        params={"service": "wrong_service"},
    )

    # Assert the request fails
    assert response.status_code == 422

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == 1


@pytest.mark.anyio
async def test_user_read_status(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the behavior of retrieving the status of a user."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user that need to be deleted on all services
    UserFactory.create()

    # Get id of newly created user
    user_id = db_session.scalar(select(User.id))

    response = await http_client.get(
        f"/v1/users/{str(user_id)}/status/ashley", headers=auth_headers
    )

    assert response.status_code == 200

    # Verify the retrieved data matches the expected format
    assert response.json() == {
        "id": str(user_id),
        "service_name": "ashley",
        "status": "to_delete",
    }


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_read_status_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of retrieving a user status with an invalid user id."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users in the database
    number_users = 10
    UserFactory.create_batch(number_users)

    # Attempt to read a user with an invalid ID
    response = await http_client.get(
        f"/v1/users/{invalid_id}/status/ashley", headers=auth_headers
    )

    assert response.status_code == 422

    # Attempt to read an user with a nonexistent ID
    nonexistent_id = uuid4().hex
    response = await http_client.get(
        f"/v1/users/{nonexistent_id}/status/ashley", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User status not found"}

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_service", ["foo", 123])
async def test_user_read_status_invalid_service(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_service
):
    """Test the behavior of retrieving a user status with an invalid service name."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users in the database
    number_users = 10
    UserFactory.create_batch(number_users)

    # Get id of one of the newly created user
    user_id = db_session.scalar(select(User.id))

    # Attempt to read a user status with an invalid service
    response = await http_client.get(
        f"/v1/users/{user_id}/status/{invalid_service}", headers=auth_headers
    )

    assert response.status_code == 422

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize(
    "service_name, deletion_status",
    [
        ("ashley", "deleting"),
        ("brevo", "deleting"),
        ("edx", "deleted"),
        ("joanie", "deleted"),
    ],
)
async def test_users_update_status_default(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    service_name: str,
    deletion_status: str,
):
    """Test the behavior of updating the deletion status for a user on a service."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    user = UserFactory.create()

    # Assert user is to be deleted on the service
    status = (
        db_session.execute(
            select(UserServiceStatus.status).where(
                UserServiceStatus.service_name == service_name
            )
        )
        .scalars()
        .one()
    )
    assert status == DeletionStatus.TO_DELETE

    # Update the status of the user for a service
    response = await http_client.patch(
        f"/v1/users/{user.id}/status/{service_name}",
        headers=auth_headers,
        json={"deletion_status": deletion_status},
    )

    response_data = response.json()

    assert response.status_code == 200

    # Assert response is as expected
    assert response_data["id"] == str(user.id)
    assert response_data["service_name"] == service_name
    assert response_data["status"] == deletion_status

    # Assert that user status has correctly been updated
    updated_status = (
        db_session.execute(
            select(UserServiceStatus.status).where(
                UserServiceStatus.service_name == service_name
            )
        )
        .scalars()
        .one()
    )
    assert updated_status == deletion_status

    # Assert only this status has been updated
    number_updated = db_session.execute(
        select(func.count()).where(UserServiceStatus.status == deletion_status)
    ).scalar()
    assert number_updated == 1


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_update_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of updating a user status for an invalid user id."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users in the database
    number_users = 10
    UserFactory.create_batch(number_users)

    # Attempt to update a user with an invalid ID
    response = await http_client.patch(
        f"/v1/users/{invalid_id}/status/ashley",
        headers=auth_headers,
        json={"deletion_status": "deleted"},
    )

    assert response.status_code == 422

    # Attempt to update a user with a nonexistent ID
    nonexistent_id = uuid4().hex
    response = await http_client.patch(
        f"/v1/users/{nonexistent_id}/status/ashley",
        headers=auth_headers,
        json={"deletion_status": "deleted"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User status not found"}

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_service", ["foo", 123])
async def test_user_update_status_invalid_service(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_service
):
    """Test the behavior of updating a user status for an invalid service name."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users in the database
    number_users = 10
    UserFactory.create_batch(number_users)

    # Get id of one of the newly created user
    user_id = db_session.scalar(select(User.id))

    # Attempt to read a user status with an invalid service
    response = await http_client.patch(
        f"/v1/users/{user_id}/status/{invalid_service}", headers=auth_headers
    )

    assert response.status_code == 422

    # Assert the database still contains the same number of users
    users = db_session.execute(select(User)).all()
    assert len(users) == number_users


@pytest.mark.anyio
@pytest.mark.parametrize(
    "deletion_status",
    [
        "wrong_status",
        123,
    ],
)
async def test_users_update_status_invalid_status(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    deletion_status: str,
):
    """Test the behavior of updating the user status with an invalid status"""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    user = UserFactory.create()

    # Try to update status with invalid parameters
    response = await http_client.patch(
        f"/v1/users/{user.id}/status/ashley",
        headers=auth_headers,
        json={"deletion_status": deletion_status},
    )

    # Assert the request fails
    assert response.status_code == 422
