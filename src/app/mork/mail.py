"""Email related functions."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from smtplib import SMTPException

from jinja2 import Environment, FileSystemLoader

from mork.conf import settings
from mork.exceptions import EmailSendError
from mork.templatetags.extra_tags import SVGStaticTag

logger = getLogger(__name__)


def render_template(template: str, context) -> str:
    """Render a Jinja template into HTML."""
    template_env = Environment(
        loader=FileSystemLoader(
            [
                settings.ROOT_PATH / "templates/html",
                settings.ROOT_PATH / "templates/text",
            ]
        ),
        autoescape=True,
        extensions=[SVGStaticTag],
    )
    template = template_env.get_template(template)
    return template.render(**context)


def send_email(email_address: str, username: str):
    """Initialize connection to SMTP and send a warning email."""
    template_vars = {
        "title": "Votre compte va être supprimé dans 30 jours.",
        "email": email_address,
        "fullname": username,
        "site": {
            "name": settings.EMAIL_SITE_NAME,
            "url": settings.EMAIL_SITE_BASE_URL,
            "login_url": settings.EMAIL_SITE_LOGIN_URL,
        },
    }
    html = render_template(
        "warning_email.html",
        template_vars,
    )

    text = render_template(
        "warning_email.txt",
        template_vars,
    )

    # Create a multipart message (with MIME type multipart/alternative) and set headers
    message = MIMEMultipart("alternative")
    message["From"] = settings.EMAIL_FROM
    message["To"] = email_address
    message["Subject"] = "Votre compte va bientôt être supprimé"

    # Attach the HTML parts. According to RFC 2046, the last part of a multipart
    # message, in this case the HTML message, is best and preferred
    message.attach(MIMEText(text, "plain"))
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
