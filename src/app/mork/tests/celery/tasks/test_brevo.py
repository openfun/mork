"""Tests for Mork Celery Brevo tasks."""

import logging
import uuid
from unittest.mock import Mock
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select

from mork.celery.tasks.brevo import (
    delete_brevo_platform_user,
    delete_brevo_user,
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


def test_delete_brevo_platform_user(db_session, monkeypatch):
    """Test to delete user from Brevo platform."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.brevo.get_user_from_mork", lambda x: user)

    mock_delete_brevo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.update_status_in_mork", mock_update_status_in_mork
    )

    delete_brevo_platform_user(user.id)

    mock_delete_brevo_user.assert_called_once_with(email=user.email)
    mock_update_status_in_mork.assert_called_once_with(
        user_id=user.id, service=ServiceName.BREVO, status=DeletionStatus.DELETED
    )


def test_delete_brevo_platform_user_empty_setting(db_session, monkeypatch):
    """Test to delete user from Brevo platform when the API URL is not set."""

    monkeypatch.setattr("mork.celery.tasks.brevo.settings.BREVO_API_URL", "")

    mock_delete_brevo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )

    delete_brevo_platform_user(uuid.uuid4())

    mock_delete_brevo_user.assert_not_called()


def test_delete_brevo_platform_user_invalid_user(monkeypatch):
    """Test to delete user from Brevo platform with an invalid user."""

    monkeypatch.setattr("mork.celery.tasks.brevo.get_user_from_mork", lambda x: None)

    mock_delete_brevo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.update_status_in_mork", mock_update_status_in_mork
    )

    nonexistent_id = uuid4().hex
    with pytest.raises(
        UserNotFound, match=f"User {nonexistent_id} could not be retrieved from Mork"
    ):
        delete_brevo_platform_user(nonexistent_id)

    mock_delete_brevo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_brevo_platform_user_invalid_status(db_session, monkeypatch):
    """Test to delete user from Brevo platform with an invalid status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on brevo
    UserFactory.create(
        service_statuses={ServiceName.BREVO: DeletionStatus.DELETED},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.brevo.get_user_from_mork", lambda x: user)

    mock_delete_brevo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"User {str(user.id)} is not to be deleted. Status: DeletionStatus.DELETED",  # noqa: E501
    ):
        delete_brevo_platform_user(user.id)

    mock_delete_brevo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_brevo_platform_user_failed_delete(db_session, monkeypatch):
    """Test to delete user from Brevo platform with a failed delete."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on brevo
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.brevo.get_user_from_mork", lambda x: user)

    def mock_delete_brevo_user(*args, **kwars):
        raise UserDeleteError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_brevo_platform_user(user.id)


def test_delete_brevo_platform_user_failed_status_update(db_session, monkeypatch):
    """Test to delete user from Brevo platform with a failed status update."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on brevo
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.brevo.get_user_from_mork", lambda x: user)

    mock_delete_brevo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.delete_brevo_user", mock_delete_brevo_user
    )
    mock_update_status_in_mork = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.brevo.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"Failed to update deletion status to deleted for user {user.id}",
    ):
        delete_brevo_platform_user(user.id)


def test_delete_brevo_user(httpx_mock):
    """Test to delete user's data from Brevo."""

    email = "johndoe@example.com"

    httpx_mock.add_response(
        url=f"{settings.BREVO_API_URL}/contacts/{email}",
        method="DELETE",
        headers={"api-key": "not-a-real-api-key"},
        status_code=200,
    )

    delete_brevo_user(email)


def test_delete_brevo_user_request_error(monkeypatch):
    """Test to delete user's data from Brevo with a request error."""

    def mock_httpx_delete(*args, **kwars):
        raise httpx.RequestError("An error occurred")

    monkeypatch.setattr("mork.celery.tasks.brevo.httpx.delete", mock_httpx_delete)

    with pytest.raises(
        UserDeleteError, match="Network error while deleting user contact on Brevo"
    ):
        delete_brevo_user("johndoe@example.com")


def test_delete_brevo_user_not_found(monkeypatch, caplog):
    """Test to delete user's data from Brevo when no contact found."""

    def mock_httpx_delete(*args, **kwars):
        raise httpx.HTTPStatusError(
            "An error occured",
            request=None,
            response=httpx.Response(status_code=httpx.codes.NOT_FOUND),
        )

    monkeypatch.setattr("mork.celery.tasks.brevo.httpx.delete", mock_httpx_delete)

    # Make sure no error is raised if contact not found on Brevo
    with caplog.at_level(logging.INFO):
        delete_brevo_user("johndoe@example.com")

    assert (
        "mork.celery.tasks.brevo",
        logging.INFO,
        "User has no contact on Brevo",
    ) in caplog.record_tuples


def test_delete_brevo_user_status_error(monkeypatch):
    """Test to delete user's data from Brevo with API returning a 4** or 5**."""

    def mock_httpx_delete(*args, **kwars):
        raise httpx.HTTPStatusError(
            "An error occured",
            request=None,
            response=httpx.Response(status_code=httpx.codes.METHOD_NOT_ALLOWED),
        )

    monkeypatch.setattr("mork.celery.tasks.brevo.httpx.delete", mock_httpx_delete)

    with pytest.raises(UserDeleteError, match="Failed to delete user contact on Brevo"):
        delete_brevo_user("johndoe@example.com")
