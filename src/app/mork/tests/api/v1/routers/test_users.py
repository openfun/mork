"""
Tests for the '/users/' endpoints of the Mork API.

- Verifies authentication, pagination, filters, reading and updating user statuses.
- Tests enhanced filtering by email and username (partial and exact matching).
- Tests flexible user lookup by UUID or email.
"""

from dataclasses import dataclass
from uuid import uuid4

import pytest
from httpx import AsyncClient

from mork.factories.users import (
    UserFactory,
    UserServiceStatusFactory,
)
from mork.models.users import (
    DeletionStatus,
    ServiceName,
)


@dataclass
class EmailFilterTestParams:
    """Parameters for email filter tests."""
    email_filter: str
    expected_count: int


@dataclass
class UsernameFilterTestParams:
    """Parameters for username filter tests."""
    username_filter: str
    expected_count: int


@pytest.mark.anyio
async def test_users_auth(http_client: AsyncClient):
    """Test that the users endpoint requires authentication."""
    response = await http_client.get("/v1/users")
    assert response.status_code == 403  # FastAPI returns 403 for missing API key


@pytest.mark.anyio
async def test_users_read_default(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the default behavior of the users endpoint."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users
    UserFactory()
    UserFactory()
    UserFactory()

    response = await http_client.get("/v1/users", headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == 3
    assert all("id" in user for user in response_data)
    assert all("email" in user for user in response_data)
    assert all("username" in user for user in response_data)


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
    """Test pagination functionality."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create users
    for _ in range(number_users):
        UserFactory()

    params = {"offset": offset, "limit": limit}
    response = await http_client.get(
        "/v1/users", headers=auth_headers, params=params
    )
    response_data = response.json()

    assert response.status_code == 200
    expected_count = min(limit, max(0, number_users - offset))
    assert len(response_data) == expected_count


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_params",
    [
        {"limit": 1001},  # Limit too high
        {"offset": -1},   # Negative offset
    ],
)
async def test_users_read_invalid_params(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    invalid_params: dict,
):
    """Test that invalid parameters return appropriate errors."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create some users
    UserFactory()
    UserFactory()

    response = await http_client.get(
        "/v1/users", headers=auth_headers, params=invalid_params
    )
    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({"email": "test"}, 1),  # Partial email match
        ({"username": "user"}, 2),  # Partial username match
        # Combined filters - should match user1
        ({"email": "test", "username": "user"}, 1),
    ],
)
async def test_users_read_filter(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    params: dict,
    expected_count: int,
):
    """Test filtering functionality."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create users with specific emails and usernames
    UserFactory(email="test@example.com", username="user1")
    UserFactory(email="other@example.com", username="user2")
    UserFactory(email="another@example.com", username="admin")

    response = await http_client.get("/v1/users", headers=auth_headers, params=params)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data) == expected_count


@pytest.mark.anyio
@pytest.mark.parametrize(
    "test_params",
    [
        # Partial match - only test@example.com contains "test"
        EmailFilterTestParams("test", 1),
        EmailFilterTestParams("user1", 1),  # Partial match
        # Partial match (no exact option)
        EmailFilterTestParams("user1@example.com", 1),
        EmailFilterTestParams("nonexistent", 0),  # No match
    ],
)
async def test_users_read_email_filter(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    test_params: EmailFilterTestParams,
):
    """Test email filtering functionality."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create users with specific emails
    UserFactory(email="user1@example.com")
    UserFactory(email="user2@example.com")
    UserFactory(email="test@example.com")

    params = {"email": test_params.email_filter}
    # email_exact parameter no longer supported, always uses partial matching

    response = await http_client.get("/v1/users", headers=auth_headers, params=params)
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == test_params.expected_count


@pytest.mark.anyio
@pytest.mark.parametrize(
    "test_params",
    [
        UsernameFilterTestParams("user1", 1),  # Partial match
        UsernameFilterTestParams("user1", 1),  # Partial match (no exact option)
        UsernameFilterTestParams("nonexistent", 0),  # No match
        UsernameFilterTestParams("test", 1),  # Partial match
    ],
)
async def test_users_read_username_filter(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
    test_params: UsernameFilterTestParams,
):
    """Test username filtering functionality."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create users with specific usernames
    UserFactory(username="user1")
    UserFactory(username="user2")
    UserFactory(username="test")

    params = {"username": test_params.username_filter}
    # username_exact parameter no longer supported, always uses partial matching

    response = await http_client.get("/v1/users", headers=auth_headers, params=params)
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == test_params.expected_count


@pytest.mark.anyio
async def test_users_read_combined_filters(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
):
    """Test combined filtering (email + username)."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create users with specific combinations
    UserFactory(
        email="john@example.com",
        username="johnsmith",
    )
    UserFactory(
        email="john@test.com",
        username="johndoe",
    )
    UserFactory(
        email="jane@example.com",
        username="jane",
    )

    # Test combined filter
    params = {
        "email": "john",
        "username": "john",
    }

    response = await http_client.get("/v1/users", headers=auth_headers, params=params)
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 2  # Both john users


@pytest.mark.anyio
async def test_user_read(db_session, http_client: AsyncClient, auth_headers: dict):
    """Test the behavior of retrieving a specific user by UUID."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user with a non-deleted status for at least one service
    user = UserFactory(service_statuses={ServiceName.ASHLEY: DeletionStatus.PROTECTED})
    db_session.flush()  # Ensure the user gets an ID

    # Retrieve the user by UUID
    response = await http_client.get(
        f"/v1/users/{user.id}", headers=auth_headers
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["id"] == str(user.id)
    assert response_data["email"] == user.email
    assert response_data["username"] == user.username


@pytest.mark.anyio
async def test_user_read_by_email(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the behavior of retrieving a specific user by email."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user with a non-deleted status for at least one service
    user = UserFactory(
        email="test@example.com",
        service_statuses={ServiceName.ASHLEY: DeletionStatus.PROTECTED}
    )
    db_session.flush()

    # Retrieve the user by email
    response = await http_client.get(
        f"/v1/users/{user.email}", headers=auth_headers
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["id"] == str(user.id)
    assert response_data["email"] == user.email
    assert response_data["username"] == user.username


@pytest.mark.anyio
async def test_user_read_by_email_with_exclude_deleted(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test retrieving user by email with exclude_deleted parameter."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user with deletion status
    user = UserFactory(
        email="deleted@example.com",
        service_statuses={ServiceName.EDX: DeletionStatus.TO_DELETE}
    )

    # Try to retrieve with exclude_deleted=true (default)
    response = await http_client.get(
        f"/v1/users/{user.email}", headers=auth_headers
    )
    assert response.status_code == 404

    # Retrieve with exclude_deleted=false
    response = await http_client.get(
        f"/v1/users/{user.email}?exclude_deleted=false", headers=auth_headers
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["id"] == str(user.id)
    assert response_data["email"] == user.email


@pytest.mark.anyio
async def test_user_read_with_invalid_email(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the behavior of retrieving a user with an invalid email format."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    UserFactory()

    # Try to retrieve with an invalid email format
    response = await http_client.get(
        "/v1/users/invalid-email-format", headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_read_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of retrieving a user with an invalid ID format."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    UserFactory()

    # Try to retrieve with an invalid ID
    response = await http_client.get(
        f"/v1/users/{invalid_id}", headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_user_read_invalid_params(
    db_session,
    http_client: AsyncClient,
    auth_headers: dict,
):
    """Test that invalid parameters return appropriate errors."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    user = UserFactory()
    db_session.flush()

    # Try to retrieve with invalid parameter (service no longer supported)
    response = await http_client.get(
        f"/v1/users/{user.id}?service=invalid_service", headers=auth_headers
    )
    # Should return 404 since service parameter is ignored and user is not found
    # due to exclude_deleted=True by default
    assert response.status_code == 404


@pytest.mark.anyio
async def test_user_read_status(
    db_session, http_client: AsyncClient, auth_headers: dict
):
    """Test the behavior of retrieving a user's status for a specific service."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user with a specific status
    user = UserFactory(service_statuses={ServiceName.ASHLEY: DeletionStatus.TO_DELETE})
    db_session.flush()

    # Retrieve the user's status
    response = await http_client.get(
        f"/v1/users/{user.id}/status/ashley", headers=auth_headers
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["id"] == str(user.id)
    assert response_data["service_name"] == "ashley"
    assert response_data["status"] == "to_delete"

    # Verify the status was actually updated in the database
    db_session.refresh(user)
    service_status = next(
        (status for status in user.service_statuses
         if status.service_name.value == "ashley"),
        None
    )
    assert service_status is not None
    assert service_status.status.value == "to_delete"


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_read_status_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of retrieving a user's status with an invalid ID format."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    UserFactory()

    # Try to retrieve status with an invalid ID
    response = await http_client.get(
        f"/v1/users/{invalid_id}/status/ashley", headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_service", ["foo", 123])
async def test_user_read_status_invalid_service(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_service
):
    """Test the behavior of retrieving a user's status with an invalid service."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    user = UserFactory()
    db_session.flush()

    # Try to retrieve status with an invalid service
    response = await http_client.get(
        f"/v1/users/{user.id}/status/{invalid_service}", headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "service_name, deletion_status",
    [
        ("ashley", "deleting"),
        ("sarbacane", "deleting"),
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
    """Test the behavior of updating a user's status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user with an initial status
    user = UserFactory(service_statuses={ServiceName.ASHLEY: DeletionStatus.PROTECTED})
    db_session.flush()

    # Update the user's status
    response = await http_client.patch(
        f"/v1/users/{user.id}/status/{service_name}",
        headers=auth_headers,
        json={"deletion_status": deletion_status}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["id"] == str(user.id)
    assert response_data["service_name"] == service_name
    assert response_data["status"] == deletion_status

    # Verify the status was actually updated in the database
    db_session.refresh(user)
    service_status = next(
        (status for status in user.service_statuses
         if status.service_name.value == service_name),
        None
    )
    assert service_status is not None
    assert service_status.status.value == deletion_status


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_id", ["foo", 123, "a1-a2-aa", uuid4().hex + "a"])
async def test_user_update_invalid_id(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_id
):
    """Test the behavior of updating a user's status with an invalid ID format."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    UserFactory()

    # Try to update status with an invalid ID
    response = await http_client.patch(
        f"/v1/users/{invalid_id}/status/ashley",
        headers=auth_headers,
        json={"deletion_status": "deleting"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_service", ["foo", 123])
async def test_user_update_status_invalid_service(
    db_session, http_client: AsyncClient, auth_headers: dict, invalid_service
):
    """Test the behavior of updating a user's status with an invalid service."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    user = UserFactory()
    db_session.flush()

    # Try to update status with an invalid service
    response = await http_client.patch(
        f"/v1/users/{user.id}/status/{invalid_service}",
        headers=auth_headers,
        json={"deletion_status": "deleting"}
    )
    assert response.status_code == 422


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
    """Test the behavior of updating a user's status with an invalid status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create a user
    user = UserFactory()
    db_session.flush()

    # Try to update status with an invalid status
    response = await http_client.patch(
        f"/v1/users/{user.id}/status/ashley",
        headers=auth_headers,
        json={"deletion_status": deletion_status}
    )
    assert response.status_code == 422
