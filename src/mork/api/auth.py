"""Main module for Mork API authentication."""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from mork.conf import settings

api_key_header = APIKeyHeader(name="X-API-Key")


def get_user(api_key_header: str = Security(api_key_header)):
    """Authenticate user with any allowed method, using credentials in the header."""
    if api_key_header not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )