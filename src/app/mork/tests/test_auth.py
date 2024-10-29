"""Tests for authentication for the Mork API."""

import pytest
from fastapi import HTTPException, status

from mork.auth import authenticate_api_key
from mork.conf import settings


@pytest.mark.anyio
async def test_authenticate_api_key():
    """Test the authentication with a wrong API key."""
    settings.API_KEYS = ["valid_key_1", "valid_key_2"]

    # Test with a valid API key
    assert authenticate_api_key("valid_key_1") is None
    assert authenticate_api_key("valid_key_2") is None

    # Test with an invalid API key
    with pytest.raises(HTTPException) as exc_info:
        authenticate_api_key("invalid_key")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Missing or invalid API key"
