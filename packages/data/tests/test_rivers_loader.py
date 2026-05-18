"""Unit tests for rivers_loader.py — uses temp GeoJSON, mocked DB cursor."""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from shapely.geometry import LineString, MultiLineString

from data.rivers_loader import load_rivers, _to_linestring


def _make_conn():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


def _write_rivers_geojson(tmp_path: Path, features: list) -> Path:
    fc = {"type": "FeatureCollection", "features": features}
    p = tmp_path / "rivers.geojson"
    p.write_text(json.dumps(fc))
    return p


NILE_COORDS = [[32.9, 22.0], [32.5, 24.0], [32.0, 28.0], [31.2, 30.1], [30.0, 31.2]]
TIBER_COORDS = [[11.7, 42.5], [12.1, 41.9], [12.3, 41.7], [12.5, 41.5]]


# ---------------------------------------------------------------------------
# _to_linestring helper
# ---------------------------------------------------------------------------

def test_to_linestring_passthrough():
    line = LineString(NILE_COORDS)
    result = _to_linestring(line)
    assert isinstance(result, LineString)
    assert list(result.coords) == list(line.coords)


def test_to_linestring_from_multilinestring():
    multi = MultiLineString([NILE_COORDS[:3], NILE_COORDS[3:]])
    result = _to_linestring(multi)
    assert isinstance(result, LineString)
    # All coords preserved
    assert len(list(result.coords)) == len(NILE_COORDS)


def test_to_linestring_raises_on_wrong_type():
    from shapely.geometry import Point
    with pytest.raises(ValueError, match="Cannot convert"):
        _to_linestring(Point(0, 0))


# ---------------------------------------------------------------------------
# load_rivers — happy path
# ---------------------------------------------------------------------------

def test_load_rivers_returns_count(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": "Neilos", "importance": 10, "source_name": "Natural Earth"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
        {"type": "Feature",
         "properties": {"name": "Tiber", "name_alt": None, "importance": 7, "source_name": "AWMC"},
         "geometry": {"type": "LineString", "coordinates": TIBER_COORDS}},
    ])
    conn, _ = _make_conn()
    result = load_rivers(conn, geojson_path=geojson)
    assert result == 2


def test_load_rivers_deletes_before_insert(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": None, "importance": 10, "source_name": "Natural Earth"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
    ])
    conn, cursor = _make_conn()
    load_rivers(conn, geojson_path=geojson)

    calls_sql = [c[0][0] for c in cursor.execute.call_args_list]
    assert any("DELETE FROM rivers" in s for s in calls_sql)
    delete_idx = next(i for i, s in enumerate(calls_sql) if "DELETE" in s)
    insert_idx = next(i for i, s in enumerate(calls_sql) if "INSERT INTO rivers" in s)
    assert delete_idx < insert_idx


def test_load_rivers_commits(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": None, "importance": 10, "source_name": "Natural Earth"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
    ])
    conn, _ = _make_conn()
    load_rivers(conn, geojson_path=geojson)
    conn.commit.assert_called_once()


def test_load_rivers_uses_st_geomfromtext(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": None, "importance": 10, "source_name": "Natural Earth"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
    ])
    conn, cursor = _make_conn()
    load_rivers(conn, geojson_path=geojson)

    insert_sql = next(
        c[0][0] for c in cursor.execute.call_args_list
        if "INSERT INTO rivers" in c[0][0]
    )
    assert "ST_GeomFromText" in insert_sql
    assert "4326" in insert_sql


def test_load_rivers_raises_if_file_missing(tmp_path):
    conn, _ = _make_conn()
    with pytest.raises(FileNotFoundError):
        load_rivers(conn, geojson_path=tmp_path / "nonexistent.geojson")


def test_load_rivers_empty_collection(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [])
    conn, _ = _make_conn()
    result = load_rivers(conn, geojson_path=geojson)
    assert result == 0


def test_load_rivers_skips_invalid_geometry(tmp_path):
    """Feature with None geometry is skipped; valid ones still load."""
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": None, "importance": 10, "source_name": "NE"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
        {"type": "Feature",
         "properties": {"name": "Bad"},
         "geometry": None},
    ])
    conn, _ = _make_conn()
    result = load_rivers(conn, geojson_path=geojson)
    assert result == 1


def test_load_rivers_passes_map_modes_array(tmp_path):
    geojson = _write_rivers_geojson(tmp_path, [
        {"type": "Feature",
         "properties": {"name": "Nile", "name_alt": None, "importance": 10, "source_name": "NE"},
         "geometry": {"type": "LineString", "coordinates": NILE_COORDS}},
    ])
    conn, cursor = _make_conn()
    load_rivers(conn, geojson_path=geojson)

    insert_params = next(
        c[0][1] for c in cursor.execute.call_args_list
        if "INSERT INTO rivers" in c[0][0]
    )
    map_modes = insert_params[-1]
    assert "political" in map_modes
    assert "physical" in map_modes
