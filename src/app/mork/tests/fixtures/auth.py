"""Fixtures for the authorization headers of Mork api."""

import pytest

from mork.conf import settings


@pytest.fixture
def auth_headers() -> dict:
    """Generate authentication headers with an API token.

    Returns:
        dict: A dictionary containing the 'X-API-Key' header with an API key.

    Example:
        To use this fixture in a test function, you can do the following::

            def test_authenticated_request(client):
                headers = auth_headers()
                response = client.get("/protected/resource", headers=headers)
                assert response.status_code == 200

    """
    return {"X-API-Key": f"{settings.API_KEYS[0]}"}
