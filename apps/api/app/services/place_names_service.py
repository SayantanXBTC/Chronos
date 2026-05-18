from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

PLACE_NAMES_SQL = text("""
    SELECT
        name,
        name_modern,
        name_local,
        type,
        importance,
        label_priority,
        date_precision,
        ST_AsGeoJSON(geom)::json AS geometry
    FROM place_names
    WHERE
        year_start <= :year
        AND (year_end IS NULL OR year_end > :year)
        AND min_zoom <= :zoom
        AND importance >= :min_importance
        AND geom && ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 4326)
    ORDER BY importance DESC
""")


class PlaceNamesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _min_importance(self, zoom: int) -> int:
        if zoom <= 3:
            return 8
        if zoom <= 5:
            return 6
        return 4

    async def get_place_names(
        self,
        year: int,
        bbox: tuple[float, float, float, float],
        zoom: int,
    ) -> dict[str, Any]:
        min_x, min_y, max_x, max_y = bbox
        rows = await self.db.execute(
            PLACE_NAMES_SQL,
            {
                "year": year,
                "zoom": zoom,
                "min_importance": self._min_importance(zoom),
                "min_x": min_x,
                "min_y": min_y,
                "max_x": max_x,
                "max_y": max_y,
            },
        )
        features = []
        for row in rows.mappings().all():
            features.append({
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "name": row["name"],
                    "name_modern": row["name_modern"],
                    "name_local": row["name_local"],
                    "type": row["type"],
                    "importance": row["importance"],
                    "label_priority": row["label_priority"],
                    "date_precision": row["date_precision"],
                },
            })
        return {"type": "FeatureCollection", "features": features}
