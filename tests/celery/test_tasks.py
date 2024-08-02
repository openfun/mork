"""Tests for Mork Celery tasks."""

import smtplib
from unittest.mock import MagicMock

import pytest

from mork.celery.tasks import check_email_already_sent, mark_email_status, send_email
from mork.exceptions import EmailSendError
from mork.factories import EmailStatusFactory


def test_check_email_already_sent(monkeypatch, db_session):
    """Test the `check_email_already_sent` function."""
    email_address = "test_email@example.com"

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.MorkDB", MockMorkDB)
    EmailStatusFactory.create_batch(3)

    assert not check_email_already_sent(email_address)

    EmailStatusFactory.create(email=email_address)
    assert check_email_already_sent(email_address)


def test_send_email(monkeypatch):
    """Test the `send_email` function."""

    mock_SMTP = MagicMock()
    monkeypatch.setattr("mork.celery.tasks.smtplib.SMTP", mock_SMTP)

    test_address = "john.doe@example.com"
    test_username = "JohnDoe"
    send_email(email_address=test_address, username=test_username)

    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1


def test_send_email_with_smtp_exception(monkeypatch):
    """Test the `send_email` function with an SMTP exception."""

    mock_SMTP = MagicMock()
    mock_SMTP.return_value.__enter__.return_value.sendmail.side_effect = (
        smtplib.SMTPException
    )

    monkeypatch.setattr("mork.celery.tasks.smtplib.SMTP", mock_SMTP)

    test_address = "john.doe@example.com"
    test_username = "JohnDoe"

    with pytest.raises(EmailSendError, match="Failed sending an email"):
        send_email(email_address=test_address, username=test_username)


def test_mark_email_status(monkeypatch, db_session):
    """Test the `mark_email_status` function."""

    class MockMorkDB:
        session = db_session

    EmailStatusFactory._meta.sqlalchemy_session = db_session
    monkeypatch.setattr("mork.celery.tasks.MorkDB", MockMorkDB)

    # Write new email status entry
    new_email = "test_email@example.com"
    mark_email_status(new_email)
    assert check_email_already_sent(new_email)
