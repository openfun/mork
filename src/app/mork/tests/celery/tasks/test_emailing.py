"""Tests for Mork Celery emailing tasks."""

from unittest.mock import Mock, call

import pytest
from faker import Faker

from mork.celery.tasks.emailing import (
    check_email_already_sent,
    mark_email_status,
    warn_inactive_users,
    warn_user,
)
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.exceptions import EmailAlreadySent, EmailSendError
from mork.factories.tasks import EmailStatusFactory


def test_warn_inactive_users(edx_mysql_db, monkeypatch):
    """Test the `warn_inactive_users` function."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe1",
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe2",
        email="johndoe2@example.com",
    )
    # 2 users that logged in recently
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(start_date="-3y"),
        username="JaneDah1",
        email="janedah1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(start_date="-3y"),
        username="JaneDah2",
        email="janedah2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.emailing.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.group", mock_group)
    mock_warn_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.warn_user", mock_warn_user)

    warn_inactive_users(dry_run=False)

    mock_group.assert_called_once_with(
        [
            mock_warn_user.s(
                email="johndoe1@example.com", username="JohnDoe1", dry_run=False
            ),
            mock_warn_user.s(
                email="johndoe2@example.com", username="JohnDoe2", dry_run=False
            ),
        ]
    )


def test_warn_inactive_users_with_limit(edx_mysql_db, monkeypatch):
    """Test the `warn_inactive_users` function with limit."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe1",
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe2",
        email="johndoe2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.emailing.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.group", mock_group)
    mock_warn_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.warn_user", mock_warn_user)

    warn_inactive_users(limit=1, dry_run=False)

    mock_group.assert_called_once_with(
        [
            mock_warn_user.s(
                email="johndoe1@example.com", username="JohnDoe1", dry_run=False
            )
        ]
    )


def test_warn_inactive_users_with_batch_size(edx_mysql_db, monkeypatch):
    """Test the `warn_inactive_users` function with batch size."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe1",
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe2",
        email="johndoe2@example.com",
    )

    monkeypatch.setattr(
        "mork.celery.tasks.emailing.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.group", mock_group)
    mock_warn_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.warn_user", mock_warn_user)

    # Set batch size to 1
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.settings.EDX_MYSQL_QUERY_BATCH_SIZE", 1
    )

    warn_inactive_users(dry_run=False)

    mock_group.assert_has_calls(
        [
            call(
                [
                    mock_warn_user.s(
                        email="johndoe1@example.com", username="JohnDoe1", dry_run=False
                    ),
                ]
            ),
            call().delay(),
            call(
                [
                    mock_warn_user.s(
                        email="johndoe2@example.com", username="JohnDoe2", dry_run=False
                    ),
                ]
            ),
            call().delay(),
        ]
    )


def test_warn_inactive_users_with_dry_run(edx_mysql_db, monkeypatch):
    """Test the `warn_inactive_users` function with dry run activated (by default)."""
    # 2 users that did not log in for 3 years
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe1",
        email="johndoe1@example.com",
    )
    EdxAuthUserFactory.create(
        last_login=Faker().date_time_between(end_date="-3y"),
        username="JohnDoe2",
        email="johndoe2@example.com",
    )
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.OpenEdxMySQLDB", lambda *args: edx_mysql_db
    )

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.group", mock_group)
    mock_warn_user = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.warn_user", mock_warn_user)

    warn_inactive_users()

    mock_group.assert_called_once_with(
        [
            mock_warn_user.s(
                email="johndoe1@example.com", username="JohnDoe1", dry_run=True
            ),
            mock_warn_user.s(
                email="johndoe2@example.com", username="JohnDoe2", dry_run=True
            ),
        ]
    )


def test_warn_user(monkeypatch):
    """Test the `warn_user` function."""
    mock_check_email = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.check_email_already_sent", mock_check_email
    )
    mock_send_email = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.send_email", mock_send_email)
    mock_mark_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.mark_email_status", mock_mark_email_status
    )

    email = "johndoe@example.com"
    username = "JohnDoe"
    warn_user(email, username, dry_run=False)

    mock_check_email.assert_called_once_with(email)
    mock_send_email.assert_called_once_with(email, username)
    mock_mark_email_status.assert_called_once_with(email)


def test_warn_user_with_dry_run(monkeypatch):
    """Test the `warn_user` function with dry run activated (by default)."""
    mock_check_email = Mock(return_value=False)
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.check_email_already_sent", mock_check_email
    )
    mock_send_email = Mock()
    monkeypatch.setattr("mork.celery.tasks.emailing.send_email", mock_send_email)
    mock_mark_email_status = Mock()
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.mark_email_status", mock_mark_email_status
    )

    email = "johndoe@example.com"
    username = "JohnDoe"
    warn_user(email, username)

    mock_check_email.assert_called_once_with(email)
    mock_send_email.assert_not_called()
    mock_mark_email_status.assert_not_called()


def test_warn_user_already_sent(monkeypatch):
    """Test the `warn_user` function when email has already been sent."""
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.check_email_already_sent", lambda x: True
    )

    with pytest.raises(
        EmailAlreadySent, match="An email has already been sent to this user"
    ):
        warn_user("johndoe@example.com", "JohnDoe")


def test_warn_user_sending_failure(monkeypatch):
    """Test the `warn_user` function with email sending failure."""
    monkeypatch.setattr(
        "mork.celery.tasks.emailing.check_email_already_sent", lambda x: False
    )

    def mock_send(*args):
        raise EmailSendError("An error occurred")

    monkeypatch.setattr("mork.celery.tasks.emailing.send_email", mock_send)

    with pytest.raises(EmailSendError, match="An error occurred"):
        warn_user("johndoe@example.com", "JohnDoe", dry_run=False)


def test_check_email_already_sent(monkeypatch, db_session):
    """Test the `check_email_already_sent` function."""
    email_address = "test_email@example.com"

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.emailing.MorkDB", MockMorkDB)
    EmailStatusFactory.create_batch(3)

    assert not check_email_already_sent(email_address)

    EmailStatusFactory.create(email=email_address)
    assert check_email_already_sent(email_address)


def test_mark_email_status(monkeypatch, db_session):
    """Test the `mark_email_status` function."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.emailing.MorkDB", MockMorkDB)

    # Write new email status entry
    new_email = "test_email@example.com"
    mark_email_status(new_email)
    assert check_email_already_sent(new_email)
