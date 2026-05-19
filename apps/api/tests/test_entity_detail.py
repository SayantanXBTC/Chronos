"""Tests for entity_service.py."""
import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.entity_service import EntityService


def _make_db(rows_by_call: list):
    """Build mock AsyncSession that returns successive result sets per execute call."""
    db = AsyncMock()
    results = []
    for rows in rows_by_call:
        mapping_rows = [dict(r) for r in rows]
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = mapping_rows
        mock_result.mappings.return_value.first.return_value = mapping_rows[0] if mapping_rows else None
        results.append(mock_result)
    db.execute = AsyncMock(side_effect=results)
    return db


class TestGetEntityDetail:
    def _entity_row(self):
        return {
            "entity_id": "uuid-aaa",
            "slug": "roman-empire",
            "type": "empire",
            "color": "#c0392b",
            "name": "Roman Empire",
            "year_start": -27,
            "year_end": 476,
            "source_name": "Manual trace",
            "confidence_type": "approximate",
            "importance": 9,
        }

    async def test_returns_none_for_unknown_slug(self):
        db = _make_db([[]])  # no rows
        svc = EntityService(db=db)
        result = await svc.get_entity_detail("nonexistent-slug")
        assert result is None

    async def test_returns_entity_fields(self):
        db = _make_db([[self._entity_row()], [], []])
        svc = EntityService(db=db)
        result = await svc.get_entity_detail("roman-empire")
        assert result is not None
        assert result["slug"] == "roman-empire"
        assert result["name"] == "Roman Empire"
        assert result["year_start"] == -27
        assert result["year_end"] == 476
        assert result["type"] == "empire"
        assert result["color"] == "#c0392b"

    async def test_returns_lineage_structure(self):
        predecessor = {
            "slug": "roman-republic",
            "name": "Roman Republic",
            "relationship_type": "evolved_into",
            "year": -27,
            "notes": "Augustus",
        }
        successor = {
            "slug": "western-roman-empire",
            "name": "Western Roman Empire",
            "relationship_type": "split_from",
            "year": 285,
            "notes": None,
        }
        db = _make_db([[self._entity_row()], [predecessor], [successor]])
        svc = EntityService(db=db)
        result = await svc.get_entity_detail("roman-empire")
        assert "lineage" in result
        assert len(result["lineage"]["predecessors"]) == 1
        assert result["lineage"]["predecessors"][0]["slug"] == "roman-republic"
        assert result["lineage"]["predecessors"][0]["relationship_type"] == "evolved_into"
        assert len(result["lineage"]["successors"]) == 1
        assert result["lineage"]["successors"][0]["slug"] == "western-roman-empire"

    async def test_empty_lineage_when_no_relations(self):
        db = _make_db([[self._entity_row()], [], []])
        svc = EntityService(db=db)
        result = await svc.get_entity_detail("roman-empire")
        assert result["lineage"]["predecessors"] == []
        assert result["lineage"]["successors"] == []

    async def test_lineage_entry_missing_notes_is_none(self):
        predecessor = {
            "slug": "roman-republic",
            "name": "Roman Republic",
            "relationship_type": "evolved_into",
            "year": -27,
            "notes": None,
        }
        db = _make_db([[self._entity_row()], [predecessor], []])
        svc = EntityService(db=db)
        result = await svc.get_entity_detail("roman-empire")
        assert result["lineage"]["predecessors"][0]["notes"] is None


class TestEntityDetailRouter:
    def test_404_for_unknown_slug(self):
        from fastapi.testclient import TestClient
        from unittest.mock import AsyncMock, patch
        from app.main import app

        with patch("app.routers.entities.EntityService") as MockSvc:
            instance = MockSvc.return_value
            instance.get_entity_detail = AsyncMock(return_value=None)
            client = TestClient(app)
            resp = client.get("/api/v1/entities/nonexistent")
        assert resp.status_code == 404

    def test_200_for_known_slug(self):
        from fastapi.testclient import TestClient
        from unittest.mock import AsyncMock, patch
        from app.main import app

        detail = {
            "slug": "roman-empire", "name": "Roman Empire", "type": "empire",
            "color": "#c0392b", "year_start": -27, "year_end": 476,
            "source_name": None, "confidence_type": "approximate", "importance": 9,
            "lineage": {"predecessors": [], "successors": []},
        }
        with patch("app.routers.entities.EntityService") as MockSvc:
            instance = MockSvc.return_value
            instance.get_entity_detail = AsyncMock(return_value=detail)
            client = TestClient(app)
            resp = client.get("/api/v1/entities/roman-empire")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "roman-empire"
        assert "lineage" in resp.json()


@pytest.mark.skipif(
    not os.environ.get("HISTORY_TEST_DB"),
    reason="requires live DB"
)
def test_roman_empire_detail_live():
    """Smoke test against live DB: roman-empire must have lineage predecessors."""
    import asyncio
    from app.database import async_session_factory
    from app.services.entity_service import EntityService

    async def run():
        async with async_session_factory() as db:
            svc = EntityService(db=db)
            return await svc.get_entity_detail("roman-empire")

    result = asyncio.get_event_loop().run_until_complete(run())
    assert result is not None
    assert result["name"] == "Roman Empire"
    assert len(result["lineage"]["predecessors"]) >= 1
