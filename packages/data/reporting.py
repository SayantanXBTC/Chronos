"""
reporting.py — DB query functions for stats, diff, audit, and coverage reporting.
"""
from __future__ import annotations

import glob
import os
import uuid
from typing import Any

import psycopg2.extensions


# ---------------------------------------------------------------------------
# Task 8: stats, diff_entity, audit_source
# ---------------------------------------------------------------------------


def stats(conn: psycopg2.extensions.connection) -> dict:
    """Return a summary dict of entity/territory/place_name/lineage/region data."""
    result: dict[str, Any] = {}

    with conn.cursor() as cur:
        # --- entities ---
        cur.execute("SELECT COUNT(*) FROM entities")
        total_entities = cur.fetchone()[0]

        cur.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
        by_type = {row[0]: row[1] for row in cur.fetchall()}

        result["entities"] = {
            "total": total_entities,
            "by_type": by_type,
        }

        # --- territories ---
        cur.execute(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(geom_lo) AS with_geom_lo,
                AVG(year_start) AS avg_year_start,
                MIN(year_start) AS earliest_year,
                MAX(year_start) AS latest_year
            FROM territories
            """
        )
        row = cur.fetchone()
        result["territories"] = {
            "total": row[0] or 0,
            "with_geom_lo": row[1] or 0,
            "avg_year_start": float(row[2]) if row[2] is not None else None,
            "earliest_year": row[3],
            "latest_year": row[4],
        }

        # --- place_names ---
        cur.execute("SELECT COUNT(*) FROM place_names")
        total_places = cur.fetchone()[0]

        cur.execute(
            """
            SELECT
                SUM(CASE WHEN importance >= 8 THEN 1 ELSE 0 END) AS high,
                SUM(CASE WHEN importance >= 5 AND importance <= 7 THEN 1 ELSE 0 END) AS medium,
                SUM(CASE WHEN importance >= 1 AND importance <= 4 THEN 1 ELSE 0 END) AS low
            FROM place_names
            """
        )
        prow = cur.fetchone()
        result["place_names"] = {
            "total": total_places,
            "by_importance_tier": {
                "high (8-10)": int(prow[0] or 0),
                "medium (5-7)": int(prow[1] or 0),
                "low (1-4)": int(prow[2] or 0),
            },
        }

        # --- lineages ---
        cur.execute("SELECT COUNT(*) FROM entity_lineages")
        result["lineages"] = {"total": cur.fetchone()[0]}

        # --- regions ---
        cur.execute(
            "SELECT DISTINCT region_name FROM region_coverage ORDER BY region_name"
        )
        result["regions"] = [row[0] for row in cur.fetchall()]

    return result


def diff_entity(
    conn: psycopg2.extensions.connection,
    slug: str,
    raw_dir: str = "data/raw/political",
) -> dict:
    """
    Compare DB territory count vs raw GeoJSON phase files for a given slug.

    Searches for phase-N.geojson files under raw_dir/**/<slug>/.
    """
    with conn.cursor() as cur:
        # Look up the entity
        cur.execute("SELECT id FROM entities WHERE slug = %s", (slug,))
        row = cur.fetchone()
        if row is None:
            return {
                "slug": slug,
                "db_territories": 0,
                "raw_phases": 0,
                "status": "not_found",
                "message": f"Entity '{slug}' not found in DB",
            }
        entity_id = row[0]

        cur.execute(
            "SELECT COUNT(*) FROM territories WHERE entity_id = %s::uuid",
            (str(entity_id),),
        )
        db_territories = cur.fetchone()[0]

    # Count raw phase files: data/raw/political/**/<slug>/phase-*.geojson
    pattern = os.path.join(raw_dir, "**", slug, "phase-*.geojson")
    raw_files = glob.glob(pattern, recursive=True)
    raw_phases = len(raw_files)

    if db_territories == raw_phases:
        status = "ok"
        message = f"DB ({db_territories}) matches raw phases ({raw_phases})"
    else:
        status = "gap"
        message = (
            f"Mismatch: DB has {db_territories} territories, "
            f"raw has {raw_phases} phase files"
        )

    return {
        "slug": slug,
        "db_territories": db_territories,
        "raw_phases": raw_phases,
        "status": status,
        "message": message,
    }


def audit_source(
    conn: psycopg2.extensions.connection,
    source_id: str,
) -> list[dict]:
    """
    List all territories whose source_name matches (ILIKE %source_id%).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                e.slug AS entity_slug,
                t.id::text AS territory_id,
                t.year_start,
                t.year_end,
                t.date_precision,
                t.confidence_type,
                t.source_name
            FROM territories t
            JOIN entities e ON e.id = t.entity_id
            WHERE t.source_name ILIKE %s
            ORDER BY e.slug, t.year_start
            """,
            (f"%{source_id}%",),
        )
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Task 9: coverage_report, update_coverage
# ---------------------------------------------------------------------------


def coverage_report(conn: psycopg2.extensions.connection) -> list[dict]:
    """Return all rows from region_coverage sorted by region_name, year_start."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id::text,
                region_name,
                year_start,
                year_end,
                completeness,
                entity_count,
                primary_source,
                notes,
                updated_at
            FROM region_coverage
            ORDER BY region_name, year_start
            """
        )
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def update_coverage(
    conn: psycopg2.extensions.connection,
    region_name: str,
    year_start: int,
    year_end: int | None,
    completeness: str,
    entity_count: int = 0,
    primary_source: str | None = None,
    notes: str | None = None,
) -> None:
    """
    Idempotent upsert into region_coverage using DELETE + INSERT.
    Matches on (region_name, year_start).
    """
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM region_coverage WHERE region_name = %s AND year_start = %s",
            (region_name, year_start),
        )
        cur.execute(
            """
            INSERT INTO region_coverage
                (id, region_name, year_start, year_end, completeness,
                 entity_count, primary_source, notes, updated_at)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                str(uuid.uuid4()),
                region_name,
                year_start,
                year_end,
                completeness,
                entity_count,
                primary_source,
                notes,
            ),
        )
    conn.commit()
