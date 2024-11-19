"""Tests for Mork Celery deletion tasks."""

import logging
from unittest.mock import Mock, call

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mork.celery.tasks.deletion import (
    delete_inactive_users,
    delete_user,
    mark_user_for_deletion,
    remove_email_status,
)
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.exceptions import UserDeleteError
from mork.factories.tasks import EmailStatusFactory
from mork.factories.users import UserFactory, UserServiceStatusFactory
from mork.models.tasks import EmailStatus
from mork.models.users import (
    DeletionReason,
    DeletionStatus,
    User,
)


def test_delete_inactive_users(edx_mysql_db, monkeypatch):
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

    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    delete_inactive_users(dry_run=False)

    mock_group.assert_called_once_with(
        [
            mock_delete_user.s(email="johndoe1@example.com", dry_run=False),
            mock_delete_user.s(email="johndoe2@example.com", dry_run=False),
        ]
    )


def test_delete_inactive_users_with_limit(edx_mysql_db, monkeypatch):
    """Test the `delete_inactive_users` function with limit."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    delete_inactive_users(limit=1, dry_run=False)

    mock_group.assert_called_once_with(
        [
            mock_delete_user.s(email="johndoe1@example.com", dry_run=False),
        ]
    )


def test_delete_inactive_users_with_batch_size(edx_mysql_db, monkeypatch):
    """Test the `warn_inactive_users` function with batch size."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    # Set batch size to 1
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.settings.EDX_MYSQL_QUERY_BATCH_SIZE", 1
    )

    delete_inactive_users(dry_run=False)

    mock_group.assert_has_calls(
        [
            call(
                [
                    mock_delete_user.s(email="johndoe1@example.com", dry_run=False),
                ]
            ),
            call().delay(),
            call(
                [
                    mock_delete_user.s(email="johndoe2@example.com", dry_run=False),
                ]
            ),
            call().delay(),
        ]
    )


def test_delete_inactive_users_with_dry_run(edx_mysql_db, monkeypatch):
    """Test the `delete_inactive_users` function with dry run activated (by default)."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        email="johndoe2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.group", mock_group)
    mock_delete_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.delete_user", mock_delete_user)

    delete_inactive_users()

    mock_group.assert_called_once_with(
        [
            mock_delete_user.s(email="johndoe1@example.com", dry_run=True),
            mock_delete_user.s(email="johndoe2@example.com", dry_run=True),
        ]
    )


def test_delete_user(monkeypatch):
    """Test the `delete_user` function."""

    mock_chain = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.chain", mock_chain)

    mock_mark_user_for_deletion = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.mark_user_for_deletion", mock_mark_user_for_deletion
    )
    mock_delete_edx_platform_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_edx_platform_user",
        mock_delete_edx_platform_user,
    )
    mock_remove_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.remove_email_status", mock_remove_email_status
    )
    email = "johndoe@example.com"
    reason = DeletionReason.USER_REQUESTED
    delete_user(email, reason, dry_run=False)

    mock_chain.assert_called_once_with(
        mock_remove_email_status.si(email=email),
        mock_mark_user_for_deletion.si(email=email, reason=reason),
        mock_delete_edx_platform_user.s(email=email),
    )
    mock_chain.assert_has_calls([call().delay()])


def test_delete_user_with_dry_run(monkeypatch):
    """Test the `delete_user` function with dry run activated (by default)."""
    mock_mark_user_for_deletion = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.mark_user_for_deletion", mock_mark_user_for_deletion
    )
    mock_delete_edx_platform_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_edx_platform_user",
        mock_delete_edx_platform_user,
    )
    mock_remove_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.remove_email_status", mock_remove_email_status
    )
    email = "johndoe@example.com"
    delete_user(email)

    mock_delete_edx_platform_user.assert_not_called()
    mock_remove_email_status.assert_not_called()

    mock_chain = Mock()
    monkeypatch.setattr("mork.celery.tasks.deletion.chain", mock_chain)

    mock_mark_user_for_deletion = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.mark_user_for_deletion", mock_mark_user_for_deletion
    )
    mock_delete_edx_platform_user = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.delete_edx_platform_user",
        mock_delete_edx_platform_user,
    )
    mock_remove_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.remove_email_status", mock_remove_email_status
    )
    email = "johndoe@example.com"
    reason = DeletionReason.USER_REQUESTED
    delete_user(email, reason)

    mock_chain.assert_not_called()
    mock_chain.delay.assert_not_called()


def test_mark_user_for_deletion(edx_mysql_db, db_session, caplog, monkeypatch):
    """Test the `mark_user_for_deletion` function."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    class MockMorkDB:
        session = db_session

    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    # As we are closing the session inside the function tested, the factory need to
    # commit the AuthUser created
    EdxAuthUserFactory._meta.sqlalchemy_session_persistence = "commit"
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )
    auth_user = EdxAuthUserFactory.create()

    # Mark this user for deletion
    mark_user_for_deletion(auth_user.email, DeletionReason.GDPR)

    # Verify user is created
    inserted_user = db_session.scalars(select(User)).first()
    assert inserted_user.username == auth_user.username
    assert inserted_user.edx_user_id == auth_user.id
    assert inserted_user.email == auth_user.email
    assert inserted_user.reason == DeletionReason.GDPR
    # Verify statuses were created for all users and services
    assert all(
        status.status == DeletionStatus.TO_DELETE
        for status in inserted_user.service_statuses
    )

    # Try to mark the user for deletion again
    with caplog.at_level(logging.INFO):
        mark_user_for_deletion(auth_user.email, DeletionReason.GDPR)

    assert (
        "mork.celery.tasks.deletion",
        logging.INFO,
        f"User with email='{inserted_user.email}' is already marked for deletion",
    ) in caplog.record_tuples

    # Reset factory persistence
    EdxAuthUserFactory._meta.sqlalchemy_session_persistence = None


def test_mark_user_for_deletion_nonexistent_user(
    edx_mysql_db, db_session, caplog, monkeypatch
):
    """Test the `mark_user_for_deletion` function with a nonexistent user."""

    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )
    email = "johndoe@example.com"
    # Try to mark this user for deletion
    with pytest.raises(
        UserDeleteError, match=f"User with {email=} not found in edx database"
    ):
        mark_user_for_deletion(email, DeletionReason.GDPR)


def test_mark_user_for_deletion_failure(edx_mysql_db, db_session, monkeypatch):
    """Test the `mark_user_for_deletion` function with a write failure."""

    def mock_session_commit():
        raise SQLAlchemyError("An error occurred")

    db_session.commit = mock_session_commit

    class MockMorkDB:
        session = db_session

    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    EdxAuthUserFactory._meta.sqlalchemy_session = edx_mysql_db.session
    monkeypatch.setattr(
        "mork.celery.tasks.deletion.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )
    auth_user = EdxAuthUserFactory.create()

    with pytest.raises(UserDeleteError, match="Failed to mark user to be deleted"):
        mark_user_for_deletion(auth_user.email, reason=DeletionReason.GDPR)


def test_remove_email_status(db_session, monkeypatch):
    """Test the `remove_email_status` function."""

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
    remove_email_status(email)

    # Check that the entry has been deleted for this email
    query = select(EmailStatus.email).where(EmailStatus.email == email)
    assert not db_session.execute(query).scalars().first()


def test_remove_email_status_no_entry(caplog, db_session, monkeypatch):
    """Test the `remove_email_status` function when entry does not exist."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.deletion.MorkDB", MockMorkDB)

    email = "johndoe1@example.com"

    # Delete non existent entry
    with caplog.at_level(logging.WARNING):
        remove_email_status(email)

    assert (
        "mork.celery.tasks.deletion",
        logging.WARNING,
        "Email status - No user found with email johndoe1@example.com for deletion",
    ) in caplog.record_tuples


def test_remove_email_status_with_failure(caplog, db_session, monkeypatch):
    """Test the `remove_email_status` with a commit failure."""

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
        remove_email_status(email)

    assert (
        "mork.celery.tasks.deletion",
        logging.ERROR,
        "Email status - Failed to delete user with email johndoe1@example.com",
    ) in caplog.record_tuples
