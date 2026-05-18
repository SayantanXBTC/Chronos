"""
Tests for reporting.py — all mocked, no live DB required.
"""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

from data.reporting import (
    audit_source,
    coverage_report,
    diff_entity,
    stats,
    update_coverage,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_conn(*cursor_side_effects):
    """
    Build a mock connection whose cursor().__enter__ returns a mock cursor
    whose fetchone / fetchall return values are driven by side_effect lists.
    """
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur
    return conn, cur


# ---------------------------------------------------------------------------
# stats()
# ---------------------------------------------------------------------------

def test_stats_returns_correct_shape():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    # fetchone calls in order:
    # 1) COUNT(*) entities
    # 2) territory aggregate row
    # 3) COUNT(*) place_names
    # 4) importance tiers (single row, 3 cols)
    # 5) COUNT(*) lineages
    cur.fetchone.side_effect = [
        (42,),                              # total entities
        (100, 5, -200.0, -500, 500),        # territory aggregate
        (20,),                              # total place_names
        (10, 8, 2),                         # importance tiers (single row, 3 cols)
        (7,),                               # total lineages
    ]
    # fetchall calls in order:
    # 1) GROUP BY type
    # 2) DISTINCT region_names
    cur.fetchall.side_effect = [
        [("empire", 30), ("kingdom", 12)],  # by_type
        [("europe",), ("asia",)],            # region_names
    ]

    result = stats(conn)

    assert "entities" in result
    assert "territories" in result
    assert "place_names" in result
    assert "lineages" in result
    assert "regions" in result

    assert result["entities"]["total"] == 42
    assert result["territories"]["total"] == 100
    assert result["place_names"]["total"] == 20
    assert result["lineages"]["total"] == 7
    assert isinstance(result["regions"], list)


def test_stats_by_type_grouping():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.fetchone.side_effect = [
        (3,),                               # total entities
        (50, 2, -100.0, -300, 200),         # territory aggregate
        (0,),                               # total place_names
        (0, 0, 0),                          # importance tiers
        (0,),                               # total lineages
    ]
    cur.fetchall.side_effect = [
        [("empire", 2), ("kingdom", 1)],    # by_type
        [],                                  # region_names
    ]

    result = stats(conn)

    assert result["entities"]["by_type"]["empire"] == 2
    assert result["entities"]["by_type"]["kingdom"] == 1
    assert result["entities"]["total"] == 3


# ---------------------------------------------------------------------------
# diff_entity()
# ---------------------------------------------------------------------------

def test_diff_entity_ok_when_counts_match():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.fetchone.side_effect = [
        ("some-uuid",),  # entity found
        (3,),            # db territory count
    ]

    with patch("data.reporting.glob.glob", return_value=["f1.geojson", "f2.geojson", "f3.geojson"]):
        result = diff_entity(conn, slug="roman-empire", raw_dir="data/raw/political")

    assert result["status"] == "ok"
    assert result["db_territories"] == 3
    assert result["raw_phases"] == 3


def test_diff_entity_gap_when_counts_differ():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.fetchone.side_effect = [
        ("some-uuid",),  # entity found
        (2,),            # db has 2 territories
    ]

    with patch("glob.glob", return_value=["f1.geojson", "f2.geojson", "f3.geojson"]):
        result = diff_entity(conn, slug="roman-empire", raw_dir="data/raw/political")

    assert result["status"] == "gap"
    assert result["db_territories"] == 2
    assert result["raw_phases"] == 3
    assert "Mismatch" in result["message"]


def test_diff_entity_not_found():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.fetchone.return_value = None  # entity not in DB

    result = diff_entity(conn, slug="nonexistent-slug")

    assert result["status"] == "not_found"
    assert result["db_territories"] == 0
    assert result["raw_phases"] == 0
    assert "nonexistent-slug" in result["message"]


# ---------------------------------------------------------------------------
# audit_source()
# ---------------------------------------------------------------------------

def test_audit_source_returns_list():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.description = [
        ("entity_slug",),
        ("territory_id",),
        ("year_start",),
        ("year_end",),
        ("date_precision",),
        ("confidence_type",),
        ("source_name",),
    ]
    cur.fetchall.return_value = [
        ("roman-empire", "uuid-1", -27, 117, "year", "approximate", "cshapes v2"),
        ("carthage", "uuid-2", -814, -146, "year", "approximate", "cshapes v2"),
    ]

    result = audit_source(conn, source_id="cshapes")

    assert len(result) == 2
    assert result[0]["entity_slug"] == "roman-empire"
    assert result[0]["source_name"] == "cshapes v2"
    assert result[1]["entity_slug"] == "carthage"
    assert "territory_id" in result[0]


# ---------------------------------------------------------------------------
# coverage_report()
# ---------------------------------------------------------------------------

def test_coverage_report_empty():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.description = [
        ("id",), ("region_name",), ("year_start",), ("year_end",),
        ("completeness",), ("entity_count",), ("primary_source",),
        ("notes",), ("updated_at",),
    ]
    cur.fetchall.return_value = []

    result = coverage_report(conn)

    assert result == []


def test_coverage_report_returns_rows():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    cur.description = [
        ("id",), ("region_name",), ("year_start",), ("year_end",),
        ("completeness",), ("entity_count",), ("primary_source",),
        ("notes",), ("updated_at",),
    ]
    cur.fetchall.return_value = [
        ("uuid-1", "mediterranean", -500, 500, "complete", 13, "AWMC", None, None),
    ]

    result = coverage_report(conn)

    assert len(result) == 1
    assert result[0]["region_name"] == "mediterranean"
    assert result[0]["completeness"] == "complete"


# ---------------------------------------------------------------------------
# update_coverage()
# ---------------------------------------------------------------------------

def test_update_coverage_calls_delete_then_insert():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cur

    with patch("data.reporting.uuid.uuid4", return_value="fixed-uuid"):
        update_coverage(
            conn,
            region_name="mediterranean",
            year_start=-500,
            year_end=500,
            completeness="complete",
            entity_count=13,
            primary_source="AWMC",
            notes="Test note",
        )

    # Verify DELETE was the first execute call
    first_call = cur.execute.call_args_list[0]
    assert "DELETE FROM region_coverage" in first_call[0][0]
    assert first_call[0][1] == ("mediterranean", -500)

    # Verify INSERT was the second execute call
    second_call = cur.execute.call_args_list[1]
    assert "INSERT INTO region_coverage" in second_call[0][0]
    insert_params = second_call[0][1]
    assert insert_params[1] == "mediterranean"   # region_name
    assert insert_params[2] == -500              # year_start
    assert insert_params[3] == 500               # year_end
    assert insert_params[4] == "complete"        # completeness
    assert insert_params[5] == 13               # entity_count
    assert insert_params[6] == "AWMC"           # primary_source
    assert insert_params[7] == "Test note"      # notes

    # Verify commit was called
    conn.commit.assert_called_once()
