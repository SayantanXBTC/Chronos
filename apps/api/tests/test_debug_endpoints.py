"""M3-J: Tests for admin/debug endpoints — /admin/stats, /admin/geometry-stats, /admin/coverage."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.cache import get_redis
from app.database import get_db
from app.main import app

pytestmark = pytest.mark.asyncio


def _make_db_with_one(**kwargs):
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [kwargs]
    mock_result.mappings.return_value.one.return_value = kwargs
    mock_db.execute.return_value = mock_result
    return mock_db


def _make_db_returning(rows):
    mock_db = AsyncMock()
    results = []
    for row_set in rows:
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = row_set
        if row_set:
            mock_result.mappings.return_value.one.return_value = row_set[0]
        results.append(mock_result)
    mock_db.execute.side_effect = results
    return mock_db


def _make_redis():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    return mock_redis


async def _client_with_db(mock_db) -> AsyncClient:
    mock_redis = _make_redis()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestAdminStatsEndpoint:
    async def test_stats_returns_200(self):
        stats_row = {"entities": 5, "territories": 12, "place_names": 100, "lineages": 3}
        regions_rows = [{"region_name": "Mediterranean"}, {"region_name": "East Asia"}]
        mock_db = _make_db_returning([[stats_row], regions_rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/stats")
        app.dependency_overrides.clear()
        assert resp.status_code == 200

    async def test_stats_has_entity_count(self):
        stats_row = {"entities": 7, "territories": 20, "place_names": 500, "lineages": 11}
        regions_rows = []
        mock_db = _make_db_returning([[stats_row], regions_rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/stats")
        app.dependency_overrides.clear()
        data = resp.json()
        assert data["entities"] == 7

    async def test_stats_has_regions_list(self):
        stats_row = {"entities": 3, "territories": 8, "place_names": 50, "lineages": 2}
        regions_rows = [{"region_name": "Africa"}, {"region_name": "Americas"}]
        mock_db = _make_db_returning([[stats_row], regions_rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/stats")
        app.dependency_overrides.clear()
        data = resp.json()
        assert "regions" in data
        assert isinstance(data["regions"], list)

    async def test_stats_has_lineages_count(self):
        stats_row = {"entities": 3, "territories": 8, "place_names": 50, "lineages": 9}
        mock_db = _make_db_returning([[stats_row], []])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/stats")
        app.dependency_overrides.clear()
        assert resp.json()["lineages"] == 9


class TestGeometryStatsEndpoint:
    async def test_geometry_stats_returns_200(self):
        geo_rows = [{
            "year_start": -206, "year_end": -87,
            "geom_vertices": 500, "geom_lo_vertices": 120,
            "area_km2": 3_500_000.0, "geom_valid": True,
        }]
        mock_db = _make_db_returning([geo_rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/geometry-stats?entity_slug=han-dynasty")
        app.dependency_overrides.clear()
        assert resp.status_code == 200

    async def test_geometry_stats_returns_entity_slug(self):
        mock_db = _make_db_returning([[]])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/geometry-stats?entity_slug=roman-empire")
        app.dependency_overrides.clear()
        assert resp.json()["entity_slug"] == "roman-empire"

    async def test_geometry_stats_territories_list(self):
        geo_rows = [{
            "year_start": -206, "year_end": -87,
            "geom_vertices": 500, "geom_lo_vertices": 120,
            "area_km2": 3_500_000.0, "geom_valid": True,
        }]
        mock_db = _make_db_returning([geo_rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/geometry-stats?entity_slug=han-dynasty")
        app.dependency_overrides.clear()
        data = resp.json()
        assert "territories" in data
        assert len(data["territories"]) == 1
        assert data["territories"][0]["year_start"] == -206

    async def test_geometry_stats_empty_entity(self):
        mock_db = _make_db_returning([[]])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/geometry-stats?entity_slug=nonexistent")
        app.dependency_overrides.clear()
        assert resp.json()["territories"] == []


class TestCoverageEndpoint:
    async def test_coverage_returns_200(self):
        rows = [{"region_name": "Mediterranean", "year_start": -800, "year_end": 1453,
                 "completeness": "complete", "entity_count": 10, "primary_source": "Barrington Atlas",
                 "notes": None}]
        mock_db = _make_db_returning([rows])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/coverage")
        app.dependency_overrides.clear()
        assert resp.status_code == 200

    async def test_coverage_has_regions_key(self):
        mock_db = _make_db_returning([[]])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/coverage")
        app.dependency_overrides.clear()
        assert "regions" in resp.json()

    async def test_coverage_empty_db_returns_empty_list(self):
        mock_db = _make_db_returning([[]])
        async with await _client_with_db(mock_db) as client:
            resp = await client.get("/api/v1/admin/coverage")
        app.dependency_overrides.clear()
        assert resp.json()["regions"] == []
