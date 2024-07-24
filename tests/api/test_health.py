"""Tests for the health check endpoints."""

import pytest


@pytest.mark.anyio
async def test_api_health_lbheartbeat(http_client):
    """Test the load balancer heartbeat healthcheck."""
    response = await http_client.get("/__lbheartbeat__")
    assert response.status_code == 200
    assert response.json() is None
