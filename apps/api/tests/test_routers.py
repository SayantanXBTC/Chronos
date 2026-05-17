import pytest


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_world_state_stub(client):
    response = await client.get("/api/v1/world/state")
    assert response.status_code == 200


async def test_snapshots_stub(client):
    response = await client.get("/api/v1/world/snapshots")
    assert response.status_code == 200
    assert "snapshots" in response.json()


async def test_events_stub(client):
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200
