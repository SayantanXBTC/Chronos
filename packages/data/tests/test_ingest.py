import os
import psycopg2
import pytest

from data.ingest import run

TEST_DB_URL = "postgresql://history:history@localhost:5433/history_test"


@pytest.fixture(autouse=True)
def set_db_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)


@pytest.fixture(autouse=True)
def clean_entities(db_conn):
    yield
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM territories")
        cur.execute("DELETE FROM entity_names")
        cur.execute("DELETE FROM entities WHERE slug IN ('roman-republic', 'germanic-tribes')")
    db_conn.commit()


def test_ingest_single_entity_creates_rows(db_conn):
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM entities WHERE slug = 'roman-republic'")
        assert cur.fetchone()[0] == 1

        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            """
        )
        assert cur.fetchone()[0] == 3  # 3 phases


def test_ingest_sets_correct_year_ranges(db_conn):
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT year_start, year_end FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            ORDER BY year_start
            """
        )
        rows = cur.fetchall()

    assert rows[0] == (-500, -264)
    assert rows[1] == (-264, -100)
    assert rows[2] == (-100, -27)


def test_ingest_is_idempotent(db_conn):
    run(entity_filter="roman-republic")
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM entities WHERE slug = 'roman-republic'")
        assert cur.fetchone()[0] == 1

        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            """
        )
        assert cur.fetchone()[0] == 3


def test_ingest_single_phase_entity(db_conn):
    run(entity_filter="germanic-tribes")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'germanic-tribes'
            """
        )
        assert cur.fetchone()[0] == 1
