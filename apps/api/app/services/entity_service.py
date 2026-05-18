from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_DETAIL_SQL = text("""
    SELECT
        e.id::text              AS entity_id,
        e.slug,
        e.type,
        e.color,
        en.name,
        MIN(t.year_start)       AS year_start,
        MAX(t.year_end)         AS year_end,
        MAX(t.source_name)      AS source_name,
        MAX(t.confidence_type)  AS confidence_type,
        MAX(COALESCE(t.importance, 5)) AS importance
    FROM entities e
    JOIN entity_names en ON en.entity_id = e.id AND en.is_primary = true
    JOIN territories t ON t.entity_id = e.id
    WHERE e.slug = :slug
    GROUP BY e.id, e.slug, e.type, e.color, en.name
    ORDER BY en.year_start DESC
    LIMIT 1
""")

_PREDECESSORS_SQL = text("""
    SELECT
        pe.slug,
        pen.name,
        el.relationship_type,
        el.year,
        el.notes
    FROM entity_lineages el
    JOIN entities pe ON pe.id = el.parent_entity_id
    JOIN (
        SELECT DISTINCT ON (entity_id) entity_id, name
        FROM entity_names
        WHERE is_primary = true
        ORDER BY entity_id, year_start DESC
    ) pen ON pen.entity_id = pe.id
    WHERE el.child_entity_id = :entity_id
    ORDER BY el.year
""")

_SUCCESSORS_SQL = text("""
    SELECT
        ce.slug,
        cen.name,
        el.relationship_type,
        el.year,
        el.notes
    FROM entity_lineages el
    JOIN entities ce ON ce.id = el.child_entity_id
    JOIN (
        SELECT DISTINCT ON (entity_id) entity_id, name
        FROM entity_names
        WHERE is_primary = true
        ORDER BY entity_id, year_start DESC
    ) cen ON cen.entity_id = ce.id
    WHERE el.parent_entity_id = :entity_id
    ORDER BY el.year
""")


class EntityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entity_detail(self, slug: str) -> dict[str, Any] | None:
        row_result = await self.db.execute(_ENTITY_DETAIL_SQL, {"slug": slug})
        row = row_result.mappings().first()
        if row is None:
            return None

        entity_id = row["entity_id"]

        pred_result = await self.db.execute(_PREDECESSORS_SQL, {"entity_id": entity_id})
        predecessors = [
            {
                "slug": r["slug"],
                "name": r["name"],
                "relationship_type": r["relationship_type"],
                "year": r["year"],
                "notes": r["notes"],
            }
            for r in pred_result.mappings().all()
        ]

        succ_result = await self.db.execute(_SUCCESSORS_SQL, {"entity_id": entity_id})
        successors = [
            {
                "slug": r["slug"],
                "name": r["name"],
                "relationship_type": r["relationship_type"],
                "year": r["year"],
                "notes": r["notes"],
            }
            for r in succ_result.mappings().all()
        ]

        return {
            "slug": row["slug"],
            "name": row["name"],
            "type": row["type"],
            "color": row["color"],
            "year_start": row["year_start"],
            "year_end": row["year_end"],
            "source_name": row["source_name"],
            "confidence_type": row["confidence_type"],
            "importance": row["importance"],
            "lineage": {
                "predecessors": predecessors,
                "successors": successors,
            },
        }
