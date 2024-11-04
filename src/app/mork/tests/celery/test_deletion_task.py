"""Tests for Mork Celery deletion tasks."""

import logging
from unittest.mock import Mock, call

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.tasks.deletion import (
    delete_email_status,
    delete_inactive_users,
    delete_user,
    delete_user_from_db,
)
from mork.edx import crud
from mork.edx.factories.auth import EdxAuthUserFactory
from mork.exceptions import UserDeleteError
from mork.factories import EmailStatusFactory
from mork.models import EmailStatus


def test_delete_inactive_users(edx_db, monkeypatch):
    """Test the `delete_inactive_users` function."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe2@example.com",
    )
    # 2 users that logged in recently
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(start_date="-3y"),
        email="janedah1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(start_date="-3y"),
        email="janedah2@example.com",
    )

    monkeypatch.setattr("mork.celery.tasks.deletion.OpenEdxDB", lambda *args: edx_db)

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    delete_inactive_users()

    mock_group.assert_called_once_with(
        [
            mock_delete_user.s(email="johndoe1@example.com"),
            mock_delete_user.s(email="johndoe2@example.com"),
        ]
    )


def test_delete_inactive_users_with_batch_size(edx_db, monkeypatch):
    """Test the `warn_inactive_users` function."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe2@example.com",
    )

    monkeypatch.setattr("mork.celery.tasks.deletion.OpenEdxDB", lambda *args: edx_db)

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    # Set batch size to 1
    monkeypatch.setattr("mork.celery.tasks.deletion.settings.EDX_QUERY_BATCH_SIZE", 1)

    delete_inactive_users()

    mock_group.assert_has_calls(
        [
            call(
                [
                    mock_delete_user.s(email="johndoe1@example.com"),
                ]
            ),
            call().delay(),
            call(
                [
                    mock_delete_user.s(email="johndoe2@example.com"),
                ]
            ),
            call().delay(),
        ]
    )


def test_delete_user(monkeypatch):
    """Test the `delete_user` function."""
    mock_delete_user_from_db = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_user_from_db", mock_delete_user_from_db
    )
    mock_delete_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_email_status", mock_delete_email_status
    )
    email = "johndoe@example.com"
    delete_user(email)

    mock_delete_user_from_db.assert_called_once_with(email)
    mock_delete_email_status.assert_called_once_with(email)


def test_delete_user_failure(monkeypatch):
    """Test the `delete_user` function with a delete failure."""

    def mock_delete_user_from_db(*args):
        raise UserDeleteError("An error occurred")

    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_user_from_db", mock_delete_user_from_db
    )

    with pytest.raises(UserDeleteError, match="An error occurred"):
        delete_user("johndoe@example.com")


def test_delete_user_from_db(edx_db, monkeypatch):
    """Test the `delete_user_from_db` function."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_db.session
    EdxAuthUserFactory.create(email="johndoe1@example.com")
    EdxAuthUserFactory.create(email="johndoe2@example.com")

    monkeypatch.setattr("mork.celery.tasks.deletion.OpenEdxDB", lambda *args: edx_db)

    assert crud.get_user(
        edx_db.session,
        email="johndoe1@example.com",
    )
    assert crud.get_user(
        edx_db.session,
        email="johndoe2@example.com",
    )

    delete_user_from_db(email="johndoe1@example.com")

    assert not crud.get_user(
        edx_db.session,
        email="johndoe1@example.com",
    )
    assert crud.get_user(
        edx_db.session,
        email="johndoe2@example.com",
    )


def test_delete_user_from_db_with_failure(edx_db, monkeypatch):
    """Test the `delete_user_from_db` function with a commit failure."""
    EdxAuthUserFactory._meta.sqlalchemy_session = edx_db.session
    EdxAuthUserFactory.create(email="johndoe1@example.com")

    def mock_session_commit():
        raise SQLAlchemyError("An error occurred")

    edx_db.session.commit = mock_session_commit
    monkeypatch.setattr("mork.celery.tasks.deletion.OpenEdxDB", lambda *args: edx_db)

    with pytest.raises(UserDeleteError, match="Failed to delete user."):
        delete_user_from_db(email="johndoe1@example.com")


def test_delete_email_status(db_session, monkeypatch):
    """Test the `delete_email_status` function."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    email = "johndoe1@example.com"
    EmailStatusFactory.create(email=email)

    # Check that an entry has been created for this email
    query = select(EmailStatus.email).where(EmailStatus.email == email)
    assert db_session.execute(query).scalars().first()

    # Delete entry
    delete_email_status(email)

    # Check that the entry has been deleted for this email
    query = select(EmailStatus.email).where(EmailStatus.email == email)
    assert not db_session.execute(query).scalars().first()


def test_delete_email_status_no_entry(caplog, db_session, monkeypatch):
    """Test the `delete_email_status` function when entry does not exist."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    email = "johndoe1@example.com"

    # Delete non existent entry
    with caplog.at_level(logging.WARNING):
        delete_email_status(email)

    assert (
        "mork.celery.tasks.deletion",
        logging.WARNING,
        "Email status - No user found with email='johndoe1@example.com' for deletion",
    ) in caplog.record_tuples


def test_delete_email_status_with_failure(caplog, db_session, monkeypatch):
    """Test the `delete_email_status` with a commit failure."""

    def mock_session_commit():
        raise SQLAlchemyError("An error occurred")

    db_session.commit = mock_session_commit

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    email = "johndoe1@example.com"
    EmailStatusFactory.create(email=email)

    # Try to delete entry
    with caplog.at_level(logging.ERROR):
        delete_email_status(email)

    assert (
        "mork.celery.tasks.deletion",
        logging.ERROR,
        "Email status - Failed to delete user with email='johndoe1@example.com':"
        " An error occurred",
    ) in caplog.record_tuples
