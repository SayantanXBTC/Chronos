"""Tests for PlaceNamesService and GET /api/v1/place-names."""
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Service unit tests
# ---------------------------------------------------------------------------

async def test_place_names_returns_feature_collection():
    from app.services.place_names_service import PlaceNamesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = PlaceNamesService(db=mock_db)
    result = await svc.get_place_names(year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4)

    assert result["type"] == "FeatureCollection"
    assert isinstance(result["features"], list)


async def test_place_names_feature_shape():
    from app.services.place_names_service import PlaceNamesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "name": "Rome",
            "name_modern": "Rome",
            "name_local": None,
            "type": "city",
            "importance": 10,
            "label_priority": 10,
            "date_precision": "approximate",
            "geometry": {"type": "Point", "coordinates": [12.5, 41.9]},
        }
    ]
    mock_db.execute.return_value = mock_result

    svc = PlaceNamesService(db=mock_db)
    result = await svc.get_place_names(year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4)

    assert len(result["features"]) == 1
    feat = result["features"][0]
    assert feat["type"] == "Feature"
    assert feat["geometry"]["type"] == "Point"
    assert feat["properties"]["name"] == "Rome"
    assert feat["properties"]["importance"] == 10
    assert feat["properties"]["label_priority"] == 10


async def test_place_names_passes_year_to_query():
    from app.services.place_names_service import PlaceNamesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = PlaceNamesService(db=mock_db)
    await svc.get_place_names(year=-500, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4)

    assert mock_db.execute.called
    params = mock_db.execute.call_args[0][1]
    assert params["year"] == -500


async def test_place_names_passes_zoom_to_query():
    from app.services.place_names_service import PlaceNamesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = PlaceNamesService(db=mock_db)
    await svc.get_place_names(year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=6)

    params = mock_db.execute.call_args[0][1]
    assert params["zoom"] == 6


# ---------------------------------------------------------------------------
# Router tests (via HTTP client)
# ---------------------------------------------------------------------------

async def test_place_names_endpoint_requires_year(client):
    response = await client.get("/api/v1/place-names")
    assert response.status_code == 422


async def test_place_names_endpoint_rejects_year_zero(client):
    response = await client.get("/api/v1/place-names?year=0")
    assert response.status_code == 422


async def test_place_names_endpoint_valid_year(client):
    response = await client.get("/api/v1/place-names?year=-264")
    # 200 or 500 (no real DB) — must not be 422
    assert response.status_code != 422


async def test_place_names_endpoint_bbox_defaults(client):
    """Endpoint accepts year-only request (bbox has defaults)."""
    response = await client.get("/api/v1/place-names?year=100")
    assert response.status_code != 422


async def test_place_names_endpoint_rejects_bad_bbox(client):
    """min_x out of [-180,180] range → 422."""
    response = await client.get("/api/v1/place-names?year=100&min_x=-999")
    assert response.status_code == 422
