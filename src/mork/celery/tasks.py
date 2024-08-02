"""Mork Celery tasks."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from smtplib import SMTPException

from sqlalchemy import select

from mork.celery.celery_app import app
from mork.conf import settings
from mork.database import MorkDB
from mork.exceptions import EmailAlreadySent, EmailSendError
from mork.models import EmailStatus

logger = getLogger(__name__)


@app.task
def warn_inactive_users():
    """Celery task to warn inactive users by email."""
    pass


@app.task
def delete_inactive_users():
    """Celery task to delete inactive users accounts."""
    pass


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


def check_email_already_sent(email_adress: str):
    """Check if an email has already been sent to the user."""
    db = MorkDB()
    query = select(EmailStatus.email).where(EmailStatus.email == email_adress)
    result = db.session.execute(query).scalars().first()
    db.session.close()
    return result


def send_email(email_address: str, username: str):
    """Initialize connection to SMTP and send a warning email."""
    html = f"""\
    <html>
    <body>
        <h1>Hello {username},</h1>
        Your account will be closed soon! If you want to keep it, please log in!
    </body>
    </html>
    """

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_FROM
    message["To"] = email_address
    message["Subject"] = "Your account will be closed soon"

    # Attach the HTML part
    message.attach(MIMEText(html, "html"))

    # Send the email
    with smtplib.SMTP(
        host=settings.EMAIL_HOST, port=settings.EMAIL_PORT
    ) as smtp_server:
        if settings.EMAIL_USE_TLS:
            smtp_server.starttls()
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            smtp_server.login(
                user=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
            )
        try:
            smtp_server.sendmail(
                from_addr=settings.EMAIL_FROM,
                to_addrs=email_address,
                msg=message.as_string(),
            )
        except SMTPException as exc:
            logger.error(f"Sending email failed: {exc} ")
            raise EmailSendError("Failed sending an email") from exc


def mark_email_status(email_address: str):
    """Mark the email status in database."""
    db = MorkDB()
    db.session.add(EmailStatus(email=email_address, sent_date=datetime.now()))
    db.session.commit()
    db.session.close()
