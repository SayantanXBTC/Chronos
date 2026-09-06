"""Tests for SourcesService and GET /api/v1/sources."""
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Service unit tests
# ---------------------------------------------------------------------------

async def test_sources_returns_list():
    from app.services.sources_service import SourcesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = SourcesService(db=mock_db)
    result = await svc.get_sources()

    assert isinstance(result, list)


async def test_sources_row_shape():
    from app.services.sources_service import SourcesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "id": "aaaaaaaa-0000-0000-0000-000000000001",
            "slug": "awmc",
            "name": "Ancient World Mapping Center",
            "url": "https://awmc.unc.edu/",
            "license": "CC BY 4.0",
            "description": "Mediterranean historical data",
            "year_min": -500,
            "year_max": 640,
            "coverage": "mediterranean",
        }
    ]
    mock_db.execute.return_value = mock_result

    svc = SourcesService(db=mock_db)
    result = await svc.get_sources()

    assert len(result) == 1
    source = result[0]
    assert source["slug"] == "awmc"
    assert source["name"] == "Ancient World Mapping Center"
    assert source["license"] == "CC BY 4.0"


async def test_sources_multiple_rows():
    from app.services.sources_service import SourcesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {"id": "aaa", "slug": "awmc", "name": "AWMC", "url": None,
         "license": "CC BY 4.0", "description": None, "year_min": -500, "year_max": 640, "coverage": None},
        {"id": "bbb", "slug": "cshapes", "name": "cShapes 2.0", "url": None,
         "license": "CC BY", "description": None, "year_min": 1886, "year_max": 2019, "coverage": "global"},
    ]
    mock_db.execute.return_value = mock_result

    svc = SourcesService(db=mock_db)
    result = await svc.get_sources()

    assert len(result) == 2
    slugs = {r["slug"] for r in result}
    assert "awmc" in slugs
    assert "cshapes" in slugs


async def test_sources_empty_db():
    from app.services.sources_service import SourcesService

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    svc = SourcesService(db=mock_db)
    result = await svc.get_sources()

    assert result == []


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------

async def test_sources_endpoint_exists(client):
    response = await client.get("/api/v1/sources")
    assert response.status_code != 404


async def test_sources_endpoint_no_params_required(client):
    response = await client.get("/api/v1/sources")
    assert response.status_code not in (404, 422)
