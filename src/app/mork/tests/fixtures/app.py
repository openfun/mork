"""Fixtures for the mork app."""

from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from mork.api import app
from mork.conf import settings

transport = ASGITransport(app=app)


@pytest.fixture
async def http_client() -> AsyncIterator[AsyncClient]:
    """Handle application lifespan while yielding asynchronous HTTP client."""
    async with AsyncClient(transport=transport, base_url=settings.SERVER_URL) as client:
        yield client
