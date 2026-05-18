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
        geom_lo_wkt="MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        date_precision="approximate",
        end_event_type="conquest",
    )
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO territories" in sql
    assert "ST_GeomFromText" in sql
    assert "4326" in sql
    assert "geom_lo" in sql
    assert "date_precision" in sql
    assert "end_event_type" in sql


def test_insert_territory_passes_geom_lo():
    """geom_lo_wkt should appear in the SQL params (passed twice for CASE WHEN)."""
    loader, cursor = _make_loader()
    hi_wkt = "MULTIPOLYGON(((10 10, 11 10, 11 11, 10 11, 10 10)))"
    med_wkt = "MULTIPOLYGON(((20 20, 21 20, 21 21, 20 21, 20 20)))"
    lo_wkt = "MULTIPOLYGON(((30 30, 31 30, 31 31, 30 31, 30 30)))"
    loader.insert_territory(
        "entity-uuid",
        hi_wkt,
        med_wkt,
        -500,
        -264,
        geom_lo_wkt=lo_wkt,
    )
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "geom_lo" in sql
    assert "CASE WHEN" in sql
    # geom_lo_wkt passed twice: once for CASE WHEN check, once for ST_GeomFromText
    assert params.count(lo_wkt) == 2


def test_insert_territory_date_precision_default():
    """Calling insert_territory without date_precision should use 'approximate'."""
    loader, cursor = _make_loader()
    loader.insert_territory(
        "entity-uuid",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        -500,
        -264,
    )
    params = cursor.execute.call_args[0][1]
    # date_precision is the second-to-last param; end_event_type is last
    assert params[-2] == "approximate"
    assert params[-1] is None  # end_event_type default


def test_upsert_entity_name_deletes_then_inserts():
    loader, cursor = _make_loader()
    loader.upsert_entity_name("entity-uuid", "Roman Republic", -753, -27)
    calls = [c[0][0] for c in cursor.execute.call_args_list]
    assert any("DELETE FROM entity_names" in s for s in calls)
    assert any("INSERT INTO entity_names" in s for s in calls)
