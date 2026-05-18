"""Tests for RiversService and GET /api/v1/rivers."""
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Service unit tests
# ---------------------------------------------------------------------------

async def test_rivers_returns_feature_collection():
    from app.services.rivers_service import RiversService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = RiversService(db=mock_db)
    result = await svc.get_rivers()

    assert result["type"] == "FeatureCollection"
    assert isinstance(result["features"], list)


async def test_rivers_feature_shape():
    from app.services.rivers_service import RiversService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "name": "Nile",
            "name_alt": "Neilos",
            "importance": 10,
            "geometry": {
                "type": "LineString",
                "coordinates": [[32.9, 22.0], [31.2, 30.1]],
            },
        }
    ]
    mock_db.execute.return_value = mock_result

    svc = RiversService(db=mock_db)
    result = await svc.get_rivers()

    assert len(result["features"]) == 1
    feat = result["features"][0]
    assert feat["type"] == "Feature"
    assert feat["geometry"]["type"] == "LineString"
    assert feat["properties"]["name"] == "Nile"
    assert feat["properties"]["name_alt"] == "Neilos"
    assert feat["properties"]["importance"] == 10


async def test_rivers_null_name_alt():
    from app.services.rivers_service import RiversService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "name": "Tiber",
            "name_alt": None,
            "importance": 7,
            "geometry": {"type": "LineString", "coordinates": [[12.0, 41.0], [12.5, 41.5]]},
        }
    ]
    mock_db.execute.return_value = mock_result

    svc = RiversService(db=mock_db)
    result = await svc.get_rivers()

    assert result["features"][0]["properties"]["name_alt"] is None


async def test_rivers_multiple_features():
    from app.services.rivers_service import RiversService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {"name": "Nile", "name_alt": None, "importance": 10,
         "geometry": {"type": "LineString", "coordinates": [[32.0, 22.0], [31.0, 30.0]]}},
        {"name": "Tiber", "name_alt": None, "importance": 7,
         "geometry": {"type": "LineString", "coordinates": [[12.0, 42.0], [12.5, 41.5]]}},
    ]
    mock_db.execute.return_value = mock_result

    svc = RiversService(db=mock_db)
    result = await svc.get_rivers()

    assert len(result["features"]) == 2


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------

async def test_rivers_endpoint_no_params_required(client):
    """Rivers endpoint takes no required params."""
    response = await client.get("/api/v1/rivers")
    # 200 or 500 (no DB) — must not be 422 or 404
    assert response.status_code not in (404, 422)


async def test_rivers_endpoint_exists(client):
    response = await client.get("/api/v1/rivers")
    assert response.status_code != 404
