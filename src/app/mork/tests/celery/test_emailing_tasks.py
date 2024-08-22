"""Tests for Mork Celery tasks."""

from unittest.mock import Mock, call

import pytest
from faker import Faker

from mork.celery.emailing_tasks import (
    check_email_already_sent,
    mark_email_status,
    send_email_task,
    warn_inactive_users,
)
from mork.edx.factories.auth import EdxAuthUserFactory
from mork.exceptions import EmailAlreadySent, EmailSendError
from mork.factories import EmailStatusFactory


def test_warn_inactive_users(edx_db, monkeypatch):
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

    monkeypatch.setattr("mork.celery.emailing_tasks.OpenEdxDB", lambda *args: edx_db)

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.emailing_tasks.group", mock_group)
    mock_send_email_task = Mock()
    monkeypatch.setattr(
        "mork.celery.emailing_tasks.send_email_task", mock_send_email_task
    )

    warn_inactive_users()

    mock_group.assert_called_once_with(
        [
            mock_send_email_task.s(email="johndoe1@example.com", username="JohnDoe1"),
            mock_send_email_task.s(email="johndoe2@example.com", username="JohnDoe2"),
        ]
    )


def test_warn_inactive_users_with_batch_size(edx_db, monkeypatch):
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

    monkeypatch.setattr("mork.celery.emailing_tasks.OpenEdxDB", lambda *args: edx_db)

    mock_group = Mock()
    monkeypatch.setattr("mork.celery.emailing_tasks.group", mock_group)
    mock_send_email_task = Mock()
    monkeypatch.setattr(
        "mork.celery.emailing_tasks.send_email_task", mock_send_email_task
    )

    # Set batch size to 1
    monkeypatch.setattr("mork.celery.emailing_tasks.settings.EDX_QUERY_BATCH_SIZE", 1)

    warn_inactive_users()

    mock_group.assert_has_calls(
        [
            call(
                [
                    mock_send_email_task.s(
                        email="johndoe1@example.com", username="JohnDoe1"
                    ),
                ]
            ),
            call().delay(),
            call(
                [
                    mock_send_email_task.s(
                        email="johndoe2@example.com", username="JohnDoe2"
                    ),
                ]
            ),
            call().delay(),
        ]
    )


def test_send_email_task(monkeypatch):
    """Test the `send_email_task` function."""
    monkeypatch.setattr(
        "mork.celery.emailing_tasks.check_email_already_sent", lambda x: False
    )
    monkeypatch.setattr("mork.celery.emailing_tasks.send_email", lambda *args: None)
    monkeypatch.setattr("mork.celery.emailing_tasks.mark_email_status", lambda x: None)

    send_email_task("johndoe@example.com", "JohnDoe")


def test_send_email_task_already_sent(monkeypatch):
    """Test the `send_email_task` function when email has already been sent."""
    monkeypatch.setattr(
        "mork.celery.emailing_tasks.check_email_already_sent", lambda x: True
    )

    with pytest.raises(
        EmailAlreadySent, match="An email has already been sent to this user"
    ):
        send_email_task("johndoe@example.com", "JohnDoe")


def test_send_email_task_sending_failure(monkeypatch):
    """Test the `send_email_task` function with email sending failure."""
    monkeypatch.setattr(
        "mork.celery.emailing_tasks.check_email_already_sent", lambda x: False
    )

    def mock_send(*args):
        raise EmailSendError("An error occurred")

    monkeypatch.setattr("mork.celery.emailing_tasks.send_email", mock_send)

    with pytest.raises(EmailSendError, match="An error occurred"):
        send_email_task("johndoe@example.com", "JohnDoe")


def test_check_email_already_sent(monkeypatch, db_session):
    """Test the `check_email_already_sent` function."""
    email_address = "test_email@example.com"

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.emailing_tasks.MorkDB", MockMorkDB)
    EmailStatusFactory.create_batch(3)

    assert not check_email_already_sent(email_address)

    EmailStatusFactory.create(email=email_address)
    assert check_email_already_sent(email_address)


def test_mark_email_status(monkeypatch, db_session):
    """Test the `mark_email_status` function."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.emailing_tasks.MorkDB", MockMorkDB)

    # Write new email status entry
    new_email = "test_email@example.com"
    mark_email_status(new_email)
    assert check_email_already_sent(new_email)
