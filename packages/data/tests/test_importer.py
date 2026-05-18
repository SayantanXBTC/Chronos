"""Unit tests for importer.py — no real DB required, everything mocked."""
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
import yaml

from data.importer import Importer, _extract_field, _import_geojson, ImportError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source_config(tmp_path: Path, extra: dict | None = None) -> Path:
    config = {
        "source_name": "Test Source",
        "source_url": "https://example.com",
        "source_license": "CC BY 4.0",
        "data_version": "2024-01",
        "fields": {
            "slug": "SLUG",
            "name": "NAME",
            "year_start": "YRSTART",
            "year_end": "YREND",
        },
        "defaults": {
            "type": "polity",
            "color": "#cc0000",
            "confidence_type": "approximate",
            "confidence_score": 0.6,
            "resolution_km": 50,
            "importance": 6,
            "map_modes": ["political"],
        },
    }
    if extra:
        config.update(extra)
    p = tmp_path / "test_source.yml"
    p.write_text(yaml.dump(config))
    return p


def _make_geojson(tmp_path: Path, features: list) -> Path:
    fc = {"type": "FeatureCollection", "features": features}
    p = tmp_path / "test.geojson"
    p.write_text(json.dumps(fc))
    return p


def _make_mock_conn():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = ("aaaaaaaa-0000-0000-0000-000000000001",)
    return mock_conn, mock_cursor


# ---------------------------------------------------------------------------
# _extract_field
# ---------------------------------------------------------------------------

def test_extract_field_returns_value():
    assert _extract_field({"NAME": "Rome"}, "NAME") == "Rome"


def test_extract_field_missing_key_returns_none():
    assert _extract_field({"NAME": "Rome"}, "MISSING") is None


def test_extract_field_none_mapping_returns_none():
    assert _extract_field({"NAME": "Rome"}, None) is None


# ---------------------------------------------------------------------------
# Importer — file not found
# ---------------------------------------------------------------------------

def test_import_file_raises_on_missing_file(tmp_path):
    config_path = _make_source_config(tmp_path)
    mock_conn, _ = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    with pytest.raises(FileNotFoundError):
        imp.import_file(tmp_path / "nonexistent.geojson")


# ---------------------------------------------------------------------------
# Importer — unsupported extension
# ---------------------------------------------------------------------------

def test_import_file_raises_on_bad_extension(tmp_path):
    config_path = _make_source_config(tmp_path)
    bad_file = tmp_path / "data.csv"
    bad_file.write_text("a,b,c")
    mock_conn, _ = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    with pytest.raises(ImportError, match="Unsupported"):
        imp.import_file(bad_file)


# ---------------------------------------------------------------------------
# GeoJSON import — happy path
# ---------------------------------------------------------------------------

def test_import_geojson_loads_feature(tmp_path):
    config_path = _make_source_config(tmp_path)
    geojson = _make_geojson(tmp_path, [
        {
            "type": "Feature",
            "properties": {"SLUG": "rome", "NAME": "Rome", "YRSTART": -753, "YREND": -27},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[[[12.0, 41.0], [13.0, 41.0], [13.0, 42.0], [12.0, 42.0], [12.0, 41.0]]]],
            },
        }
    ])
    mock_conn, mock_cursor = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    loaded, skipped = imp.import_file(geojson)

    assert loaded == 1
    assert skipped == 0
    mock_conn.commit.assert_called_once()


def test_import_geojson_returns_counts(tmp_path):
    config_path = _make_source_config(tmp_path)
    good_feat = {
        "type": "Feature",
        "properties": {"SLUG": "rome", "NAME": "Rome", "YRSTART": -264, "YREND": None},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[12.0, 41.0], [13.0, 41.0], [13.0, 42.0], [12.0, 42.0], [12.0, 41.0]]]],
        },
    }
    bad_feat = {
        "type": "Feature",
        "properties": {"SLUG": "bad", "NAME": "Bad"},
        "geometry": None,  # will cause shape() to fail
    }
    geojson = _make_geojson(tmp_path, [good_feat, bad_feat])
    mock_conn, _ = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    loaded, skipped = imp.import_file(geojson)

    assert loaded == 1
    assert skipped == 1


def test_import_geojson_passes_source_metadata_to_insert(tmp_path):
    config_path = _make_source_config(tmp_path)
    geojson = _make_geojson(tmp_path, [
        {
            "type": "Feature",
            "properties": {"SLUG": "rome", "NAME": "Rome", "YRSTART": -264, "YREND": None},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[[[12.0, 41.0], [13.0, 41.0], [13.0, 42.0], [12.0, 42.0], [12.0, 41.0]]]],
            },
        }
    ])
    mock_conn, mock_cursor = _make_mock_conn()
    imp = Importer(mock_conn, config_path)
    imp.import_file(geojson)

    # Find the INSERT INTO territories call
    insert_calls = [
        c for c in mock_cursor.execute.call_args_list
        if "INSERT INTO territories" in str(c)
    ]
    assert len(insert_calls) == 1
    params = insert_calls[0][0][1]
    # source_name is 9th param (index 8, after id, entity_id, geom_wkt, simplified_wkt, year_start, year_end, confidence_type, confidence_score)
    assert "Test Source" in params


# ---------------------------------------------------------------------------
# Importer — empty FeatureCollection
# ---------------------------------------------------------------------------

def test_import_geojson_empty_file(tmp_path):
    config_path = _make_source_config(tmp_path)
    geojson = _make_geojson(tmp_path, [])
    mock_conn, _ = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    loaded, skipped = imp.import_file(geojson)

    assert loaded == 0
    assert skipped == 0


# ---------------------------------------------------------------------------
# Importer — Polygon auto-converted to MultiPolygon
# ---------------------------------------------------------------------------

def test_import_geojson_polygon_converted_to_multipolygon(tmp_path):
    config_path = _make_source_config(tmp_path)
    geojson = _make_geojson(tmp_path, [
        {
            "type": "Feature",
            "properties": {"SLUG": "rome", "NAME": "Rome", "YRSTART": -264, "YREND": None},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[12.0, 41.0], [13.0, 41.0], [13.0, 42.0], [12.0, 42.0], [12.0, 41.0]]],
            },
        }
    ])
    mock_conn, _ = _make_mock_conn()
    imp = Importer(mock_conn, config_path)

    loaded, skipped = imp.import_file(geojson)

    assert loaded == 1
    assert skipped == 0
