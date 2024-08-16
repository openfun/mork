"""Mork Celery emailing tasks."""

from datetime import datetime
from logging import getLogger

from celery import group
from sqlalchemy import select

from mork.celery.celery_app import app
from mork.conf import settings
from mork.database import MorkDB
from mork.edx.database import OpenEdxDB
from mork.edx.models.auth import AuthUser
from mork.exceptions import EmailAlreadySent, EmailSendError
from mork.mail import send_email
from mork.models import EmailStatus

logger = getLogger(__name__)


@app.task
def warn_inactive_users():
    """Celery task to warn inactive users by email."""
    db = OpenEdxDB()

    threshold_date = datetime.now() - settings.WARNING_PERIOD

    total = AuthUser.get_inactive_users_count(db.session, threshold_date)
    for batch_offset in range(0, total, settings.EDX_QUERY_BATCH_SIZE):
        inactive_users = AuthUser.get_inactive_users(
            db.session,
            threshold_date,
            offset=batch_offset,
            limit=settings.EDX_QUERY_BATCH_SIZE,
        )
        send_email_group = group(
            [send_email_task.s(user.email, user.username) for user in inactive_users]
        )
        send_email_group.delay()


@app.task(
    bind=True,
    rate_limit=settings.EMAIL_RATE_LIMIT,
    retry_kwargs={"max_retries": settings.EMAIL_MAX_RETRIES},
)
def send_email_task(self, email_address: str, username: str):
    """Celery task that sends an email to the specified user."""
    # Check that user has not already received a warning email
    if check_email_already_sent(email_address):
        raise EmailAlreadySent("An email has already been sent to this user")

    try:
        send_email(email_address, username)
    except EmailSendError as exc:
        logger.exception(exc)
        raise self.retry(exc=exc) from exc

    # Write flag that email was correctly sent to this user
    mark_email_status(email_address)


def check_email_already_sent(email_address: str):
    """Check if an email has already been sent to the user."""
    db = MorkDB()
    query = select(EmailStatus.email).where(EmailStatus.email == email_address)
    result = db.session.execute(query).scalars().first()
    db.session.close()
    return result


def mark_email_status(email_address: str):
    """Mark the email status in database."""
    db = MorkDB()
    db.session.add(EmailStatus(email=email_address, sent_date=datetime.now()))
    db.session.commit()
    db.session.close()
