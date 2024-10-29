"""Tests for the health check endpoints."""

import pytest


@pytest.mark.anyio
async def test_api_health_lbheartbeat(http_client):
    """Test the load balancer heartbeat healthcheck."""
    response = await http_client.get("/__lbheartbeat__")
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.anyio
async def test_api_health_heartbeat(db_session, http_client, monkeypatch):
    """Test the heartbeat healthcheck."""
    monkeypatch.setattr("mork.db.get_session", db_session)

    response = await http_client.get("/__heartbeat__")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}

    monkeypatch.setattr("mork.api.health.is_db_alive", lambda x: False)

    response = await http_client.get("/__heartbeat__")
    assert response.status_code == 500
    assert response.json() == {"database": "error"}
