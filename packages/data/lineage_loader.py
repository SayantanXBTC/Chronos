"""lineage_loader.py — load entity lineage relationships from YAML into the DB."""
from pathlib import Path

import yaml


def load_lineages_from_yaml(yaml_path: Path) -> list[dict]:
    """Parse lineages YAML. Returns list of dicts with keys:
    parent_slug, child_slug, relationship_type, year, notes (optional)."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    lineages = data.get("lineages") or []
    result = []
    for entry in lineages:
        row: dict = {
            "parent_slug": entry["parent"],
            "child_slug": entry["child"],
            "relationship_type": entry["relationship"],
            "year": entry["year"],
        }
        if "notes" in entry and entry["notes"] is not None:
            row["notes"] = entry["notes"]
        result.append(row)
    return result


def resolve_slugs(conn, slugs: list[str]) -> dict[str, str]:
    """Query DB for entity UUIDs. Returns {slug: uuid_str}.
    Raises ValueError if any slug not found."""
    if not slugs:
        return {}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT slug, id::text FROM entities WHERE slug = ANY(%s)",
            (list(slugs),),
        )
        rows = cur.fetchall()

    found = {row[0]: row[1] for row in rows}
    missing = [s for s in slugs if s not in found]
    if missing:
        raise ValueError(f"Entity slug(s) not found in DB: {', '.join(missing)}")
    return found


def upsert_lineages(conn, lineages: list[dict]) -> int:
    """Bulk upsert lineages into entity_lineages table.
    Resolves slugs to UUIDs. Idempotent via ON CONFLICT DO NOTHING.
    Returns count of rows inserted (not updated)."""
    if not lineages:
        return 0

    all_slugs = set()
    for row in lineages:
        all_slugs.add(row["parent_slug"])
        all_slugs.add(row["child_slug"])

    slug_map = resolve_slugs(conn, list(all_slugs))

    inserted = 0
    with conn.cursor() as cur:
        for row in lineages:
            parent_id = slug_map[row["parent_slug"]]
            child_id = slug_map[row["child_slug"]]
            notes = row.get("notes")
            cur.execute(
                """
                INSERT INTO entity_lineages
                    (parent_entity_id, child_entity_id, relationship_type, year, notes)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (parent_id, child_id, row["relationship_type"], row["year"], notes),
            )
            inserted += cur.rowcount

    return inserted
