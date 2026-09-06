from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.asyncio


async def test_world_state_returns_feature_collection():
    """Empty DB → valid empty FeatureCollection structure."""
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = WorldStateService(db=mock_db)
    result = await svc.get_state(
        year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4, layer="political"
    )

    assert result["type"] == "FeatureCollection"
    assert result["year"] == -264
    assert isinstance(result["features"], list)
    assert len(result["features"]) == 0


async def test_world_state_year_in_query_params():
    """Year -500 is passed to DB query."""
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = WorldStateService(db=mock_db)
    await svc.get_state(year=-500, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4, layer="political")

    assert mock_db.execute.called
    call_args = mock_db.execute.call_args
    params = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("params", {})
    assert params.get("year") == -500


async def test_world_state_snapshot_year_in_response():
    """Response includes snapshot_year field."""
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = WorldStateService(db=mock_db)
    result = await svc.get_state(
        year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4, layer="political"
    )

    assert "snapshot_year" in result
    assert isinstance(result["snapshot_year"], int)


async def test_world_state_feature_shape():
    """Row from DB is mapped to correct GeoJSON Feature structure."""
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "entity_id": "123e4567-e89b-12d3-a456-426614174000",
            "slug": "roman-empire",
            "type": "empire",
            "color": "#C0392B",
            "name": "Roman Republic",
            "confidence_type": "approximate",
            "source_name": "Ancient World Mapping Center",
            "importance": 7,
            "year_start": -509,
            "year_end": -27,
            "geometry": {"type": "MultiPolygon", "coordinates": []},
        }
    ]
    mock_db.execute.return_value = mock_result

    svc = WorldStateService(db=mock_db)
    result = await svc.get_state(
        year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4, layer="political"
    )

    assert len(result["features"]) == 1
    feature = result["features"][0]
    assert feature["type"] == "Feature"
    assert feature["id"] == "roman-empire"
    assert feature["geometry"] == {"type": "MultiPolygon", "coordinates": []}
    assert feature["properties"]["name"] == "Roman Republic"
    assert feature["properties"]["color"] == "#C0392B"
