"""Fixtures for the mork app."""

from typing import AsyncIterator

import pytest
from httpx import AsyncClient

from mork.api import app
from mork.conf import settings


@pytest.fixture
@pytest.mark.anyio
async def http_client() -> AsyncIterator[AsyncClient]:
    """Handle application lifespan while yielding asynchronous HTTP client."""
    async with AsyncClient(app=app, base_url=settings.SERVER_URL) as client:
        yield client
