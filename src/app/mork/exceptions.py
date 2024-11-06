"""Exceptions for Mork."""


class EmailAlreadySent(Exception):
    """Raised when an email has already been sent to this user."""


class EmailSendError(Exception):
    """Raised when an error occurs when sending an email."""


class UserDeleteError(Exception):
    """Raised when an error occurs when deleting a user."""


class UserNotFound(Exception):
    """Raised when a user has not been found."""


class UserStatusError(Exception):
    """Raised when an error occurs when checking a user status."""


class UserProtected(Exception):
    """Raised when a user is associated with an entry in a protected table."""
