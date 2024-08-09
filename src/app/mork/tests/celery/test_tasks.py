"""Tests for Mork Celery tasks."""

from mork.celery.tasks import check_email_already_sent, mark_email_status
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
