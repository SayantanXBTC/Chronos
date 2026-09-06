import pytest

pytestmark = pytest.mark.asyncio


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_world_state_requires_year(client):
    """year is now a required query param — missing it returns 422."""
    response = await client.get("/api/v1/world/state")
    assert response.status_code == 422


async def test_world_state_rejects_year_zero(client):
    """Year 0 is invalid in historical convention."""
    response = await client.get("/api/v1/world/state?year=0")
    assert response.status_code == 422


async def test_snapshots_stub(client):
    response = await client.get("/api/v1/world/snapshots")
    assert response.status_code == 200
    assert "snapshots" in response.json()


async def test_events_stub(client):
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200



async def test_database_module_imports():
    """Verify database module loads without error (no connection needed)."""
    from app.database import Base, engine
    assert Base is not None
    assert engine is not None
