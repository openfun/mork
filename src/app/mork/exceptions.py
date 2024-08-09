"""Exceptions for Mork."""


class EmailAlreadySent(Exception):
    """Raised when an email has already been sent to this user."""


class EmailSendError(Exception):
    """Raised when an error occurs when sending an email."""
