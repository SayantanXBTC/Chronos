import uuid

import psycopg2.extensions


class Loader:
    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self.conn = conn

    def upsert_entity(self, slug: str, entity_type: str, color: str) -> str:
        with self.conn.cursor() as cur:
            entity_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO entities (id, slug, type, color)
                VALUES (%s::uuid, %s, %s, %s)
                ON CONFLICT (slug) DO UPDATE
                    SET type = EXCLUDED.type, color = EXCLUDED.color
                RETURNING id::text
                """,
                (entity_id, slug, entity_type, color),
            )
            return cur.fetchone()[0]

    def upsert_entity_name(
        self, entity_id: str, name: str, year_start: int, year_end: int | None
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM entity_names WHERE entity_id = %s::uuid",
                (entity_id,),
            )
            cur.execute(
                """
                INSERT INTO entity_names (id, entity_id, name, language, year_start, year_end, is_primary)
                VALUES (%s::uuid, %s::uuid, %s, 'en', %s, %s, true)
                """,
                (str(uuid.uuid4()), entity_id, name, year_start, year_end),
            )

    def delete_territories(self, entity_id: str) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM territories WHERE entity_id = %s::uuid",
                (entity_id,),
            )
            return cur.rowcount

    def insert_territory(
        self,
        entity_id: str,
        geom_wkt: str,
        simplified_wkt: str,
        year_start: int,
        year_end: int | None,
        confidence_type: str = "approximate",
        confidence_score: float | None = None,
        source_name: str | None = None,
        source_url: str | None = None,
        source_license: str | None = None,
        data_version: str | None = None,
        resolution_km: int | None = None,
        importance: int = 5,
        map_modes: list[str] | None = None,
    ) -> None:
        if map_modes is None:
            map_modes = ["political"]
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO territories (
                    id, entity_id, geom, simplified_geom,
                    year_start, year_end,
                    confidence_type, confidence_score,
                    source_name, source_url, source_license, data_version,
                    resolution_km, importance, map_modes
                )
                VALUES (
                    %s::uuid, %s::uuid,
                    ST_Multi(ST_GeomFromText(%s, 4326)),
                    ST_Multi(ST_GeomFromText(%s, 4326)),
                    %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
                """,
                (
                    str(uuid.uuid4()),
                    entity_id,
                    geom_wkt,
                    simplified_wkt,
                    year_start,
                    year_end,
                    confidence_type,
                    confidence_score,
                    source_name,
                    source_url,
                    source_license,
                    data_version,
                    resolution_km,
                    importance,
                    map_modes,
                ),
            )
