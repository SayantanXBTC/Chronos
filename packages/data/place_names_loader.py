"""Load historical city/settlement data from CSV into the place_names table."""
import csv
import uuid
from pathlib import Path
import psycopg2.extensions

_REPO_ROOT = Path(__file__).parent.parent.parent
CITIES_CSV = _REPO_ROOT / "data" / "raw" / "place_names" / "ancient_cities.csv"


def load_place_names(conn: psycopg2.extensions.connection, csv_path: Path | None = None) -> int:
    path = csv_path or CITIES_CSV
    if not path.exists():
        raise FileNotFoundError(f"Cities CSV not found: {path}")

    loaded = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM place_names")
            for row in reader:
                try:
                    lon = float(row["lon"])
                    lat = float(row["lat"])
                    year_start = int(row["year_start"])
                    year_end = int(row["year_end"]) if row.get("year_end") else None
                    importance = int(row.get("importance", 5))
                    label_priority = int(row.get("label_priority", importance))
                    min_zoom = int(row.get("min_zoom", 3))
                    name_local = row.get("name_local") or None
                    date_precision = row.get("date_precision") or "approximate"
                    cur.execute(
                        """
                        INSERT INTO place_names
                            (id, name, name_modern, name_local, type, geom,
                             year_start, year_end, min_zoom,
                             source_name, importance, label_priority,
                             date_precision, map_modes)
                        VALUES (
                            %s::uuid, %s, %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            str(uuid.uuid4()),
                            row["name"],
                            row.get("name_modern") or None,
                            name_local,
                            row.get("type", "city"),
                            lon,
                            lat,
                            year_start,
                            year_end,
                            min_zoom,
                            row.get("source_name", "Ancient World Mapping Center"),
                            importance,
                            label_priority,
                            date_precision,
                            ["political"],
                        ),
                    )
                    loaded += 1
                except Exception as e:
                    print(f"  WARNING: skipped row {row.get('name', '?')}: {e}")
    conn.commit()
    return loaded


if __name__ == "__main__":
    import os
    import psycopg2

    db_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    conn = psycopg2.connect(db_url)
    n = load_place_names(conn)
    conn.close()
    print(f"Loaded {n} place names")
