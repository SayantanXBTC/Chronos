from unittest.mock import MagicMock

from data.qa import check_overlaps, check_invalid_geoms, check_temporal_gaps


def _make_mock_conn(rows: list[tuple], col_names: list[str]) -> MagicMock:
    """Build a mock psycopg2 connection whose cursor returns given rows."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.description = [(col,) for col in col_names]
    mock_cursor.fetchall.return_value = rows

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


class TestCheckInvalidGeoms:
    def test_empty_db_returns_empty_list(self):
        conn = _make_mock_conn([], ["entity_slug", "territory_id", "year_start", "year_end"])
        result = check_invalid_geoms(conn)
        assert result == []

    def test_one_invalid_geom_returned(self):
        conn = _make_mock_conn(
            [("roman-empire", "uuid-1", -27, 395)],
            ["entity_slug", "territory_id", "year_start", "year_end"],
        )
        result = check_invalid_geoms(conn)
        assert len(result) == 1
        assert result[0]["entity_slug"] == "roman-empire"
        assert result[0]["territory_id"] == "uuid-1"

    def test_result_is_list_of_dicts(self):
        conn = _make_mock_conn(
            [("han-dynasty", "uuid-2", -206, 220)],
            ["entity_slug", "territory_id", "year_start", "year_end"],
        )
        result = check_invalid_geoms(conn)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert set(result[0].keys()) == {"entity_slug", "territory_id", "year_start", "year_end"}


class TestCheckTemporalGaps:
    def test_no_gaps_returns_empty_list(self):
        conn = _make_mock_conn([], ["entity_slug", "gap_start", "gap_end", "gap_years"])
        result = check_temporal_gaps(conn)
        assert result == []

    def test_one_gap_returned(self):
        conn = _make_mock_conn(
            [("roman-empire", 395, 476, 81)],
            ["entity_slug", "gap_start", "gap_end", "gap_years"],
        )
        result = check_temporal_gaps(conn)
        assert len(result) == 1
        assert result[0]["entity_slug"] == "roman-empire"
        assert result[0]["gap_years"] == 81

    def test_multiple_gaps_returned(self):
        conn = _make_mock_conn(
            [
                ("carthage", -300, -264, 36),
                ("carthage", -200, -146, 54),
            ],
            ["entity_slug", "gap_start", "gap_end", "gap_years"],
        )
        result = check_temporal_gaps(conn)
        assert len(result) == 2


class TestCheckOverlaps:
    def test_empty_db_returns_empty_list(self):
        conn = _make_mock_conn(
            [],
            ["entity_a", "entity_b", "year_overlap_start", "year_overlap_end",
             "overlap_fraction", "territory_a_id", "territory_b_id"],
        )
        result = check_overlaps(conn)
        assert result == []

    def test_overlap_returned_with_all_fields(self):
        conn = _make_mock_conn(
            [("roman-empire", "parthian-empire", -27, 100, 0.65, "uuid-a", "uuid-b")],
            ["entity_a", "entity_b", "year_overlap_start", "year_overlap_end",
             "overlap_fraction", "territory_a_id", "territory_b_id"],
        )
        result = check_overlaps(conn)
        assert len(result) == 1
        row = result[0]
        assert row["entity_a"] == "roman-empire"
        assert row["entity_b"] == "parthian-empire"
        assert row["overlap_fraction"] == 0.65

    def test_custom_threshold_passed_to_query(self):
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.description = [
            ("entity_a",), ("entity_b",), ("year_overlap_start",), ("year_overlap_end",),
            ("overlap_fraction",), ("territory_a_id",), ("territory_b_id",),
        ]
        mock_cursor.fetchall.return_value = []

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        check_overlaps(mock_conn, threshold=0.75)
        call_args = mock_cursor.execute.call_args
        # threshold value should be in the params dict
        assert 0.75 in call_args[0][1].values()
