from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

RIVERS_SQL = text("""
    SELECT
        name,
        name_alt,
        importance,
        ST_AsGeoJSON(geom)::json AS geometry
    FROM rivers
    ORDER BY importance DESC
""")


class RiversService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rivers(self) -> dict[str, Any]:
        rows = await self.db.execute(RIVERS_SQL)
        features = []
        for row in rows.mappings().all():
            features.append({
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "name": row["name"],
                    "name_alt": row["name_alt"],
                    "importance": row["importance"],
                },
            })
        return {"type": "FeatureCollection", "features": features}
