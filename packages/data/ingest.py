"""
Data ingestion CLI.
Usage: python -m data.ingest [--source manual]
"""
import argparse
import asyncio
import json
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data.normalize import fix_geometry, simplify_geometry, to_multipolygon
from data.sources.base import EntityRecord, TerritoryRecord
from data.sources.manual import ManualSource

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://history:history@localhost:5432/history"
)


async def upsert_entity(session: AsyncSession, rec: EntityRecord) -> uuid.UUID:
    result = await session.execute(
        text("SELECT id FROM entities WHERE slug = :slug"), {"slug": rec.slug}
    )
    row = result.fetchone()
    if row:
        entity_id = uuid.UUID(str(row[0]))
    else:
        entity_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO entities (id, slug, type, color) "
                "VALUES (:id, :slug, :type, :color)"
            ),
            {"id": str(entity_id), "slug": rec.slug, "type": rec.type, "color": rec.color},
        )

    await session.execute(
        text("DELETE FROM entity_names WHERE entity_id = :eid"),
        {"eid": str(entity_id)},
    )
    for name in rec.names:
        await session.execute(
            text(
                "INSERT INTO entity_names "
                "(id, entity_id, name, language, year_start, year_end, is_primary) "
                "VALUES (:id, :eid, :name, :lang, :ys, :ye, :primary)"
            ),
            {
                "id": str(uuid.uuid4()),
                "eid": str(entity_id),
                "name": name["name"],
                "lang": name["language"],
                "ys": name["year_start"],
                "ye": name.get("year_end"),
                "primary": name["is_primary"],
            },
        )
    return entity_id


async def upsert_territory(
    session: AsyncSession, rec: TerritoryRecord, entity_id: uuid.UUID
) -> None:
    await session.execute(
        text(
            "DELETE FROM territories WHERE entity_id = :eid AND year_start = :ys"
        ),
        {"eid": str(entity_id), "ys": rec.year_start},
    )

    try:
        geom = to_multipolygon(rec.geojson)
    except Exception as e:
        print(f"    Warning: to_multipolygon failed ({e}), attempting fix_geometry")
        geom = fix_geometry(rec.geojson)

    try:
        simplified = simplify_geometry(geom, tolerance=0.1)
    except Exception:
        simplified = geom

    geom_json = json.dumps(geom)
    simplified_json = json.dumps(simplified)

    await session.execute(
        text(
            "INSERT INTO territories "
            "(id, entity_id, geom, simplified_geom, year_start, year_end, confidence, source) "
            "VALUES (:id, :eid, "
            "ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326), "
            "ST_SetSRID(ST_GeomFromGeoJSON(:simplified), 4326), "
            ":ys, :ye, :conf, :src)"
        ),
        {
            "id": str(uuid.uuid4()),
            "eid": str(entity_id),
            "geom": geom_json,
            "simplified": simplified_json,
            "ys": rec.year_start,
            "ye": rec.year_end,
            "conf": rec.confidence,
            "src": rec.source,
        },
    )


async def seed_layers(session: AsyncSession) -> None:
    layers = [
        ("political", "Political Borders", True),
        ("religious", "Religious Influence", False),
        ("trade_routes", "Trade Routes", False),
        ("military", "Military Campaigns", False),
        ("linguistic", "Linguistic Groups", False),
        ("migration", "Migration Patterns", False),
    ]
    for layer_id, display_name, active in layers:
        await session.execute(
            text(
                "INSERT INTO layers (id, display_name, active) "
                "VALUES (:id, :name, :active) "
                "ON CONFLICT (id) DO UPDATE SET display_name = EXCLUDED.display_name, active = EXCLUDED.active"
            ),
            {"id": layer_id, "name": display_name, "active": active},
        )


async def run_ingest(source_name: str = "manual") -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    if source_name not in ("manual",):
        await engine.dispose()
        raise ValueError(f"Unknown source: {source_name}")

    if source_name == "manual":
        source = ManualSource()

    try:
        async with Session() as session:
            async with session.begin():
                print("Seeding layers...")
                await seed_layers(session)

                for entity_rec in source.get_entities():
                    print(f"  Upserting entity: {entity_rec.slug}")
                    entity_id = await upsert_entity(session, entity_rec)

                    for territory_rec in source.get_territories():
                        if territory_rec.entity_slug == entity_rec.slug:
                            print(
                                f"    Upserting territory: "
                                f"{entity_rec.slug} {territory_rec.year_start}"
                            )
                            await upsert_territory(session, territory_rec, entity_id)
    finally:
        await engine.dispose()

    print("Ingestion complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="manual")
    args = parser.parse_args()
    asyncio.run(run_ingest(args.source))
