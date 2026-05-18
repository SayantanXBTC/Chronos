"""Integration tests: verify M2 columns are populated by ingest.

Requires test DB (postgresql://history:history@localhost:5433/history_test).
Skipped automatically when DB is unavailable.
"""
import os
import pytest
import psycopg2

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
        cur.execute("DELETE FROM entities WHERE slug = 'roman-republic'")
    db_conn.commit()


def test_ingest_m2_confidence_type_set(db_conn):
    run(entity_filter="roman-republic")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT confidence_type FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            """
        )
        values = {row[0] for row in cur.fetchall()}
    # All phases should have a non-null confidence_type
    assert len(values) > 0
    assert None not in values
    assert all(v in ("exact", "approximate", "inferred", "disputed") for v in values)


def test_ingest_m2_source_name_set(db_conn):
    run(entity_filter="roman-republic")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT source_name FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            LIMIT 1
            """
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] is not None
    assert len(row[0]) > 0


def test_ingest_m2_importance_set(db_conn):
    run(entity_filter="roman-republic")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT importance FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            LIMIT 1
            """
        )
        row = cur.fetchone()
    assert row is not None
    assert 1 <= row[0] <= 10


def test_ingest_m2_map_modes_set(db_conn):
    run(entity_filter="roman-republic")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT map_modes FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            LIMIT 1
            """
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] is not None
    assert "political" in row[0]


def test_ingest_m2_confidence_score_set(db_conn):
    run(entity_filter="roman-republic")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT confidence_score FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            LIMIT 1
            """
        )
        row = cur.fetchone()
    assert row is not None
    assert row[0] is not None
    assert 0.0 <= row[0] <= 1.0
