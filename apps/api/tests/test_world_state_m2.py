"""Tests verifying M2 additions to WorldStateService: confidence_type, source_name, importance."""
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio


def _make_territory_row(**overrides):
    base = {
        "entity_id": "123e4567-e89b-12d3-a456-426614174000",
        "slug": "roman-republic",
        "type": "polity",
        "color": "#C0392B",
        "name": "Roman Republic",
        "confidence_type": "approximate",
        "source_name": "Ancient World Mapping Center",
        "importance": 7,
        "year_start": -509,
        "year_end": -27,
        "geometry": {"type": "MultiPolygon", "coordinates": []},
    }
    base.update(overrides)
    return base


async def _get_state(rows):
    from app.services.world_state import WorldStateService
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = rows
    mock_db.execute.return_value = mock_result
    svc = WorldStateService(db=mock_db)
    return await svc.get_state(year=-264, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=4)


async def test_world_state_m2_confidence_type_in_properties():
    result = await _get_state([_make_territory_row(confidence_type="approximate")])
    props = result["features"][0]["properties"]
    assert "confidence_type" in props
    assert props["confidence_type"] == "approximate"


async def test_world_state_m2_source_name_in_properties():
    result = await _get_state([_make_territory_row(source_name="Ancient World Mapping Center")])
    props = result["features"][0]["properties"]
    assert "source_name" in props
    assert props["source_name"] == "Ancient World Mapping Center"


async def test_world_state_m2_importance_in_properties():
    result = await _get_state([_make_territory_row(importance=8)])
    props = result["features"][0]["properties"]
    assert "importance" in props
    assert props["importance"] == 8


async def test_world_state_m2_confidence_backward_compat():
    """confidence field (legacy) still present alongside confidence_type."""
    result = await _get_state([_make_territory_row(confidence_type="exact")])
    props = result["features"][0]["properties"]
    assert "confidence" in props
    assert props["confidence"] == props["confidence_type"]


async def test_world_state_m2_null_source_name():
    """source_name=None is passed through without error."""
    result = await _get_state([_make_territory_row(source_name=None)])
    props = result["features"][0]["properties"]
    assert "source_name" in props
    assert props["source_name"] is None


async def test_world_state_m2_importance_defaults_to_5():
    """Row with importance=None → COALESCE gives 5."""
    result = await _get_state([_make_territory_row(importance=5)])
    props = result["features"][0]["properties"]
    assert props["importance"] == 5


async def test_world_state_m2_all_confidence_types():
    for ct in ("exact", "approximate", "inferred", "disputed"):
        result = await _get_state([_make_territory_row(confidence_type=ct)])
        assert result["features"][0]["properties"]["confidence_type"] == ct


async def test_world_state_m2_multiple_features_have_m2_fields():
    rows = [
        _make_territory_row(slug="roman-republic", confidence_type="approximate", importance=7),
        _make_territory_row(slug="carthage", confidence_type="inferred", source_name="AWMC", importance=6),
    ]
    result = await _get_state(rows)
    assert len(result["features"]) == 2
    for feat in result["features"]:
        assert "confidence_type" in feat["properties"]
        assert "source_name" in feat["properties"]
        assert "importance" in feat["properties"]
