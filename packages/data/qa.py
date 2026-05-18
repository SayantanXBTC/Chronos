"""QA checks for historical territory data using live PostGIS queries.

Run via CLI:
    python -m data qa --check-overlaps
    python -m data qa --invalid-geoms
    python -m data qa --temporal-gaps
"""
from __future__ import annotations

from typing import Any


def check_overlaps(conn, threshold: float = 0.5) -> list[dict]:
    """Find territory pairs of DIFFERENT entities with overlapping years AND
    intersecting geometries where overlap area / smaller area > threshold.

    Returns list of dicts: {entity_a, entity_b, year_overlap_start, year_overlap_end,
                            overlap_fraction, territory_a_id, territory_b_id}

    SQL approach: self-join territories on year overlap + ST_Intersects,
    compute ST_Area(ST_Intersection) / ST_Area(smaller), filter by threshold.
    """
    sql = """
        SELECT
            ea.slug        AS entity_a,
            eb.slug        AS entity_b,
            GREATEST(ta.year_start, tb.year_start)  AS year_overlap_start,
            LEAST(
                COALESCE(ta.year_end, 9999),
                COALESCE(tb.year_end, 9999)
            )                                        AS year_overlap_end,
            ST_Area(ST_Intersection(ta.geom, tb.geom)) /
                NULLIF(
                    LEAST(ST_Area(ta.geom), ST_Area(tb.geom)),
                    0
                )                                    AS overlap_fraction,
            ta.id          AS territory_a_id,
            tb.id          AS territory_b_id
        FROM territories ta
        JOIN entities ea ON ea.id = ta.entity_id
        JOIN territories tb ON tb.id > ta.id
        JOIN entities eb ON eb.id = tb.entity_id
        WHERE
            ea.id <> eb.id
            -- Year overlap: max(start) < min(end)
            AND ta.year_start < COALESCE(tb.year_end, 9999)
            AND tb.year_start < COALESCE(ta.year_end, 9999)
            -- Spatial overlap (fast filter)
            AND ST_Intersects(ta.geom, tb.geom)
            -- Area-fraction filter
            AND (
                ST_Area(ST_Intersection(ta.geom, tb.geom)) /
                NULLIF(LEAST(ST_Area(ta.geom), ST_Area(tb.geom)), 0)
            ) > %(threshold)s
        ORDER BY overlap_fraction DESC NULLS LAST
    """
    with conn.cursor() as cur:
        cur.execute(sql, {'threshold': threshold})
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def check_invalid_geoms(conn) -> list[dict]:
    """Find territories where ST_IsValid(geom) = false.
    Returns list of {entity_slug, territory_id, year_start, year_end}.
    """
    sql = """
        SELECT
            e.slug      AS entity_slug,
            t.id        AS territory_id,
            t.year_start,
            t.year_end
        FROM territories t
        JOIN entities e ON e.id = t.entity_id
        WHERE NOT ST_IsValid(t.geom)
        ORDER BY e.slug, t.year_start
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def check_temporal_gaps(conn) -> list[dict]:
    """Find entities where there is a gap between consecutive territory phases.
    Gap = max(year_end of phase N) < min(year_start of phase N+1).
    Returns list of {entity_slug, gap_start, gap_end, gap_years}.
    """
    sql = """
        WITH ordered AS (
            SELECT
                e.slug                          AS entity_slug,
                t.year_start,
                t.year_end,
                LEAD(t.year_start) OVER (
                    PARTITION BY t.entity_id
                    ORDER BY t.year_start
                )                               AS next_year_start
            FROM territories t
            JOIN entities e ON e.id = t.entity_id
            WHERE t.year_end IS NOT NULL
        )
        SELECT
            entity_slug,
            year_end                            AS gap_start,
            next_year_start                     AS gap_end,
            next_year_start - year_end          AS gap_years
        FROM ordered
        WHERE next_year_start IS NOT NULL
          AND next_year_start > year_end
        ORDER BY entity_slug, gap_start
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
