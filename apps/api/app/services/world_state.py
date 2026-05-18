from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.year import snap_to_snapshot

SNAPSHOT_YEARS: list[int] = [y for y in range(-500, 501, 25) if y != 0]

WORLD_STATE_SQL = text("""
    SELECT
        e.id::text              AS entity_id,
        e.slug                  AS slug,
        e.type                  AS type,
        e.color                 AS color,
        en.name                 AS name,
        t.confidence_type       AS confidence_type,
        t.source_name           AS source_name,
        COALESCE(t.importance, 5) AS importance,
        ST_AsGeoJSON(
            CASE WHEN :zoom < 7 THEN t.simplified_geom ELSE t.geom END
        )::json                 AS geometry
    FROM territories t
    JOIN entities e ON t.entity_id = e.id
    JOIN entity_names en
        ON en.entity_id = e.id
        AND en.year_start <= :year
        AND (en.year_end IS NULL OR en.year_end > :year)
        AND en.is_primary = true
    WHERE
        t.year_start <= :year
        AND (t.year_end IS NULL OR t.year_end > :year)
        AND t.geom && ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 4326)
    ORDER BY e.slug
""")


class WorldStateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_state(
        self,
        year: int,
        bbox: tuple[float, float, float, float],
        zoom: int,
        layer: str = "political",
    ) -> dict[str, Any]:
        min_x, min_y, max_x, max_y = bbox

        rows = await self.db.execute(
            WORLD_STATE_SQL,
            {
                "year": year,
                "zoom": zoom,
                "min_x": min_x,
                "min_y": min_y,
                "max_x": max_x,
                "max_y": max_y,
            },
        )

        features: list[dict[str, Any]] = []
        for row in rows.mappings().all():
            features.append({
                "type": "Feature",
                "id": row["slug"],
                "geometry": row["geometry"],
                "properties": {
                    "entity_id": row["entity_id"],
                    "slug": row["slug"],
                    "name": row["name"],
                    "type": row["type"],
                    "color": row["color"],
                    "confidence": row["confidence_type"],
                    "confidence_type": row["confidence_type"],
                    "source_name": row["source_name"],
                    "importance": row["importance"],
                },
            })

        return {
            "type": "FeatureCollection",
            "year": year,
            "snapshot_year": snap_to_snapshot(year, SNAPSHOT_YEARS),
            "features": features,
        }
