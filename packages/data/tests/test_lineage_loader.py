"""Tests for lineage_loader.py."""
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import yaml

from data.lineage_loader import load_lineages_from_yaml, resolve_slugs, upsert_lineages

# Path to the canonical lineage data file
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_ALL_YAML = _REPO_ROOT / "data" / "raw" / "lineages" / "all.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_conn(cursor_rows=None, rowcount=1):
    """Build a mock psycopg2 connection."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    if cursor_rows is not None:
        mock_cursor.fetchall.return_value = cursor_rows
    mock_cursor.rowcount = rowcount

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# ---------------------------------------------------------------------------
# load_lineages_from_yaml
# ---------------------------------------------------------------------------

class TestLoadLineagesFromYaml:
    def test_load_lineages_from_yaml_parses_all_fields(self):
        lineages = load_lineages_from_yaml(_ALL_YAML)
        assert len(lineages) == 9
        first = lineages[0]
        assert first["parent_slug"] == "roman-republic"
        assert first["child_slug"] == "roman-empire"
        assert first["relationship_type"] == "evolved_into"
        assert first["year"] == -27
        assert first["notes"] == "Transition from Republic to Principate under Augustus"

    def test_load_lineages_notes_optional(self):
        # Second entry has no notes field
        lineages = load_lineages_from_yaml(_ALL_YAML)
        second = lineages[1]
        assert second["parent_slug"] == "roman-empire"
        assert second["child_slug"] == "western-roman-empire"
        # notes should be absent or None when not in YAML
        assert "notes" not in second or second.get("notes") is None

    def test_load_lineages_all_relationships_parsed(self):
        lineages = load_lineages_from_yaml(_ALL_YAML)
        relationships = [l["relationship_type"] for l in lineages]
        assert "evolved_into" in relationships
        assert "split_from" in relationships
        assert "continuation" in relationships
        assert "successor" in relationships

    def test_load_lineages_empty_file_returns_empty_list(self, tmp_path):
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("lineages: []\n")
        result = load_lineages_from_yaml(yaml_file)
        assert result == []

    def test_load_lineages_invalid_relationship_still_parses(self, tmp_path):
        """Loader does not validate relationship types — DB constraint does."""
        yaml_file = tmp_path / "bad_rel.yaml"
        yaml_file.write_text(
            "lineages:\n"
            "  - parent: a\n"
            "    child: b\n"
            "    relationship: totally_made_up\n"
            "    year: 100\n"
        )
        result = load_lineages_from_yaml(yaml_file)
        assert len(result) == 1
        assert result[0]["relationship_type"] == "totally_made_up"

    def test_load_lineages_year_negative(self):
        lineages = load_lineages_from_yaml(_ALL_YAML)
        # roman-republic -> roman-empire is year -27
        assert lineages[0]["year"] == -27


# ---------------------------------------------------------------------------
# resolve_slugs
# ---------------------------------------------------------------------------

class TestResolveSlugs:
    def test_resolve_slugs_found(self):
        conn, cur = _make_conn(
            cursor_rows=[
                ("roman-empire", "uuid-1111"),
                ("roman-republic", "uuid-2222"),
            ]
        )
        result = resolve_slugs(conn, ["roman-empire", "roman-republic"])
        assert result == {"roman-empire": "uuid-1111", "roman-republic": "uuid-2222"}

    def test_resolve_slugs_missing_raises(self):
        conn, cur = _make_conn(cursor_rows=[("roman-empire", "uuid-1111")])
        with pytest.raises(ValueError) as exc_info:
            resolve_slugs(conn, ["roman-empire", "missing-slug"])
        assert "missing-slug" in str(exc_info.value)

    def test_resolve_slugs_empty_list_returns_empty(self):
        conn, cur = _make_conn(cursor_rows=[])
        result = resolve_slugs(conn, [])
        assert result == {}
        # Should not query DB for empty list
        cur.execute.assert_not_called()


# ---------------------------------------------------------------------------
# upsert_lineages
# ---------------------------------------------------------------------------

class TestUpsertLineages:
    def _lineage_rows(self):
        return [
            {
                "parent_slug": "roman-republic",
                "child_slug": "roman-empire",
                "relationship_type": "evolved_into",
                "year": -27,
                "notes": "Some note",
            }
        ]

    def _slug_map(self):
        return {"roman-republic": "uuid-aaa", "roman-empire": "uuid-bbb"}

    def test_upsert_lineages_calls_execute(self):
        conn, cur = _make_conn(
            cursor_rows=[("roman-republic", "uuid-aaa"), ("roman-empire", "uuid-bbb")],
            rowcount=1,
        )
        upsert_lineages(conn, self._lineage_rows())
        # execute should have been called (once for SELECT, once for INSERT)
        assert cur.execute.call_count >= 1
        # Check that the INSERT SQL contains expected table name
        insert_sql = cur.execute.call_args_list[-1][0][0]
        assert "INSERT INTO entity_lineages" in insert_sql

    def test_upsert_lineages_idempotent_on_conflict(self):
        conn, cur = _make_conn(
            cursor_rows=[("roman-republic", "uuid-aaa"), ("roman-empire", "uuid-bbb")],
            rowcount=1,
        )
        upsert_lineages(conn, self._lineage_rows())
        insert_sql = cur.execute.call_args_list[-1][0][0]
        assert "ON CONFLICT DO NOTHING" in insert_sql

    def test_upsert_lineages_returns_count(self):
        conn, cur = _make_conn(
            cursor_rows=[
                ("roman-republic", "uuid-aaa"),
                ("roman-empire", "uuid-bbb"),
                ("umayyad-caliphate", "uuid-ccc"),
                ("abbasid-caliphate", "uuid-ddd"),
                ("mongol-empire", "uuid-eee"),
                ("yuan-dynasty", "uuid-fff"),
            ],
            rowcount=1,
        )
        lineages = [
            {"parent_slug": "roman-republic", "child_slug": "roman-empire",
             "relationship_type": "evolved_into", "year": -27},
            {"parent_slug": "umayyad-caliphate", "child_slug": "abbasid-caliphate",
             "relationship_type": "successor", "year": 750},
            {"parent_slug": "mongol-empire", "child_slug": "yuan-dynasty",
             "relationship_type": "split_from", "year": 1271},
        ]
        count = upsert_lineages(conn, lineages)
        assert count == 3

    def test_upsert_lineages_resolves_slugs_before_insert(self):
        conn, cur = _make_conn(
            cursor_rows=[("roman-republic", "uuid-aaa"), ("roman-empire", "uuid-bbb")],
            rowcount=1,
        )
        upsert_lineages(conn, self._lineage_rows())
        # First execute call should be the SELECT for slug resolution
        first_call_sql = cur.execute.call_args_list[0][0][0]
        assert "SELECT" in first_call_sql
        assert "entities" in first_call_sql

    def test_upsert_lineages_empty_returns_zero(self):
        conn, cur = _make_conn(cursor_rows=[], rowcount=0)
        count = upsert_lineages(conn, [])
        assert count == 0
