"""Tests for Mork Celery edx tasks."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.tasks.edx import delete_edx_mysql_user, delete_edx_platform_user
from mork.edx.mysql import crud
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.exceptions import (
    UserDeleteError,
    UserNotFound,
    UserProtected,
    UserStatusError,
)
from mork.factories.users import UserFactory, UserServiceStatusFactory
from mork.models.users import DeletionStatus, ServiceName, User
from mork.schemas.users import UserRead


def test_delete_edx_platform_user(db_session, monkeypatch):
    """Test to delete user from edX platform."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_called_once_with(email=user.email)
    mock_delete_edx_mongo_user.assert_called_once_with(username=user.username)
    mock_update_status_in_mork.assert_called_once_with(
        user_id=user.id, service=ServiceName.EDX, status=DeletionStatus.DELETED
    )


def test_delete_edx_platform_user_invalid_user(monkeypatch):
    """Test to delete user from edX platform with an invalid user."""

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: None)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    nonexistent_id = uuid4().hex
    with pytest.raises(
        UserNotFound, match=f"User {nonexistent_id} could not be retrieved from Mork"
    ):
        delete_edx_platform_user(nonexistent_id)

    mock_delete_edx_mysql_user.assert_not_called()
    mock_delete_edx_mongo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_edx_platform_user_invalid_status(db_session, monkeypatch):
    """Test to delete user from edX platform with an invalid status."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on edx
    UserFactory.create(
        service_statuses={ServiceName.EDX: DeletionStatus.DELETED},
    )

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=True)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"User {str(user.id)} is not to be deleted. Status: DeletionStatus.DELETED",  # noqa: E501
    ):
        delete_edx_platform_user(user.id)

    mock_delete_edx_mysql_user.assert_not_called()
    mock_delete_edx_mongo_user.assert_not_called()
    mock_update_status_in_mork.assert_not_called()


def test_delete_edx_platform_user_failed_delete(db_session, monkeypatch):
    """Test to delete user from edX platform with a failed delete."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on edx
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    def mock_delete_edx_mysql_user(*args, **kwars):
        raise UserDeleteError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_edx_platform_user(user.id)


def test_delete_edx_platform_user_failed_status_update(db_session, monkeypatch):
    """Test to delete user from edX platform with a failed status update."""
    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database that is already deleted on edx
    UserFactory.create()

    # Get user from db
    user = UserRead.model_validate(db_session.scalar(select(User)))

    monkeypatch.setattr("mork.celery.tasks.edx.get_user_from_mork", lambda x: user)

    mock_delete_edx_mysql_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mysql_user", mock_delete_edx_mysql_user
    )
    mock_delete_edx_mongo_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.edx.delete_edx_mongo_user", mock_delete_edx_mongo_user
    )
    mock_update_status_in_mork = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.edx.update_status_in_mork", mock_update_status_in_mork
    )

    with pytest.raises(
        UserStatusError,
        match=f"Failed to update deletion status to deleted for user {user.id}",
    ):
        delete_edx_platform_user(user.id)


def test_delete_edx_mysql_user(edx_mysql_db, monkeypatch):
    """Test to delete user's data from MySQL."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    EdxAuthUserFactory.create(email="johndoe1@example.com")
    EdxAuthUserFactory.create(email="johndoe2@example.com")

    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    # Check both users exist on the MySQL database
    assert crud.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )
    assert crud.get_user(
        edx_mysql_db.session,
        email="johndoe2@example.com",
    )

    delete_edx_mysql_user(email="johndoe1@example.com")

    # Check only one remains
    assert not crud.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )
    assert crud.get_user(
        edx_mysql_db.session,
        email="johndoe2@example.com",
    )


def test_delete_edx_mysql_user_protected(edx_mysql_db, monkeypatch):
    """Test to delete data from MySQL for a protected user."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    email = "johndoe1@example.com"
    EdxAuthUserFactory.create(email=email)

    def mock_delete_user(*args, **kwargs):
        raise UserProtected("An error occurred")

    monkeypatch.setattr("mork.celery.tasks.edx.mysql.delete_user", mock_delete_user)

    delete_edx_mysql_user(email=email)

    # Check the user still exists on the edX MySQL database
    assert crud.get_user(
        edx_mysql_db.session,
        email="johndoe1@example.com",
    )


def test_delete_edx_mysql_user_with_failure(edx_mysql_db, monkeypatch):
    """Test to delete user's data from MySQL with a commit failure."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    email = "johndoe1@example.com"
    EdxAuthUserFactory.create(email=email)

    def mock_session_commit():
        raise SQLAlchemyError("An error occurred")

    edx_mysql_db.session.commit = mock_session_commit
    monkeypatch.setattr(
        "mork.celery.tasks.edx.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    with pytest.raises(
        UserDeleteError,
        match=f"Failed to delete user with email='{email}' from edX MySQL",
    ):
        delete_edx_mysql_user(email=email)
