"""M3-J: Tests for M3 additions to WorldStateService — 3-tier LOD, snapshot range."""
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio


def _make_row(**overrides):
    base = {
        "entity_id": "aabbccdd-0000-0000-0000-000000000001",
        "slug": "han-dynasty",
        "type": "dynasty",
        "color": "#2980b9",
        "name": "Han Dynasty",
        "confidence_type": "approximate",
        "source_name": "CHGIS",
        "importance": 10,
        "geometry": {"type": "MultiPolygon", "coordinates": []},
        "year_start": -264,
        "year_end": None,
    }
    base.update(overrides)
    return base


async def _call_service(rows, year=-100, zoom=4, bbox=(-180.0, -90.0, 180.0, 90.0)):
    from app.services.world_state import WorldStateService
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = rows
    mock_db.execute.return_value = mock_result
    svc = WorldStateService(db=mock_db)
    return await svc.get_state(year=year, bbox=bbox, zoom=zoom)


# ---------------------------------------------------------------------------
# Snapshot years range
# ---------------------------------------------------------------------------

class TestSnapshotYears:
    def test_snapshot_years_includes_negative_1000(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert -1000 in SNAPSHOT_YEARS

    def test_snapshot_years_includes_2026(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert 2026 in SNAPSHOT_YEARS

    def test_snapshot_years_includes_classical_era_25_year_steps(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert -475 in SNAPSHOT_YEARS
        assert -450 in SNAPSHOT_YEARS
        assert 25 in SNAPSHOT_YEARS
        assert 50 in SNAPSHOT_YEARS

    def test_snapshot_years_sorted_ascending(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert SNAPSHOT_YEARS == sorted(SNAPSHOT_YEARS)

    def test_snapshot_years_no_duplicates(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert len(SNAPSHOT_YEARS) == len(set(SNAPSHOT_YEARS))

    def test_snapshot_years_skip_year_zero(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert 0 not in SNAPSHOT_YEARS

    def test_snapshot_years_minimum_80_entries(self):
        from app.services.world_state import SNAPSHOT_YEARS
        assert len(SNAPSHOT_YEARS) >= 80


# ---------------------------------------------------------------------------
# LOD tier selection via zoom parameter
# ---------------------------------------------------------------------------

class TestLodTierSelection:
    async def test_response_contains_geometry_field(self):
        result = await _call_service([_make_row()], zoom=4)
        assert "geometry" in result["features"][0]

    async def test_zoom_param_passed_to_db(self):
        from app.services.world_state import WorldStateService
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        svc = WorldStateService(db=mock_db)
        await svc.get_state(year=-100, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=7)

        call_args = mock_db.execute.call_args
        params = call_args[0][1]
        assert params["zoom"] == 7

    async def test_low_zoom_value_passed_to_db(self):
        from app.services.world_state import WorldStateService
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        svc = WorldStateService(db=mock_db)
        await svc.get_state(year=-100, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=2)

        params = mock_db.execute.call_args[0][1]
        assert params["zoom"] == 2

    async def test_high_zoom_value_passed_to_db(self):
        from app.services.world_state import WorldStateService
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        svc = WorldStateService(db=mock_db)
        await svc.get_state(year=-100, bbox=(-180.0, -90.0, 180.0, 90.0), zoom=12)

        params = mock_db.execute.call_args[0][1]
        assert params["zoom"] == 12


# ---------------------------------------------------------------------------
# Feature collection structure
# ---------------------------------------------------------------------------

class TestFeatureCollectionStructure:
    async def test_result_type_is_featurecollection(self):
        result = await _call_service([_make_row()])
        assert result["type"] == "FeatureCollection"

    async def test_year_in_response(self):
        result = await _call_service([_make_row()], year=-87)
        assert result["year"] == -87

    async def test_snapshot_year_in_response(self):
        result = await _call_service([_make_row()], year=-87)
        assert "snapshot_year" in result

    async def test_empty_db_returns_empty_features(self):
        result = await _call_service([])
        assert result["features"] == []

    async def test_feature_id_is_slug(self):
        result = await _call_service([_make_row(slug="tang-dynasty")])
        assert result["features"][0]["id"] == "tang-dynasty"

    async def test_multiple_features_returned(self):
        rows = [
            _make_row(slug="han-dynasty", entity_id="aabbccdd-0000-0000-0000-000000000001"),
            _make_row(slug="tang-dynasty", entity_id="aabbccdd-0000-0000-0000-000000000002"),
        ]
        result = await _call_service(rows)
        assert len(result["features"]) == 2

    async def test_bbox_params_passed_to_db(self):
        from app.services.world_state import WorldStateService
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        svc = WorldStateService(db=mock_db)
        await svc.get_state(year=-100, bbox=(10.0, 20.0, 50.0, 60.0), zoom=5)

        params = mock_db.execute.call_args[0][1]
        assert params["min_x"] == 10.0
        assert params["min_y"] == 20.0
        assert params["max_x"] == 50.0
        assert params["max_y"] == 60.0


# ---------------------------------------------------------------------------
# year_start / year_end in feature properties
# ---------------------------------------------------------------------------

class TestYearStartYearEnd:
    async def test_feature_has_year_start_and_year_end(self):
        """Territory year_start and year_end must be in feature properties."""
        row = _make_row(year_start=-27, year_end=476)
        result = await _call_service([row])
        props = result["features"][0]["properties"]
        assert props["year_start"] == -27
        assert props["year_end"] == 476
