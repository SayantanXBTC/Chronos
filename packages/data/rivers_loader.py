"""Load river LineString data from GeoJSON into the rivers table."""
import json
import uuid
from pathlib import Path

import psycopg2.extensions
from shapely.geometry import shape, LineString, MultiLineString
from shapely.validation import make_valid

_REPO_ROOT = Path(__file__).parent.parent.parent
RIVERS_GEOJSON = _REPO_ROOT / "data" / "raw" / "physical" / "rivers.geojson"


def _to_linestring(geom) -> LineString:
    if isinstance(geom, LineString):
        return geom
    if isinstance(geom, MultiLineString):
        coords = []
        for line in geom.geoms:
            coords.extend(line.coords)
        return LineString(coords)
    raise ValueError(f"Cannot convert {geom.geom_type} to LineString")


def load_rivers(conn: psycopg2.extensions.connection, geojson_path: Path | None = None) -> int:
    path = geojson_path or RIVERS_GEOJSON
    if not path.exists():
        raise FileNotFoundError(f"Rivers GeoJSON not found: {path}")

    with open(path) as f:
        fc = json.load(f)

    loaded = 0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM rivers")
        for feat in fc.get("features", []):
            props = feat.get("properties", {}) or {}
            try:
                raw_geom = shape(feat["geometry"])
                if not raw_geom.is_valid:
                    raw_geom = make_valid(raw_geom)
                line = _to_linestring(raw_geom)
                cur.execute(
                    """
                    INSERT INTO rivers
                        (id, name, name_alt, geom, year_start, year_end,
                         importance, source_name, map_modes)
                    VALUES (
                        %s::uuid, %s, %s,
                        ST_GeomFromText(%s, 4326),
                        %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        str(uuid.uuid4()),
                        props.get("name", "Unknown"),
                        props.get("name_alt"),
                        line.wkt,
                        props.get("year_start"),
                        props.get("year_end"),
                        int(props.get("importance", 5)),
                        props.get("source_name", "Natural Earth"),
                        ["political", "physical", "trade", "migration", "military"],
                    ),
                )
                loaded += 1
            except Exception as e:
                print(f"  WARNING: skipped river {props.get('name', '?')}: {e}")
    conn.commit()
    return loaded


if __name__ == "__main__":
    import os
    import psycopg2

    db_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    conn = psycopg2.connect(db_url)
    n = load_rivers(conn)
    conn.close()
    print(f"Loaded {n} rivers")
