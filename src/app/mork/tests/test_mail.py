"""Tests for Mork mail functions."""

import smtplib
from unittest.mock import MagicMock

import pytest

from mork.exceptions import EmailSendError
from mork.mail import render_template, send_email


def test_render_template():
    """Test the `render_template` function."""
    template_vars = {
        "title": "Votre compte va être supprimé dans 30 jours.",
        "email": "test@example.com",
        "fullname": "John Doe",
        "site": {
            "name": "Example site",
            "url": "http://base_url.com",
            "login_url": "http://url.com/login",
        },
    }
    render_html = render_template("warning_email.html", template_vars)
    assert template_vars["title"] in render_html
    assert template_vars["email"] in render_html
    assert template_vars["fullname"] in render_html
    assert template_vars["site"]["name"] in render_html
    assert template_vars["site"]["url"] in render_html
    assert template_vars["site"]["login_url"] in render_html
    assert 'src="data:' in render_html

    render_text = render_template("warning_email.txt", template_vars)
    assert template_vars["title"] in render_text
    assert template_vars["email"] in render_text
    assert template_vars["fullname"] in render_text
    assert template_vars["site"]["name"] in render_text
    assert template_vars["site"]["url"] in render_text
    assert template_vars["site"]["login_url"] in render_text
    assert "data:" in render_text


def test_send_email(monkeypatch):
    """Test the `send_email` function."""

    mock_SMTP = MagicMock()
    monkeypatch.setattr("mork.mail.smtplib.SMTP", mock_SMTP)

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

    monkeypatch.setattr("mork.mail.smtplib.SMTP", mock_SMTP)

    test_address = "john.doe@example.com"
    test_username = "JohnDoe"

    with pytest.raises(EmailSendError, match="Failed sending an email"):
        send_email(email_address=test_address, username=test_username)
