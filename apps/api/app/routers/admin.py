"""Admin/debug endpoints for geometry stats, system stats, and region coverage."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return entity, territory, place_name, and lineage counts."""
    rows = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM entities)          AS entities,
            (SELECT COUNT(*) FROM territories)       AS territories,
            (SELECT COUNT(*) FROM place_names)       AS place_names,
            (SELECT COUNT(*) FROM entity_lineages)   AS lineages
    """))
    row = rows.mappings().one()
    regions = await db.execute(text("""
        SELECT DISTINCT region_name FROM region_coverage ORDER BY region_name
    """))
    region_list = [r["region_name"] for r in regions.mappings().all()]
    return {
        "entities": row["entities"],
        "territories": row["territories"],
        "place_names": row["place_names"],
        "lineages": row["lineages"],
        "regions": region_list,
    }


@router.get("/geometry-stats")
async def get_geometry_stats(
    entity_slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return geometry vertex counts and area for all territories of an entity."""
    rows = await db.execute(
        text("""
            SELECT
                t.year_start,
                t.year_end,
                ST_NPoints(t.geom)     AS geom_vertices,
                ST_NPoints(t.geom_lo)  AS geom_lo_vertices,
                ST_Area(t.geom::geography) / 1e6 AS area_km2,
                ST_IsValid(t.geom)     AS geom_valid
            FROM territories t
            JOIN entities e ON e.id = t.entity_id
            WHERE e.slug = :slug
            ORDER BY t.year_start
        """),
        {"slug": entity_slug},
    )
    records = []
    for r in rows.mappings().all():
        records.append({
            "year_start": r["year_start"],
            "year_end": r["year_end"],
            "geom_vertices": r["geom_vertices"],
            "geom_lo_vertices": r["geom_lo_vertices"],
            "area_km2": round(float(r["area_km2"]), 1) if r["area_km2"] else None,
            "geom_valid": r["geom_valid"],
        })
    return {"entity_slug": entity_slug, "territories": records}


@router.get("/coverage")
async def get_coverage(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return region_coverage table as JSON."""
    rows = await db.execute(text("""
        SELECT region_name, year_start, year_end, completeness, entity_count, primary_source, notes
        FROM region_coverage
        ORDER BY region_name
    """))
    records = [dict(r) for r in rows.mappings().all()]
    return {"regions": records}
