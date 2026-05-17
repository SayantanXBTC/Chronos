from unittest.mock import MagicMock, call

from data.loader import Loader


def _make_loader():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return Loader(mock_conn), mock_cursor


def test_upsert_entity_returns_uuid():
    loader, cursor = _make_loader()
    cursor.fetchone.return_value = ("aaaaaaaa-0000-0000-0000-000000000001",)
    result = loader.upsert_entity("roman-republic", "polity", "#c0392b")
    assert result == "aaaaaaaa-0000-0000-0000-000000000001"
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO entities" in sql
    assert "ON CONFLICT (slug)" in sql
    assert "RETURNING id::text" in sql


def test_delete_territories_returns_count():
    loader, cursor = _make_loader()
    cursor.rowcount = 5
    result = loader.delete_territories("some-entity-uuid")
    assert result == 5
    sql = cursor.execute.call_args[0][0]
    assert "DELETE FROM territories" in sql
    assert "entity_id" in sql


def test_insert_territory_uses_st_geomfromtext_with_srid():
    loader, cursor = _make_loader()
    loader.insert_territory(
        "entity-uuid",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        -500,
        -264,
        "approximate",
    )
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO territories" in sql
    assert "ST_GeomFromText" in sql
    assert "4326" in sql


def test_upsert_entity_name_deletes_then_inserts():
    loader, cursor = _make_loader()
    loader.upsert_entity_name("entity-uuid", "Roman Republic", -753, -27)
    calls = [c[0][0] for c in cursor.execute.call_args_list]
    assert any("DELETE FROM entity_names" in s for s in calls)
    assert any("INSERT INTO entity_names" in s for s in calls)
