"""Tests for Mork Celery Sarbacane tasks."""

import logging
import uuid
from unittest.mock import Mock
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select

from mork.celery.tasks.sarbacane import (
    delete_sarbacane_platform_user,
    delete_sarbacane_user,
)
from mork.conf import settings
from mork.exceptions import (
    UserDeleteError,
    UserNotFound,
    UserStatusError,
)
from mork.factories.users import UserFactory, UserServiceStatusFactory
from mork.models.users import DeletionStatus, ServiceName, User
from mork.schemas.users import UserRead


def test_delete_sarbacane_platform_user(db_session, monkeypatch):
    """Test to delete user from Sarbacane platform."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: user
    )

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.update_status_in_mork", mock_update_status_in_mork
    )

    delete_sarbacane_platform_user(user.id)

    mock_delete_sarbacane_user.assert_called_once_with(email=user.email)
    mock_update_status_in_mork.assert_called_once_with(
        user_id=user.id, service=ServiceName.SARBACANE, status=DeletionStatus.DELETED
    )


def test_delete_sarbacane_platform_user_empty_setting(db_session, monkeypatch):
    """Test to delete user from Sarbacane platform when the API URL is not set."""

    monkeypatch.setattr("mork.celery.tasks.sarbacane.settings.SARBACANE_API_URL", "")

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )

    delete_sarbacane_platform_user(uuid.uuid4())

    mock_delete_sarbacane_user.assert_not_called()


def test_delete_sarbacane_platform_user_invalid_user(monkeypatch):
    """Test to delete user from Sarbacane platform with an invalid user."""

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: None
    )

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.update_status_in_mork", mock_update_status_in_mork
    )

    nonexistent_id = uuid4().hex
    with pytest.raises(
        UserNotFound, match=f"User {nonexistent_id} could not be retrieved from Mork"
    ):
        delete_sarbacane_platform_user(nonexistent_id)

    mock_delete_sarbacane_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_sarbacane_platform_user_deleted_status(db_session, monkeypatch, caplog):
    """Test to delete user from Sarbacane platform already deleted."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on sarbacane
    UserFactory.create(
        service_statuses={ServiceName.SARBACANE: DeletionStatus.DELETED},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: user
    )

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.update_status_in_mork", mock_update_status_in_mork
    )

    # User is already deleted, silently exit the task
    with caplog.at_level(logging.WARNING):
        delete_sarbacane_platform_user(user.id)

    assert (
        "mork.celery.tasks.sarbacane",
        logging.WARNING,
        f"User {str(user.id)} has already been deleted.",
    ) in caplog.record_tuples

    mock_delete_sarbacane_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_sarbacane_platform_user_invalid_status(db_session, monkeypatch, caplog):
    """Test to delete user from Sarbacane platform with an invalid status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is being deleted on sarbacane
    UserFactory.create(
        service_statuses={ServiceName.SARBACANE: DeletionStatus.DELETING},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: user
    )

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"User {str(user.id)} cannot be deleted. Status: DeletionStatus.DELETING",
    ):
        delete_sarbacane_platform_user(user.id)

    mock_delete_sarbacane_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_sarbacane_platform_user_failed_delete(db_session, monkeypatch):
    """Test to delete user from Sarbacane platform with a failed delete."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on sarbacane
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: user
    )

    def mock_delete_sarbacane_user(*args, **kwars):
        raise UserDeleteError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_sarbacane_platform_user(user.id)


def test_delete_sarbacane_platform_user_failed_status_update(db_session, monkeypatch):
    """Test to delete user from Sarbacane platform with a failed status update."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on sarbacane
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.get_user_from_mork", lambda x: user
    )

    mock_delete_sarbacane_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.delete_sarbacane_user", mock_delete_sarbacane_user
    )
    mock_update_status_in_mork = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"Failed to update deletion status to 'DELETED' for user {user.id}",
    ):
        delete_sarbacane_platform_user(user.id)


def test_delete_sarbacane_user(httpx_mock):
    """Test to delete user's data from Sarbacane."""

    email = "johndoe@example.com"

    headers = {"apiKey": "not-a-real-api-key", "accountID": "not-a-real-key"}
    # Mock requests on /lists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[{"id": "list0"}, {"id": "list1"}],
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists/list0/contacts?email={email}",
        method="DELETE",
        headers=headers,
        status_code=500,
        json={"message": "No contacts versions to delete"},
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists/list1/contacts?email={email}",
        method="DELETE",
        headers=headers,
        status_code=200,
    )

    # Mock requests on /blacklists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[{"id": "blacklist0"}, {"id": "blacklist1"}],
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists/blacklist0/unsubscribers?email={email}",
        method="DELETE",
        headers=headers,
        status_code=500,
        json={"message": "No contacts versions to delete"},
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists/blacklist1/unsubscribers?email={email}",
        method="DELETE",
        headers=headers,
        status_code=200,
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists/blacklist0/complaints?email={email}",
        method="DELETE",
        headers=headers,
        status_code=200,
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists/blacklist1/complaints?email={email}",
        method="DELETE",
        headers=headers,
        status_code=200,
    )

    delete_sarbacane_user(email)


def test_delete_sarbacane_user_request_error(httpx_mock, monkeypatch):
    """Test to delete user's data from Sarbacane with a request error."""

    # User request error when deleting the contact
    headers = {"apiKey": "not-a-real-api-key", "accountID": "not-a-real-key"}
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[{"id": "list0"}],
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[],
    )

    def mock_httpx_delete(*args, **kwars):
        raise httpx.RequestError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.sarbacane.httpx.Client.delete", mock_httpx_delete
    )

    with pytest.raises(
        UserDeleteError,
        match="Network error while deleting user contact at /lists/list0/contacts",
    ):
        delete_sarbacane_user("johndoe@example.com")

    # User request error when retrieving the list ids
    def mock_httpx_get(*args, **kwars):
        raise httpx.RequestError("An error occurred")

    monkeypatch.setattr("mork.celery.tasks.sarbacane.httpx.Client.get", mock_httpx_get)

    with pytest.raises(
        UserDeleteError, match="Network error while retrieving lists of contacts"
    ):
        delete_sarbacane_user("johndoe@example.com")


def test_delete_sarbacane_user_not_found(httpx_mock, caplog):
    """Test to delete user's data from Sarbacane when no contact found."""

    email = "johndoe@example.com"

    headers = {"apiKey": "not-a-real-api-key", "accountID": "not-a-real-key"}
    # Mock requests on /lists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[{"id": "list0"}],
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists/list0/contacts?email={email}",
        method="DELETE",
        headers=headers,
        status_code=500,
        json={"message": "No contacts versions to delete"},
    )

    # Mock requests on /blacklists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists",
        method="GET",
        headers=headers,
        status_code=200,
        json={},
    )

    # Make sure no error is raised if contact not found on Sarbacane
    with caplog.at_level(logging.INFO):
        delete_sarbacane_user("johndoe@example.com")

    assert (
        "mork.celery.tasks.sarbacane",
        logging.INFO,
        "User not found at /lists/list0/contacts",
    ) in caplog.record_tuples


def test_delete_sarbacane_user_delete_error(httpx_mock):
    """Test to delete user's data from Sarbacane with API returning a 5**."""

    email = "johndoe@example.com"

    headers = {"apiKey": "not-a-real-api-key", "accountID": "not-a-real-key"}
    # Mock requests on /lists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[{"id": "list0"}],
    )
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/lists/list0/contacts?email={email}",
        method="DELETE",
        headers=headers,
        status_code=500,
    )

    # Mock requests on /blacklists endpoint
    httpx_mock.add_response(
        url=f"{settings.SARBACANE_API_URL}/blacklists",
        method="GET",
        headers=headers,
        status_code=200,
        json=[],
    )

    with pytest.raises(
        UserDeleteError, match="Failed to delete user contact at /lists/list0/contacts"
    ):
        delete_sarbacane_user("johndoe@example.com")
