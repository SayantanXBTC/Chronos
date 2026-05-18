"""Unit tests for place_names_loader.py — uses temp CSV, mocked DB cursor."""
import csv
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from data.place_names_loader import load_place_names


def _make_conn():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


def _write_csv(tmp_path: Path, rows: list[dict]) -> Path:
    fields = ["name", "name_modern", "type", "lon", "lat",
              "year_start", "year_end", "importance", "label_priority", "min_zoom", "source_name"]
    p = tmp_path / "cities.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return p


def test_load_place_names_returns_count(tmp_path):
    csv_path = _write_csv(tmp_path, [
        {"name": "Rome", "name_modern": "Rome", "type": "city",
         "lon": "12.5", "lat": "41.9", "year_start": "-753", "year_end": "",
         "importance": "10", "label_priority": "10", "min_zoom": "2", "source_name": "AWMC"},
        {"name": "Carthage", "name_modern": "Tunis", "type": "city",
         "lon": "10.3", "lat": "36.9", "year_start": "-800", "year_end": "-146",
         "importance": "8", "label_priority": "8", "min_zoom": "3", "source_name": "AWMC"},
    ])
    conn, cursor = _make_conn()
    result = load_place_names(conn, csv_path=csv_path)
    assert result == 2


def test_load_place_names_deletes_before_insert(tmp_path):
    csv_path = _write_csv(tmp_path, [
        {"name": "Rome", "name_modern": "Rome", "type": "city",
         "lon": "12.5", "lat": "41.9", "year_start": "-753", "year_end": "",
         "importance": "10", "label_priority": "10", "min_zoom": "2", "source_name": "AWMC"},
    ])
    conn, cursor = _make_conn()
    load_place_names(conn, csv_path=csv_path)

    calls_sql = [c[0][0] for c in cursor.execute.call_args_list]
    assert any("DELETE FROM place_names" in s for s in calls_sql)
    # DELETE must come before INSERT
    delete_idx = next(i for i, s in enumerate(calls_sql) if "DELETE" in s)
    insert_idx = next(i for i, s in enumerate(calls_sql) if "INSERT INTO place_names" in s)
    assert delete_idx < insert_idx


def test_load_place_names_commits(tmp_path):
    csv_path = _write_csv(tmp_path, [
        {"name": "Rome", "name_modern": "", "type": "city",
         "lon": "12.5", "lat": "41.9", "year_start": "-753", "year_end": "",
         "importance": "10", "label_priority": "10", "min_zoom": "2", "source_name": "AWMC"},
    ])
    conn, _ = _make_conn()
    load_place_names(conn, csv_path=csv_path)
    conn.commit.assert_called_once()


def test_load_place_names_uses_st_makepoint(tmp_path):
    csv_path = _write_csv(tmp_path, [
        {"name": "Alexandria", "name_modern": "Alexandria", "type": "city",
         "lon": "29.9", "lat": "31.2", "year_start": "-331", "year_end": "",
         "importance": "9", "label_priority": "9", "min_zoom": "2", "source_name": "AWMC"},
    ])
    conn, cursor = _make_conn()
    load_place_names(conn, csv_path=csv_path)

    insert_sql = next(
        c[0][0] for c in cursor.execute.call_args_list
        if "INSERT INTO place_names" in c[0][0]
    )
    assert "ST_MakePoint" in insert_sql
    assert "ST_SetSRID" in insert_sql


def test_load_place_names_raises_if_file_missing(tmp_path):
    conn, _ = _make_conn()
    with pytest.raises(FileNotFoundError):
        load_place_names(conn, csv_path=tmp_path / "nonexistent.csv")


def test_load_place_names_skips_bad_rows(tmp_path):
    """Row with non-numeric lon is skipped; valid rows still load."""
    fields = ["name", "name_modern", "type", "lon", "lat",
              "year_start", "year_end", "importance", "label_priority", "min_zoom", "source_name"]
    p = tmp_path / "cities.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow({"name": "Rome", "name_modern": "Rome", "type": "city",
                         "lon": "12.5", "lat": "41.9", "year_start": "-753", "year_end": "",
                         "importance": "10", "label_priority": "10", "min_zoom": "2", "source_name": "AWMC"})
        writer.writerow({"name": "Bad", "name_modern": "", "type": "city",
                         "lon": "NOT_A_NUMBER", "lat": "0", "year_start": "-100", "year_end": "",
                         "importance": "5", "label_priority": "5", "min_zoom": "3", "source_name": "test"})

    conn, _ = _make_conn()
    result = load_place_names(conn, csv_path=p)
    assert result == 1


def test_load_place_names_null_year_end(tmp_path):
    """Empty year_end should produce NULL, not crash."""
    csv_path = _write_csv(tmp_path, [
        {"name": "Rome", "name_modern": "Rome", "type": "city",
         "lon": "12.5", "lat": "41.9", "year_start": "-753", "year_end": "",
         "importance": "10", "label_priority": "10", "min_zoom": "2", "source_name": "AWMC"},
    ])
    conn, cursor = _make_conn()
    result = load_place_names(conn, csv_path=csv_path)
    assert result == 1

    insert_params = next(
        c[0][1] for c in cursor.execute.call_args_list
        if "INSERT INTO place_names" in c[0][0]
    )
    # year_end param (index 7) should be None
    assert insert_params[7] is None
