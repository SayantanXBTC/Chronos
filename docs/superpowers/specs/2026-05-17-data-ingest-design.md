# Data Ingest Pipeline — Design Spec

**Date:** 2026-05-17
**Scope:** Build a CLI pipeline that loads 13 Mediterranean civilizations with phase-based temporal territories into PostGIS, enabling the timeline slider to show meaningful territorial changes from 500 BCE to 500 CE.

---

## Goal

Populate the `entities`, `entity_names`, and `territories` tables with real historical data for 13 civilizations covering the Mediterranean world (-500 to +500 CE). Each civilization has 1–5 territorial phases (different polygons for different historical periods), enabling the slider to show Rome growing, Persia fragmenting, etc.

---

## Architecture

**Approach:** Config-driven entity registry with bundled GeoJSON geometry files.

- Each entity defined in a YAML config file in `packages/data/entities/`
- Each territorial phase references a GeoJSON file in `data/raw/political/<slug>/`
- Pipeline reads all configs + geometries, normalizes, bulk-inserts into PostGIS
- Idempotent: re-running clears and re-inserts territories for affected entities

**Package location:** `packages/data/` — standalone Python package, separate from the API. Uses sync `psycopg2-binary` (no async complexity in a one-shot CLI).

---

## File Structure

```
packages/data/
├── pyproject.toml
├── __init__.py
├── __main__.py          # entry point: python -m data
├── ingest.py            # orchestrator
├── loader.py            # DB upsert logic (psycopg2)
├── normalize.py         # Shapely geometry normalization
├── entities/            # YAML config per entity (13 files)
│   ├── roman-republic.yml
│   ├── roman-empire.yml
│   ├── western-roman-empire.yml
│   ├── eastern-roman-empire.yml
│   ├── achaemenid-persia.yml
│   ├── macedonian-empire.yml
│   ├── seleucid-empire.yml
│   ├── ptolemaic-egypt.yml
│   ├── parthian-empire.yml
│   ├── carthage.yml
│   ├── greek-city-states.yml
│   ├── numidia.yml
│   └── germanic-tribes.yml
└── tests/
    ├── conftest.py
    ├── test_normalize.py
    ├── test_loader.py
    └── test_ingest.py   # integration test against test DB

data/raw/political/      # GeoJSON geometry files (version-controlled)
├── roman-republic/
│   ├── phase-1.geojson  # Italian peninsula, -500 to -264
│   ├── phase-2.geojson  # W. Mediterranean, -264 to -100
│   └── phase-3.geojson  # Full Mediterranean, -100 to -27
├── roman-empire/
│   ├── phase-1.geojson  # Augustan consolidation, -27 to 14
│   ├── phase-2.geojson  # High Empire peak, 14 to 180
│   ├── phase-3.geojson  # Crisis period, 180 to 284
│   └── phase-4.geojson  # Late Empire, 284 to 395
├── western-roman-empire/
│   └── phase-1.geojson  # 395 to 476
├── eastern-roman-empire/
│   └── phase-1.geojson  # 395 to 1453 (full Byzantine span)
├── achaemenid-persia/
│   ├── phase-1.geojson  # Full extent, -500 to -400
│   └── phase-2.geojson  # Contraction, -400 to -330
├── macedonian-empire/
│   ├── phase-1.geojson  # Macedon only, -500 to -336
│   └── phase-2.geojson  # Alexander's empire, -336 to -301
├── seleucid-empire/
│   ├── phase-1.geojson  # Large successor, -301 to -200
│   ├── phase-2.geojson  # Fragmented, -200 to -100
│   └── phase-3.geojson  # Rump Syria, -100 to -63
├── ptolemaic-egypt/
│   ├── phase-1.geojson  # Egypt + Cyprus + Cyrene, -305 to -200
│   └── phase-2.geojson  # Egypt core, -200 to -30
├── parthian-empire/
│   ├── phase-1.geojson  # Early Parthia, -247 to -100
│   └── phase-2.geojson  # Peak Parthia, -100 to 224
├── carthage/
│   ├── phase-1.geojson  # N.Africa + Spain + Sicily, -500 to -264
│   └── phase-2.geojson  # N.Africa + Spain (post First Punic), -264 to -146
├── greek-city-states/
│   └── phase-1.geojson  # Aegean sphere, -500 to -338
├── numidia/
│   └── phase-1.geojson  # N.Africa, -202 to 46
└── germanic-tribes/
    └── phase-1.geojson  # N.Europe, 200 to 500
```

---

## Entity Config Format

```yaml
# packages/data/entities/roman-republic.yml
slug: roman-republic
name: Roman Republic
type: polity
color: "#c0392b"
phases:
  - geometry: roman-republic/phase-1.geojson
    year_start: -500
    year_end: -264
    confidence: approximate
  - geometry: roman-republic/phase-2.geojson
    year_start: -264
    year_end: -100
    confidence: approximate
  - geometry: roman-republic/phase-3.geojson
    year_start: -100
    year_end: -27
    confidence: approximate
```

`geometry` paths are relative to `data/raw/political/`. `year_start`/`year_end` define the territory row's temporal range (negative = BCE, no year 0, consistent with app convention).

---

## Entity Catalog

| Slug | Name | Color | Year Start | Year End | Phases |
|------|------|-------|-----------|---------|--------|
| `roman-republic` | Roman Republic | `#c0392b` | -500 | -27 | 3 |
| `roman-empire` | Roman Empire | `#e74c3c` | -27 | 395 | 4 |
| `western-roman-empire` | Western Roman Empire | `#e67e22` | 395 | 476 | 1 |
| `eastern-roman-empire` | Eastern Roman Empire | `#9b59b6` | 395 | 1453 | 1 |
| `achaemenid-persia` | Achaemenid Persian Empire | `#f39c12` | -500 | -330 | 2 |
| `macedonian-empire` | Macedonian Empire | `#3498db` | -500 | -301 | 2 |
| `seleucid-empire` | Seleucid Empire | `#2980b9` | -301 | -63 | 3 |
| `ptolemaic-egypt` | Ptolemaic Egypt | `#27ae60` | -305 | -30 | 2 |
| `parthian-empire` | Parthian Empire | `#16a085` | -247 | 224 | 2 |
| `carthage` | Carthage | `#8e44ad` | -500 | -146 | 2 |
| `greek-city-states` | Greek City-States | `#2ecc71` | -500 | -338 | 1 |
| `numidia` | Numidia | `#d35400` | -202 | 46 | 1 |
| `germanic-tribes` | Germanic Tribes | `#7f8c8d` | 200 | 500 | 1 |

Total: 13 entities, ~30 GeoJSON phase files.

---

## Pipeline Flow

```
python -m data [--entity <slug>] [--dry-run]
```

Per entity:
1. Load YAML config
2. Upsert `entities` row (slug, type, color) — ON CONFLICT DO UPDATE
3. Upsert `entity_names` row (name, language=en, year_start, year_end, is_primary=true)
4. DELETE existing `territories` rows for this entity (idempotent)
5. For each phase:
   a. Load GeoJSON file from `data/raw/political/<path>`
   b. Parse geometry with `shapely.geometry.shape()`
   c. Wrap Polygon → MultiPolygon if needed
   d. Validate: `geom.is_valid` — skip phase with warning if invalid
   e. Simplify: `geom.simplify(0.05, preserve_topology=True)` → `simplified_geom`
   f. Convert to WKT, INSERT territory row
6. Print per-entity summary (phases loaded / skipped)

`--dry-run`: validate all configs + GeoJSON files, print what would be inserted, exit without DB writes.

`--entity <slug>`: process only the named entity. Useful for iterating on a single entity's geometry.

---

## Normalization (`normalize.py`)

```python
def to_multipolygon(geom: BaseGeometry) -> MultiPolygon
def simplify_geom(geom: MultiPolygon, tolerance: float = 0.05) -> MultiPolygon
def validate_geom(geom: BaseGeometry) -> bool
```

- `to_multipolygon`: if input is Polygon, wrap in MultiPolygon. If GeometryCollection, extract Polygons. Raise ValueError for non-polygon types.
- `simplify_geom`: `geom.simplify(tolerance, preserve_topology=True)`. Returns simplified MultiPolygon.
- `validate_geom`: returns `geom.is_valid`. Caller logs warning and skips on False.

---

## Loader (`loader.py`)

Uses `psycopg2-binary` (sync, no async). Reads `DATABASE_URL` from env, strips `+asyncpg` prefix if present.

```python
class Loader:
    def __init__(self, conn): ...
    def upsert_entity(self, slug, type, color) -> str  # returns entity_id (UUID)
    def upsert_entity_name(self, entity_id, name, year_start, year_end) -> None
    def delete_territories(self, entity_id) -> int  # returns deleted count
    def insert_territory(self, entity_id, geom_wkt, simplified_wkt,
                         year_start, year_end, confidence) -> None
```

All methods operate within a single transaction per entity (commit after all phases inserted, rollback on error).

---

## GeoJSON Data Files

All ~30 GeoJSON files created as part of this milestone. Geometries are approximate polygon coordinates derived from standard historical atlas boundaries (Barrington Atlas, AWMC reference maps). Accuracy appropriate for zoom 2–4 visualization (not sub-region precision).

Each file is a single GeoJSON `Feature` with a `MultiPolygon` geometry:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [[[[...]]]]
  },
  "properties": {}
}
```

CRS: WGS84 (EPSG:4326). Coordinates as [longitude, latitude].

---

## Testing

**`test_normalize.py`** (unit, no DB):
- Polygon input → MultiPolygon output
- MultiPolygon passthrough unchanged
- Invalid geometry → `validate_geom` returns False
- Simplification reduces vertex count

**`test_loader.py`** (unit, mock psycopg2):
- `upsert_entity` executes correct INSERT ON CONFLICT SQL
- `delete_territories` executes DELETE WHERE entity_id
- `insert_territory` passes WKT to ST_GeomFromText with correct SRID

**`test_ingest.py`** (integration, test DB from `infra/docker-compose.test.yml`):
- Run full ingest for 2 entities
- Query DB: assert correct entity count, territory count, year ranges
- Run again: assert idempotent (same counts, no duplicates)

---

## Dependencies (`packages/data/pyproject.toml`)

```toml
[project]
name = "history-data"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "shapely>=2.0",
    "pyyaml>=6.0",
    "psycopg2-binary>=2.9",
]
```

No GeoPandas/Fiona needed for GeoJSON loading — `json` + `shapely` is sufficient.

---

## Running the Pipeline

The pipeline runs **locally** (not inside Docker) against the exposed postgres port. Install the package first:

```bash
pip install -e packages/data
```

Then run with `DATABASE_URL` pointing to localhost:

```bash
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --entity roman-republic
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run
```

**Makefile targets** (adds `DATABASE_URL` automatically from `.env`):

```makefile
seed:
    export $(shell cat .env | xargs) && python -m data

seed-entity:
    export $(shell cat .env | xargs) && python -m data --entity $(ENTITY)

seed-dry:
    export $(shell cat .env | xargs) && python -m data --dry-run
```

Run after `make migrate`. Requires Docker stack running (`make dev`) so postgres is reachable on port 5432.

---

## Out of Scope

- AWMC shapefile download automation (manual data preparation)
- Events, routes, cities (separate layer)
- Neo4j entity relationship loading
- Snapshot precomputation to disk (API serves live from DB)
- Data beyond 500 CE (app slider range)
