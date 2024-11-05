"""Tests of the Mork models."""

from mork.factories.tasks import EmailStatusFactory


def test_models_user_safe_dict(db_session):
    """Test the `safe_dict` method for the EmailStatus model."""
    EmailStatusFactory._meta.sqlalchemy_session = db_session
    email_status = EmailStatusFactory()

    assert email_status.safe_dict() == {
        "id": email_status.id,
        "sent_date": email_status.sent_date,
        "created_at": email_status.created_at,
        "updated_at": email_status.updated_at,
    }
