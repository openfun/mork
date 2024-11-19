"""Mork Celery emailing tasks."""

from datetime import datetime
from logging import getLogger

from celery import group
from sqlalchemy import select

from mork.celery.celery_app import app
from mork.conf import settings
from mork.db import MorkDB
from mork.edx.mysql import crud
from mork.edx.mysql.database import OpenEdxMySQLDB
from mork.exceptions import EmailAlreadySent, EmailSendError
from mork.mail import send_email
from mork.models.tasks import EmailStatus

logger = getLogger(__name__)


@app.task
def warn_inactive_users(limit: int = 0, dry_run: bool = True):
    """Celery task to warn inactive users by email."""
    db = OpenEdxMySQLDB()

    threshold_date = datetime.now() - settings.WARNING_PERIOD
    total = crud.get_inactive_users_count(db.session, threshold_date)

    if limit:
        total = min(total, limit)

    for batch_offset in range(0, total, settings.EDX_MYSQL_QUERY_BATCH_SIZE):
        batch_limit = min(settings.EDX_MYSQL_QUERY_BATCH_SIZE, total - batch_offset)
        inactive_users = crud.get_inactive_users(
            db.session,
            threshold_date,
            offset=batch_offset,
            limit=batch_limit,
        )
        send_email_group = group(
            [
                warn_user.s(email=user.email, username=user.username, dry_run=dry_run)
                for user in inactive_users
            ]
        )
        send_email_group.delay()


@app.task(
    bind=True,
    rate_limit=settings.EMAIL_RATE_LIMIT,
    retry_kwargs={"max_retries": settings.EMAIL_MAX_RETRIES},
)
def warn_user(self, email: str, username: str, dry_run: bool = True):
    """Celery task that warns the specified user by sending an email."""
    # Check that user has not already received a warning email
    if check_email_already_sent(email):
        raise EmailAlreadySent("An email has already been sent to this user")

    if dry_run:
        logger.info(f"Dry run: An email would have been sent to user with {email=} ")
        return

    logger.info(f"Sending an email to user with {email=}")
    try:
        send_email(email, username)
    except EmailSendError as exc:
        logger.exception(exc)
        raise self.retry(exc=exc) from exc

    # Write flag that email was correctly sent to this user
    mark_email_status(email)


def check_email_already_sent(email: str):
    """Check if an email has already been sent to the user."""
    db = MorkDB()
    query = select(EmailStatus.email).where(EmailStatus.email == email)
    result = db.session.execute(query).scalars().first()
    db.session.close()
    return result


def mark_email_status(email: str):
    """Mark the email status in database."""
    db = MorkDB()
    db.session.add(EmailStatus(email=email, sent_date=datetime.now()))
    db.session.commit()
    db.session.close()
