from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SOURCES_SQL = text("""
    SELECT id::text, slug, name, url, license, description, year_min, year_max, coverage
    FROM data_sources
    ORDER BY name
""")


class SourcesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sources(self) -> list[dict[str, Any]]:
        rows = await self.db.execute(SOURCES_SQL)
        return [dict(row) for row in rows.mappings().all()]
