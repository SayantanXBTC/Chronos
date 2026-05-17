# Data Ingest Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI pipeline (`python -m data`) that loads 13 Mediterranean civilizations with phase-based territorial polygons into PostGIS, enabling the timeline slider to show real historical territorial change from 500 BCE to 500 CE.

**Architecture:** `packages/data/` standalone Python package. Each entity defined in a YAML config file. Each territorial phase references a GeoJSON file in `data/raw/political/`. Pipeline reads configs + geometries, normalizes with Shapely, bulk-inserts into PostGIS via psycopg2. Idempotent: DELETE + re-INSERT territories per entity on each run.

**Tech Stack:** Python 3.12, Shapely 2.x, PyYAML, psycopg2-binary, pytest. No GeoPandas — GeoJSON loaded with stdlib `json` + Shapely.

---

## File Map

```
packages/data/
├── pyproject.toml
├── __init__.py
├── __main__.py
├── ingest.py
├── loader.py
├── normalize.py
├── entities/
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
    └── test_ingest.py

data/raw/political/
├── roman-republic/phase-1.geojson  (-500 to -264)
├── roman-republic/phase-2.geojson  (-264 to -100)
├── roman-republic/phase-3.geojson  (-100 to -27)
├── roman-empire/phase-1.geojson    (-27 to 14)
├── roman-empire/phase-2.geojson    (14 to 180)
├── roman-empire/phase-3.geojson    (180 to 284)
├── roman-empire/phase-4.geojson    (284 to 395)
├── western-roman-empire/phase-1.geojson  (395 to 476)
├── eastern-roman-empire/phase-1.geojson  (395 to 1453)
├── achaemenid-persia/phase-1.geojson     (-500 to -400)
├── achaemenid-persia/phase-2.geojson     (-400 to -330)
├── macedonian-empire/phase-1.geojson     (-500 to -336)
├── macedonian-empire/phase-2.geojson     (-336 to -301)
├── seleucid-empire/phase-1.geojson       (-301 to -200)
├── seleucid-empire/phase-2.geojson       (-200 to -100)
├── seleucid-empire/phase-3.geojson       (-100 to -63)
├── ptolemaic-egypt/phase-1.geojson       (-305 to -200)
├── ptolemaic-egypt/phase-2.geojson       (-200 to -30)
├── parthian-empire/phase-1.geojson       (-247 to -100)
├── parthian-empire/phase-2.geojson       (-100 to 224)
├── carthage/phase-1.geojson              (-500 to -264)
├── carthage/phase-2.geojson              (-264 to -146)
├── greek-city-states/phase-1.geojson     (-500 to -338)
├── numidia/phase-1.geojson               (-202 to 46)
└── germanic-tribes/phase-1.geojson       (200 to 500)
```

**Modified files:**
- `Makefile` — add `seed`, `seed-entity`, `seed-dry` targets

---

### Task 1: Package Scaffold

**Files:**
- Create: `packages/data/pyproject.toml`
- Create: `packages/data/__init__.py`
- Create: `packages/data/__main__.py`

- [ ] **Step 1: Create package directory structure**

```bash
mkdir -p packages/data/entities packages/data/tests
```

- [ ] **Step 2: Create `packages/data/pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "history-data"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "shapely>=2.0",
    "pyyaml>=6.0",
    "psycopg2-binary>=2.9",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Create `packages/data/__init__.py`**

```python
```

(empty file)

- [ ] **Step 4: Create stub `packages/data/__main__.py`**

```python
def main() -> None:
    print("history-data ingest pipeline")

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Install the package in editable mode**

Run from repo root:
```bash
pip install -e packages/data
```

- [ ] **Step 6: Verify package installs and entry point works**

```bash
python -m data
```

Expected output:
```
history-data ingest pipeline
```

- [ ] **Step 7: Commit**

```bash
git add packages/data/pyproject.toml packages/data/__init__.py packages/data/__main__.py
git commit -m "feat(data): scaffold packages/data Python package"
```

---

### Task 2: normalize.py + Tests

**Files:**
- Create: `packages/data/tests/test_normalize.py`
- Create: `packages/data/normalize.py`

- [ ] **Step 1: Create `packages/data/tests/__init__.py`**

```python
```

(empty file)

- [ ] **Step 2: Write failing tests in `packages/data/tests/test_normalize.py`**

```python
import pytest
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely import wkt as shapely_wkt

from data.normalize import to_multipolygon, simplify_geom, validate_geom


def test_polygon_wraps_to_multipolygon():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    result = to_multipolygon(poly)
    assert isinstance(result, MultiPolygon)
    assert len(list(result.geoms)) == 1


def test_multipolygon_passthrough():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    result = to_multipolygon(mp)
    assert result is mp


def test_non_polygon_raises():
    with pytest.raises(ValueError, match="Cannot convert"):
        to_multipolygon(Point(0, 0))


def test_simplify_returns_multipolygon():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    result = simplify_geom(mp, tolerance=0.01)
    assert isinstance(result, MultiPolygon)


def test_simplify_reduces_vertices():
    coords = [(i * 0.001, 0.001 * (i % 3)) for i in range(200)]
    coords += [(0.2, 0.1), (0, 0.1), (0, 0)]
    poly = MultiPolygon([Polygon(coords)])
    simplified = simplify_geom(poly, tolerance=0.05)
    original_verts = sum(len(list(g.exterior.coords)) for g in poly.geoms)
    simplified_verts = sum(len(list(g.exterior.coords)) for g in simplified.geoms)
    assert simplified_verts < original_verts


def test_valid_geometry_returns_true():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    assert validate_geom(mp) is True


def test_invalid_geometry_returns_false():
    # Self-intersecting (bowtie) polygon is invalid
    invalid = shapely_wkt.loads("POLYGON((0 0, 1 1, 1 0, 0 1, 0 0))")
    assert validate_geom(invalid) is False
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd packages/data && python -m pytest tests/test_normalize.py -v
```

Expected: `ModuleNotFoundError: No module named 'data.normalize'`

- [ ] **Step 4: Implement `packages/data/normalize.py`**

```python
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry


def to_multipolygon(geom: BaseGeometry) -> MultiPolygon:
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    raise ValueError(f"Cannot convert {geom.geom_type} to MultiPolygon")


def simplify_geom(geom: MultiPolygon, tolerance: float = 0.05) -> MultiPolygon:
    simplified = geom.simplify(tolerance, preserve_topology=True)
    return to_multipolygon(simplified)


def validate_geom(geom: BaseGeometry) -> bool:
    return bool(geom.is_valid)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd packages/data && python -m pytest tests/test_normalize.py -v
```

Expected: `7 passed`

- [ ] **Step 6: Commit**

```bash
git add packages/data/normalize.py packages/data/tests/__init__.py packages/data/tests/test_normalize.py
git commit -m "feat(data): normalize.py — Polygon→MultiPolygon, simplify, validate"
```

---

### Task 3: loader.py + Tests

**Files:**
- Create: `packages/data/tests/test_loader.py`
- Create: `packages/data/loader.py`

**Context:** The DB schema has these tables (from `apps/api/alembic/versions/0001_initial_schema.py`):
- `entities(id UUID PK, slug VARCHAR(100) UNIQUE, type VARCHAR(50), color VARCHAR(7))`
- `entity_names(id UUID PK, entity_id UUID FK, name TEXT, language VARCHAR(10), year_start INT, year_end INT, is_primary BOOL)`
- `territories(id UUID PK, entity_id UUID FK, geom MULTIPOLYGON(4326), simplified_geom MULTIPOLYGON(4326), year_start INT, year_end INT, confidence VARCHAR(20), source TEXT)`

- [ ] **Step 1: Write failing tests in `packages/data/tests/test_loader.py`**

```python
from unittest.mock import MagicMock, call

from data.loader import Loader


def _make_loader():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return Loader(mock_conn), mock_cursor


def test_upsert_entity_returns_uuid():
    loader, cursor = _make_loader()
    cursor.fetchone.return_value = ("aaaaaaaa-0000-0000-0000-000000000001",)
    result = loader.upsert_entity("roman-republic", "polity", "#c0392b")
    assert result == "aaaaaaaa-0000-0000-0000-000000000001"
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO entities" in sql
    assert "ON CONFLICT (slug)" in sql
    assert "RETURNING id::text" in sql


def test_delete_territories_returns_count():
    loader, cursor = _make_loader()
    cursor.rowcount = 5
    result = loader.delete_territories("some-entity-uuid")
    assert result == 5
    sql = cursor.execute.call_args[0][0]
    assert "DELETE FROM territories" in sql
    assert "entity_id" in sql


def test_insert_territory_uses_st_geomfromtext_with_srid():
    loader, cursor = _make_loader()
    loader.insert_territory(
        "entity-uuid",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        "MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))",
        -500,
        -264,
        "approximate",
    )
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO territories" in sql
    assert "ST_GeomFromText" in sql
    assert "4326" in sql


def test_upsert_entity_name_deletes_then_inserts():
    loader, cursor = _make_loader()
    loader.upsert_entity_name("entity-uuid", "Roman Republic", -753, -27)
    calls = [c[0][0] for c in cursor.execute.call_args_list]
    assert any("DELETE FROM entity_names" in s for s in calls)
    assert any("INSERT INTO entity_names" in s for s in calls)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd packages/data && python -m pytest tests/test_loader.py -v
```

Expected: `ModuleNotFoundError: No module named 'data.loader'`

- [ ] **Step 3: Implement `packages/data/loader.py`**

```python
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
        confidence: str,
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO territories
                    (id, entity_id, geom, simplified_geom, year_start, year_end, confidence)
                VALUES (
                    %s::uuid, %s::uuid,
                    ST_Multi(ST_GeomFromText(%s, 4326)),
                    ST_Multi(ST_GeomFromText(%s, 4326)),
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
                    confidence,
                ),
            )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd packages/data && python -m pytest tests/test_loader.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add packages/data/loader.py packages/data/tests/test_loader.py
git commit -m "feat(data): loader.py — psycopg2 upsert/insert for entities and territories"
```

---

### Task 4: ingest.py Orchestrator + __main__.py

**Files:**
- Create: `packages/data/ingest.py`
- Modify: `packages/data/__main__.py`

**Context:** `DATA_DIR` must resolve to `data/raw/political/` at the repo root. The package lives at `packages/data/`, so `Path(__file__).parent.parent.parent` goes up three levels to the repo root.

- [ ] **Step 1: Implement `packages/data/ingest.py`**

```python
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
import yaml
from shapely.geometry import shape

from .loader import Loader
from .normalize import simplify_geom, to_multipolygon, validate_geom

_REPO_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = _REPO_ROOT / "data" / "raw" / "political"
ENTITIES_DIR = Path(__file__).parent / "entities"


def _load_configs(entity_filter: str | None) -> list[dict[str, Any]]:
    configs = []
    for yml_file in sorted(ENTITIES_DIR.glob("*.yml")):
        with open(yml_file) as f:
            configs.append(yaml.safe_load(f))
    if entity_filter:
        configs = [c for c in configs if c["slug"] == entity_filter]
        if not configs:
            print(f"Entity '{entity_filter}' not found. Available slugs:")
            for yml_file in sorted(ENTITIES_DIR.glob("*.yml")):
                print(f"  {yml_file.stem}")
            sys.exit(1)
    return configs


def _load_geojson(relative_path: str) -> dict[str, Any]:
    full_path = DATA_DIR / relative_path
    with open(full_path) as f:
        return json.load(f)


def _ingest_entity(loader: Loader, config: dict[str, Any]) -> tuple[int, int]:
    slug = config["slug"]
    entity_id = loader.upsert_entity(slug, config["type"], config["color"])
    loader.upsert_entity_name(
        entity_id,
        config["name"],
        config["year_start"],
        config["year_end"],
    )
    loader.delete_territories(entity_id)

    loaded = 0
    skipped = 0
    for phase in config["phases"]:
        path = phase["geometry"]
        try:
            geojson = _load_geojson(path)
            raw_geom = shape(geojson["geometry"])
            geom = to_multipolygon(raw_geom)
            if not validate_geom(geom):
                print(f"    WARNING: invalid geometry in {path}, skipping")
                skipped += 1
                continue
            simplified = simplify_geom(geom)
            loader.insert_territory(
                entity_id,
                geom.wkt,
                simplified.wkt,
                phase["year_start"],
                phase["year_end"],
                phase.get("confidence", "approximate"),
            )
            loaded += 1
        except Exception as e:
            print(f"    WARNING: failed to load {path}: {e}")
            skipped += 1

    return loaded, skipped


def _validate_only(configs: list[dict[str, Any]]) -> None:
    print(f"DRY RUN: validating {len(configs)} entities")
    errors = 0
    for config in configs:
        slug = config["slug"]
        phase_ok = 0
        phase_err = 0
        for phase in config["phases"]:
            path = phase["geometry"]
            full_path = DATA_DIR / path
            if not full_path.exists():
                print(f"  ERROR: {slug} — file not found: {full_path}")
                phase_err += 1
                errors += 1
                continue
            try:
                with open(full_path) as f:
                    geojson = json.load(f)
                raw_geom = shape(geojson["geometry"])
                geom = to_multipolygon(raw_geom)
                if not validate_geom(geom):
                    print(f"  ERROR: {slug} — invalid geometry: {path}")
                    phase_err += 1
                    errors += 1
                else:
                    phase_ok += 1
            except Exception as e:
                print(f"  ERROR: {slug} — {path}: {e}")
                phase_err += 1
                errors += 1
        status = "OK" if phase_err == 0 else "ERRORS"
        print(f"  [{status}] {slug}: {phase_ok} phases valid, {phase_err} errors")
    if errors:
        print(f"\n{errors} validation error(s). Fix before ingesting.")
        sys.exit(1)
    else:
        print("\nAll files valid.")


def run(entity_filter: str | None = None, dry_run: bool = False) -> None:
    configs = _load_configs(entity_filter)

    if dry_run:
        _validate_only(configs)
        return

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    db_url = db_url.replace("+asyncpg", "")

    conn = psycopg2.connect(db_url)
    try:
        loader = Loader(conn)
        total_loaded = 0
        total_skipped = 0
        for config in configs:
            slug = config["slug"]
            print(f"  {slug}...")
            loaded, skipped = _ingest_entity(loader, config)
            conn.commit()
            total_loaded += loaded
            total_skipped += skipped
            print(f"    {loaded} phases inserted, {skipped} skipped")
        print(f"\nDone: {len(configs)} entities, {total_loaded} territory phases inserted")
        if total_skipped:
            print(f"  ({total_skipped} phases skipped due to errors)")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

- [ ] **Step 2: Replace `packages/data/__main__.py`**

```python
import argparse

from .ingest import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest historical entity data into PostGIS"
    )
    parser.add_argument("--entity", help="Ingest only this entity slug")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs and GeoJSON files without writing to DB",
    )
    args = parser.parse_args()
    run(entity_filter=args.entity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify the module runs**

```bash
python -m data --help
```

Expected:
```
usage: __main__.py [-h] [--entity ENTITY] [--dry-run]
...
```

- [ ] **Step 4: Commit**

```bash
git add packages/data/ingest.py packages/data/__main__.py
git commit -m "feat(data): ingest.py orchestrator and CLI entry point"
```

---

### Task 5: Entity YAML Configs (13 files)

**Files:**
- Create: `packages/data/entities/*.yml` (13 files)

`year_start`/`year_end` at the entity level set the `entity_names` row's temporal range. Phase `year_start`/`year_end` set the `territories` row's range.

- [ ] **Step 1: Create `packages/data/entities/roman-republic.yml`**

```yaml
slug: roman-republic
name: Roman Republic
type: polity
color: "#c0392b"
year_start: -753
year_end: -27
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

- [ ] **Step 2: Create `packages/data/entities/roman-empire.yml`**

```yaml
slug: roman-empire
name: Roman Empire
type: polity
color: "#e74c3c"
year_start: -27
year_end: 395
phases:
  - geometry: roman-empire/phase-1.geojson
    year_start: -27
    year_end: 14
    confidence: approximate
  - geometry: roman-empire/phase-2.geojson
    year_start: 14
    year_end: 180
    confidence: approximate
  - geometry: roman-empire/phase-3.geojson
    year_start: 180
    year_end: 284
    confidence: approximate
  - geometry: roman-empire/phase-4.geojson
    year_start: 284
    year_end: 395
    confidence: approximate
```

- [ ] **Step 3: Create `packages/data/entities/western-roman-empire.yml`**

```yaml
slug: western-roman-empire
name: Western Roman Empire
type: polity
color: "#e67e22"
year_start: 395
year_end: 476
phases:
  - geometry: western-roman-empire/phase-1.geojson
    year_start: 395
    year_end: 476
    confidence: approximate
```

- [ ] **Step 4: Create `packages/data/entities/eastern-roman-empire.yml`**

```yaml
slug: eastern-roman-empire
name: Eastern Roman Empire
type: polity
color: "#9b59b6"
year_start: 395
year_end: 1453
phases:
  - geometry: eastern-roman-empire/phase-1.geojson
    year_start: 395
    year_end: 1453
    confidence: approximate
```

- [ ] **Step 5: Create `packages/data/entities/achaemenid-persia.yml`**

```yaml
slug: achaemenid-persia
name: Achaemenid Persian Empire
type: polity
color: "#f39c12"
year_start: -550
year_end: -330
phases:
  - geometry: achaemenid-persia/phase-1.geojson
    year_start: -500
    year_end: -400
    confidence: approximate
  - geometry: achaemenid-persia/phase-2.geojson
    year_start: -400
    year_end: -330
    confidence: approximate
```

- [ ] **Step 6: Create `packages/data/entities/macedonian-empire.yml`**

```yaml
slug: macedonian-empire
name: Macedonian Empire
type: polity
color: "#3498db"
year_start: -808
year_end: -301
phases:
  - geometry: macedonian-empire/phase-1.geojson
    year_start: -500
    year_end: -336
    confidence: approximate
  - geometry: macedonian-empire/phase-2.geojson
    year_start: -336
    year_end: -301
    confidence: approximate
```

- [ ] **Step 7: Create `packages/data/entities/seleucid-empire.yml`**

```yaml
slug: seleucid-empire
name: Seleucid Empire
type: polity
color: "#2980b9"
year_start: -312
year_end: -63
phases:
  - geometry: seleucid-empire/phase-1.geojson
    year_start: -301
    year_end: -200
    confidence: approximate
  - geometry: seleucid-empire/phase-2.geojson
    year_start: -200
    year_end: -100
    confidence: approximate
  - geometry: seleucid-empire/phase-3.geojson
    year_start: -100
    year_end: -63
    confidence: approximate
```

- [ ] **Step 8: Create `packages/data/entities/ptolemaic-egypt.yml`**

```yaml
slug: ptolemaic-egypt
name: Ptolemaic Egypt
type: polity
color: "#27ae60"
year_start: -305
year_end: -30
phases:
  - geometry: ptolemaic-egypt/phase-1.geojson
    year_start: -305
    year_end: -200
    confidence: approximate
  - geometry: ptolemaic-egypt/phase-2.geojson
    year_start: -200
    year_end: -30
    confidence: approximate
```

- [ ] **Step 9: Create `packages/data/entities/parthian-empire.yml`**

```yaml
slug: parthian-empire
name: Parthian Empire
type: polity
color: "#16a085"
year_start: -247
year_end: 224
phases:
  - geometry: parthian-empire/phase-1.geojson
    year_start: -247
    year_end: -100
    confidence: approximate
  - geometry: parthian-empire/phase-2.geojson
    year_start: -100
    year_end: 224
    confidence: approximate
```

- [ ] **Step 10: Create `packages/data/entities/carthage.yml`**

```yaml
slug: carthage
name: Carthage
type: polity
color: "#8e44ad"
year_start: -814
year_end: -146
phases:
  - geometry: carthage/phase-1.geojson
    year_start: -500
    year_end: -264
    confidence: approximate
  - geometry: carthage/phase-2.geojson
    year_start: -264
    year_end: -146
    confidence: approximate
```

- [ ] **Step 11: Create `packages/data/entities/greek-city-states.yml`**

```yaml
slug: greek-city-states
name: Greek City-States
type: polity
color: "#2ecc71"
year_start: -800
year_end: -338
phases:
  - geometry: greek-city-states/phase-1.geojson
    year_start: -500
    year_end: -338
    confidence: approximate
```

- [ ] **Step 12: Create `packages/data/entities/numidia.yml`**

```yaml
slug: numidia
name: Numidia
type: polity
color: "#d35400"
year_start: -202
year_end: 46
phases:
  - geometry: numidia/phase-1.geojson
    year_start: -202
    year_end: 46
    confidence: approximate
```

- [ ] **Step 13: Create `packages/data/entities/germanic-tribes.yml`**

```yaml
slug: germanic-tribes
name: Germanic Tribes
type: polity
color: "#7f8c8d"
year_start: 200
year_end: 500
phases:
  - geometry: germanic-tribes/phase-1.geojson
    year_start: 200
    year_end: 500
    confidence: approximate
```

- [ ] **Step 14: Commit**

```bash
git add packages/data/entities/
git commit -m "feat(data): entity YAML configs for all 13 civilizations"
```

---

### Task 6: Roman GeoJSON Files (9 files)

**Files:**
- Create: `data/raw/political/roman-republic/phase-1.geojson`
- Create: `data/raw/political/roman-republic/phase-2.geojson`
- Create: `data/raw/political/roman-republic/phase-3.geojson`
- Create: `data/raw/political/roman-empire/phase-1.geojson`
- Create: `data/raw/political/roman-empire/phase-2.geojson`
- Create: `data/raw/political/roman-empire/phase-3.geojson`
- Create: `data/raw/political/roman-empire/phase-4.geojson`
- Create: `data/raw/political/western-roman-empire/phase-1.geojson`
- Create: `data/raw/political/eastern-roman-empire/phase-1.geojson`

All coordinates: [longitude, latitude], WGS84. Each ring must close (first point = last point). Approximate historical boundaries, accurate to zoom 2–4.

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p data/raw/political/roman-republic
mkdir -p data/raw/political/roman-empire
mkdir -p data/raw/political/western-roman-empire
mkdir -p data/raw/political/eastern-roman-empire
```

- [ ] **Step 2: Create `data/raw/political/roman-republic/phase-1.geojson`**

Italian peninsula (-500 to -264). Rome controls Latium, then all of Italy south of the Po Valley. Excludes Cisalpine Gaul (north of ~44°N).

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[7.5,43.8],[14.0,44.0],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 3: Create `data/raw/political/roman-republic/phase-2.geojson`**

(-264 to -100). After First Punic War (-264 to -241): gains Sicily, Sardinia (-238), Corsica (-238). After Second Punic War (-218 to -201): eastern Iberia. After Third Punic War (-149 to -146): Tunisia. Po Valley (Cisalpine Gaul) taken -189. Southern France (Narbonese Gaul) -121.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-0.5,43.5],[3.5,43.5],[3.5,37.5],[-0.5,36.5],[-0.5,43.5]]],
      [[[7.5,37.0],[11.5,37.0],[11.5,30.0],[7.5,30.0],[7.5,37.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 4: Create `data/raw/political/roman-republic/phase-3.geojson`**

(-100 to -27). Full Republic: all Iberia (-133), all Gaul (Caesar -58 to -50), Greece (-146), Turkey/Pergamon (-133), Syria (-64), Egypt (-30). Massive Mediterranean empire.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[7.0,51.0],[2.5,51.5],[-2.0,51.0],[-5.0,48.0],[-5.0,44.0]]],
      [[[-6.0,35.5],[13.5,37.0],[13.5,30.5],[10.0,30.0],[5.0,30.5],[-1.5,31.5],[-6.0,33.5],[-6.0,35.5]]],
      [[[19.5,42.0],[28.5,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[42.5,37.0],[42.5,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 5: Create `data/raw/political/roman-empire/phase-1.geojson`**

(-27 to 14). Augustan reorganization. Same core as Republic Phase 3 with consolidated Balkans (Danube frontier) and firm Rhine frontier.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[6.5,51.5],[2.5,51.5],[-2.0,51.0],[-5.0,48.0],[-5.0,44.0]]],
      [[[-6.0,35.5],[13.5,37.0],[13.5,30.5],[10.0,30.0],[5.0,30.5],[-1.5,31.5],[-6.0,33.5],[-6.0,35.5]]],
      [[[19.5,42.0],[30.0,45.0],[30.0,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[42.5,37.0],[42.5,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 6: Create `data/raw/political/roman-empire/phase-2.geojson`**

(14 to 180). High Empire peak under Trajan (~117 CE). Add Britain, Dacia (Romania), expanded N.Africa (Mauretania).

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[6.5,51.5],[2.5,51.5],[-2.0,51.0],[-5.0,48.0],[-5.0,44.0]]],
      [[[-5.5,50.0],[1.5,51.5],[0.5,53.5],[-3.0,58.5],[-6.0,58.5],[-5.5,56.0],[-4.0,53.5],[-5.5,50.0]]],
      [[[-6.0,35.5],[13.5,37.0],[13.5,30.0],[10.0,29.5],[5.0,30.0],[-1.5,31.0],[-6.0,33.0],[-6.0,35.5]]],
      [[[19.5,42.0],[30.5,47.0],[30.5,43.5],[30.0,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[22.0,44.0],[30.0,44.0],[30.0,47.0],[22.0,47.0],[22.0,44.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[44.0,37.5],[44.0,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 7: Create `data/raw/political/roman-empire/phase-3.geojson`**

(180 to 284). Crisis of the Third Century. Loss of Dacia (271), reduced Mesopotamia, Britain becomes autonomous zones but nominally Roman. Core Mediterranean held.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[6.5,51.5],[2.5,51.5],[-2.0,51.0],[-5.0,48.0],[-5.0,44.0]]],
      [[[-5.5,50.0],[1.5,51.5],[0.5,53.0],[-3.0,58.0],[-6.0,58.0],[-5.5,50.0]]],
      [[[-6.0,35.5],[13.5,37.0],[13.5,30.0],[5.0,30.0],[-1.5,31.0],[-6.0,33.0],[-6.0,35.5]]],
      [[[19.5,42.0],[30.5,46.0],[30.5,43.0],[30.0,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[42.5,37.0],[42.5,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 8: Create `data/raw/political/roman-empire/phase-4.geojson`**

(284 to 395). Diocletian/Constantine. Reorganized empire. Dacia abandoned, Britain less secure. Core Mediterranean stable.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[6.5,51.5],[2.5,51.5],[-2.0,51.0],[-5.0,48.0],[-5.0,44.0]]],
      [[[-5.5,50.0],[1.5,51.5],[0.5,53.0],[-3.0,57.0],[-5.5,50.0]]],
      [[[-6.0,35.5],[13.5,37.0],[13.5,30.0],[5.0,30.0],[-1.5,31.0],[-6.0,33.0],[-6.0,35.5]]],
      [[[19.5,42.0],[30.5,46.0],[30.5,43.0],[30.0,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[42.5,37.0],[42.5,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 9: Create `data/raw/political/western-roman-empire/phase-1.geojson`**

(395 to 476). Western half after the split. Circa 420 CE state: Italy, Gaul (increasingly Visigothic), Iberia (Visigothic pressure), Dalmatia. N.Africa lost to Vandals by 439 CE; representing ~430 CE.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[6.5,44.0],[13.5,46.0],[14.0,45.5],[15.0,44.5],[15.5,41.5],[17.8,40.5],[18.5,40.0],[16.5,38.0],[15.5,37.5],[13.5,37.5],[12.0,37.8],[12.0,38.5],[10.0,38.0],[8.5,39.5],[7.5,43.8],[6.5,44.0]]],
      [[[12.5,38.2],[15.5,38.2],[15.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.5,43.0],[9.6,43.0],[9.6,38.8],[8.5,38.8],[8.5,43.0]]],
      [[[-9.5,44.0],[3.5,43.5],[3.5,36.0],[-5.5,36.0],[-9.5,37.0],[-9.5,44.0]]],
      [[[-5.0,44.0],[8.0,44.0],[8.0,48.0],[5.0,51.0],[2.0,51.0],[-2.0,49.0],[-5.0,47.0],[-5.0,44.0]]],
      [[[7.5,37.0],[11.0,37.0],[11.0,30.0],[7.5,30.0],[7.5,37.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 10: Create `data/raw/political/eastern-roman-empire/phase-1.geojson`**

(395 to 1453). Eastern half (Byzantine Empire). Circa 400 CE state: Balkans, Turkey, Syria, Egypt, Libya. Stable for centuries despite later losses.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[19.5,42.0],[30.5,46.0],[30.5,43.0],[30.0,42.0],[28.5,36.0],[22.0,36.0],[20.0,37.5],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[42.5,37.0],[42.5,30.0],[35.5,30.0],[34.5,31.5],[36.0,37.0]]],
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]],
      [[[11.5,32.5],[25.0,32.5],[25.0,28.0],[11.5,28.0],[11.5,32.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 11: Validate Roman GeoJSON files**

```bash
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity roman-republic
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity roman-empire
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity western-roman-empire
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity eastern-roman-empire
```

Expected: `All files valid.` for each entity.

- [ ] **Step 12: Commit**

```bash
git add data/raw/political/roman-republic/ data/raw/political/roman-empire/ data/raw/political/western-roman-empire/ data/raw/political/eastern-roman-empire/
git commit -m "feat(data): GeoJSON phase files for Roman entities (9 files)"
```

---

### Task 7: Eastern Mediterranean GeoJSON (11 files)

**Files:**
- Create: `data/raw/political/achaemenid-persia/phase-1.geojson`
- Create: `data/raw/political/achaemenid-persia/phase-2.geojson`
- Create: `data/raw/political/macedonian-empire/phase-1.geojson`
- Create: `data/raw/political/macedonian-empire/phase-2.geojson`
- Create: `data/raw/political/seleucid-empire/phase-1.geojson`
- Create: `data/raw/political/seleucid-empire/phase-2.geojson`
- Create: `data/raw/political/seleucid-empire/phase-3.geojson`
- Create: `data/raw/political/ptolemaic-egypt/phase-1.geojson`
- Create: `data/raw/political/ptolemaic-egypt/phase-2.geojson`
- Create: `data/raw/political/parthian-empire/phase-1.geojson`
- Create: `data/raw/political/parthian-empire/phase-2.geojson`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p data/raw/political/achaemenid-persia
mkdir -p data/raw/political/macedonian-empire
mkdir -p data/raw/political/seleucid-empire
mkdir -p data/raw/political/ptolemaic-egypt
mkdir -p data/raw/political/parthian-empire
```

- [ ] **Step 2: Create `data/raw/political/achaemenid-persia/phase-1.geojson`**

(-500 to -400). Full Achaemenid extent under Darius/Xerxes: Turkey, Syria, Egypt, Mesopotamia, Iran, Afghanistan, Central Asia, NW India.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[26.0,42.0],[36.5,38.0],[38.0,38.0],[44.0,38.0],[52.0,38.0],[70.0,42.0],[77.0,34.0],[64.0,22.0],[44.0,22.0],[34.0,22.0],[25.0,22.0],[25.0,31.5],[35.0,31.5],[36.0,33.0],[36.0,37.0],[42.5,37.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 3: Create `data/raw/political/achaemenid-persia/phase-2.geojson`**

(-400 to -330). Reduced: lost Egypt (-404 and again after revolts), western Anatolia contested with Greeks. Eastern extent maintained.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[28.0,42.0],[36.5,38.0],[44.0,38.0],[52.0,38.0],[68.0,42.0],[72.0,34.0],[60.0,22.0],[44.0,22.0],[36.0,28.0],[36.0,33.0],[36.0,37.0],[42.5,37.0],[36.5,36.0],[28.0,36.0],[28.0,42.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 4: Create `data/raw/political/macedonian-empire/phase-1.geojson`**

(-500 to -336). Kingdom of Macedon before Alexander: small region in northern Greece, roughly modern North Macedonia and northern Greece.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[20.5,41.5],[23.5,41.5],[24.0,40.5],[22.5,40.0],[21.0,40.5],[20.5,41.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 5: Create `data/raw/political/macedonian-empire/phase-2.geojson`**

(-336 to -301). Alexander's Empire at its peak (~323 BCE): Greece, Turkey, Egypt, Persia, Central Asia, NW India.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[19.5,42.0],[28.5,42.0],[28.5,36.0],[20.0,36.0],[19.5,42.0]]],
      [[[26.0,42.0],[36.5,42.0],[36.5,36.0],[26.0,36.0],[26.0,42.0]]],
      [[[36.0,37.0],[44.0,38.0],[52.0,38.0],[72.0,42.0],[77.0,32.0],[60.0,20.0],[44.0,20.0],[34.0,20.0],[25.0,22.0],[25.0,31.5],[35.0,31.5],[36.0,33.0],[36.0,37.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 6: Create `data/raw/political/seleucid-empire/phase-1.geojson`**

(-301 to -200). Large Seleucid successor state: Turkey (east), Syria, Mesopotamia, Iran, Central Asia. Not Egypt (Ptolemaic), not Greece (Antigonid).

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[30.0,42.0],[36.5,42.0],[44.0,38.0],[52.0,38.0],[70.0,42.0],[72.0,32.0],[60.0,22.0],[44.0,22.0],[36.0,28.0],[36.0,33.0],[36.0,37.0],[42.5,37.0],[36.5,36.0],[30.0,36.0],[30.0,42.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 7: Create `data/raw/political/seleucid-empire/phase-2.geojson`**

(-200 to -100). Fragmented: lost eastern territories to Parthia and Bactria. Mainly Turkey + Syria + Mesopotamia.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[30.0,42.0],[36.5,42.0],[48.0,34.0],[44.0,30.0],[36.0,30.0],[36.0,33.0],[36.0,37.0],[42.5,37.0],[36.5,36.0],[30.0,36.0],[30.0,42.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 8: Create `data/raw/political/seleucid-empire/phase-3.geojson`**

(-100 to -63). Rump state: essentially just Syria (Antioch area) and parts of southern Turkey.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[35.5,37.5],[38.0,37.5],[42.5,37.0],[42.5,33.0],[36.0,33.0],[35.5,35.0],[35.5,37.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 9: Create `data/raw/political/ptolemaic-egypt/phase-1.geojson`**

(-305 to -200). Ptolemaic Egypt at its height: Egypt, Cyrene (Libya), Cyprus, parts of the Levant coast.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[25.0,31.5],[35.0,31.5],[36.0,31.0],[34.5,30.0],[25.0,22.0],[25.0,31.5]]],
      [[[11.5,33.0],[25.0,33.0],[25.0,28.0],[11.5,28.0],[11.5,33.0]]],
      [[[33.0,35.7],[34.5,35.7],[34.5,34.5],[33.0,34.5],[33.0,35.7]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 10: Create `data/raw/political/ptolemaic-egypt/phase-2.geojson`**

(-200 to -30). Reduced Ptolemaic Egypt: core Nile valley + Cyprus only.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[25.0,31.5],[35.0,31.5],[35.0,22.0],[25.0,22.0],[25.0,31.5]]],
      [[[33.0,35.7],[34.5,35.7],[34.5,34.5],[33.0,34.5],[33.0,35.7]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 11: Create `data/raw/political/parthian-empire/phase-1.geojson`**

(-247 to -100). Early Parthian state: northeastern Iran and parts of Central Asia. Gradually expanding westward.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[44.0,38.0],[68.0,42.0],[70.0,34.0],[52.0,24.0],[44.0,28.0],[40.0,34.0],[44.0,38.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 12: Create `data/raw/political/parthian-empire/phase-2.geojson`**

(-100 to 224). Peak Parthian Empire: Iran + Mesopotamia (Iraq) + parts of Central Asia. Rivals Rome along the Euphrates.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[38.0,38.0],[44.0,38.0],[52.0,38.0],[65.0,40.0],[68.0,32.0],[52.0,22.0],[44.0,22.0],[38.0,30.0],[36.0,33.0],[40.0,36.0],[38.0,38.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 13: Validate Eastern Mediterranean GeoJSON files**

```bash
for entity in achaemenid-persia macedonian-empire seleucid-empire ptolemaic-egypt parthian-empire; do
  echo "Validating $entity..."
  DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity $entity
done
```

Expected: `All files valid.` for each entity.

- [ ] **Step 14: Commit**

```bash
git add data/raw/political/achaemenid-persia/ data/raw/political/macedonian-empire/ data/raw/political/seleucid-empire/ data/raw/political/ptolemaic-egypt/ data/raw/political/parthian-empire/
git commit -m "feat(data): GeoJSON phase files for Eastern Mediterranean entities (11 files)"
```

---

### Task 8: Western Mediterranean + Other GeoJSON (5 files)

**Files:**
- Create: `data/raw/political/carthage/phase-1.geojson`
- Create: `data/raw/political/carthage/phase-2.geojson`
- Create: `data/raw/political/greek-city-states/phase-1.geojson`
- Create: `data/raw/political/numidia/phase-1.geojson`
- Create: `data/raw/political/germanic-tribes/phase-1.geojson`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p data/raw/political/carthage
mkdir -p data/raw/political/greek-city-states
mkdir -p data/raw/political/numidia
mkdir -p data/raw/political/germanic-tribes
```

- [ ] **Step 2: Create `data/raw/political/carthage/phase-1.geojson`**

(-500 to -264). Carthaginian Empire at height: Tunisia, western Algeria, southern Iberia, western Sicily (contested), Sardinia, Malta, Balearic Islands.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[-2.0,37.5],[11.5,37.5],[11.5,30.0],[-2.0,30.0],[-2.0,37.5]]],
      [[[-6.0,38.5],[0.0,38.5],[0.0,36.0],[-6.0,36.0],[-6.0,38.5]]],
      [[[12.5,38.2],[13.5,38.2],[13.5,37.0],[12.5,37.0],[12.5,38.2]]],
      [[[8.3,40.0],[9.0,40.0],[9.0,38.8],[8.3,38.8],[8.3,40.0]]],
      [[[14.3,35.9],[14.6,35.9],[14.6,35.8],[14.3,35.8],[14.3,35.9]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 3: Create `data/raw/political/carthage/phase-2.geojson`**

(-264 to -146). Reduced after First Punic War (lost Sicily -241). Barcid conquest of Spain -237 to -218 adds Iberian territory. Tunisia + Algeria + southern Spain.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[-2.0,37.5],[11.5,37.5],[11.5,30.0],[-2.0,30.0],[-2.0,37.5]]],
      [[[-6.0,39.0],[-0.5,39.0],[-0.5,36.0],[-6.0,36.0],[-6.0,39.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 4: Create `data/raw/political/greek-city-states/phase-1.geojson`**

(-500 to -338). Classical Greek world: mainland Greece, Aegean islands, Ionian coast (western Turkey). Dominated by Athens and Sparta at various times.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[19.5,42.0],[28.5,42.0],[28.5,36.0],[20.5,36.0],[19.5,37.5],[19.5,42.0]]],
      [[[26.0,40.0],[28.5,40.0],[28.5,37.0],[26.0,37.0],[26.0,40.0]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 5: Create `data/raw/political/numidia/phase-1.geojson`**

(-202 to 46). Numidian kingdom: western Tunisia and Algeria (west of Carthage). Allied with Rome against Carthage, later became Roman province Africa Nova.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[-2.0,37.5],[7.5,37.5],[7.5,30.0],[-2.0,30.0],[-2.0,37.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 6: Create `data/raw/political/germanic-tribes/phase-1.geojson`**

(200 to 500). Germanic tribal confederations east of the Rhine: Goths, Vandals, Alemanni, Franks, Saxons. Represented as a rough block covering Germany, southern Scandinavia, Poland.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [[[8.0,47.5],[25.0,47.5],[25.0,50.0],[30.0,55.0],[15.0,58.0],[8.0,58.0],[8.0,47.5]]]
    ]
  },
  "properties": {}
}
```

- [ ] **Step 7: Validate remaining GeoJSON files**

```bash
for entity in carthage greek-city-states numidia germanic-tribes; do
  echo "Validating $entity..."
  DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run --entity $entity
done
```

Expected: `All files valid.` for each entity.

- [ ] **Step 8: Validate all 13 entities at once**

```bash
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run
```

Expected:
```
DRY RUN: validating 13 entities
  [OK] achaemenid-persia: 2 phases valid, 0 errors
  [OK] carthage: 2 phases valid, 0 errors
  ...
All files valid.
```

- [ ] **Step 9: Commit**

```bash
git add data/raw/political/carthage/ data/raw/political/greek-city-states/ data/raw/political/numidia/ data/raw/political/germanic-tribes/
git commit -m "feat(data): GeoJSON phase files for W.Mediterranean and other entities (5 files)"
```

---

### Task 9: Integration Test

**Files:**
- Create: `packages/data/tests/conftest.py`
- Create: `packages/data/tests/test_ingest.py`

**Context:** Integration tests require the test DB from `infra/docker-compose.test.yml` running on port 5433. The test DB URL is `postgresql://history:history@localhost:5433/history_test`. Run `docker compose -f infra/docker-compose.test.yml up -d` before running these tests. The test DB must have migrations applied.

- [ ] **Step 1: Create `packages/data/tests/conftest.py`**

```python
import os
import subprocess
import pytest
import psycopg2


TEST_DB_URL = "postgresql://history:history@localhost:5433/history_test"
TEST_DB_URL_ASYNC = "postgresql+asyncpg://history:history@localhost:5433/history_test"


@pytest.fixture(scope="session", autouse=True)
def migrate_test_db():
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DB_URL_ASYNC
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        cwd="apps/api",
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"Could not migrate test DB: {result.stderr}")


@pytest.fixture(scope="session")
def db_conn():
    try:
        conn = psycopg2.connect(TEST_DB_URL)
    except Exception as e:
        pytest.skip(f"Test DB not available: {e}")
    yield conn
    conn.close()
```

- [ ] **Step 2: Write `packages/data/tests/test_ingest.py`**

```python
import os
import psycopg2
import pytest

from data.ingest import run

TEST_DB_URL = "postgresql://history:history@localhost:5433/history_test"


@pytest.fixture(autouse=True)
def set_db_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)


@pytest.fixture(autouse=True)
def clean_entities(db_conn):
    yield
    with db_conn.cursor() as cur:
        cur.execute("DELETE FROM territories")
        cur.execute("DELETE FROM entity_names")
        cur.execute("DELETE FROM entities WHERE slug IN ('roman-republic', 'germanic-tribes')")
    db_conn.commit()


def test_ingest_single_entity_creates_rows(db_conn):
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM entities WHERE slug = 'roman-republic'")
        assert cur.fetchone()[0] == 1

        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            """
        )
        assert cur.fetchone()[0] == 3  # 3 phases


def test_ingest_sets_correct_year_ranges(db_conn):
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT year_start, year_end FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            ORDER BY year_start
            """
        )
        rows = cur.fetchall()

    assert rows[0] == (-500, -264)
    assert rows[1] == (-264, -100)
    assert rows[2] == (-100, -27)


def test_ingest_is_idempotent(db_conn):
    run(entity_filter="roman-republic")
    run(entity_filter="roman-republic")

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM entities WHERE slug = 'roman-republic'")
        assert cur.fetchone()[0] == 1

        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'roman-republic'
            """
        )
        assert cur.fetchone()[0] == 3


def test_ingest_single_phase_entity(db_conn):
    run(entity_filter="germanic-tribes")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM territories t
            JOIN entities e ON t.entity_id = e.id
            WHERE e.slug = 'germanic-tribes'
            """
        )
        assert cur.fetchone()[0] == 1
```

- [ ] **Step 3: Start test DB and run migrations**

```bash
docker compose -f infra/docker-compose.test.yml up -d
```

Wait ~10 seconds for postgres_test to be ready.

- [ ] **Step 4: Run integration tests**

```bash
cd packages/data && python -m pytest tests/test_ingest.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add packages/data/tests/conftest.py packages/data/tests/test_ingest.py
git commit -m "test(data): integration tests for ingest pipeline"
```

---

### Task 10: Makefile Update + End-to-End Verification

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Update `Makefile`**

Current relevant content (lines 12-16):
```makefile
migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python -m data.ingest
```

Replace those two targets and add new ones. The full updated `Makefile`:

```makefile
.PHONY: dev dev-build stop migrate seed seed-entity seed-dry test lint

dev:
	docker compose -f infra/docker-compose.yml --project-directory . up

dev-build:
	docker compose -f infra/docker-compose.yml --project-directory . up --build

stop:
	docker compose -f infra/docker-compose.yml --project-directory . down

migrate:
	docker compose -f infra/docker-compose.yml --project-directory . exec api alembic upgrade head

seed:
	DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data

seed-entity:
	DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --entity $(ENTITY)

seed-dry:
	DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data --dry-run

test:
	docker compose -f infra/docker-compose.test.yml up -d
	docker compose -f infra/docker-compose.test.yml exec postgres_test sh -c 'until pg_isready -U history; do sleep 1; done'
	cd apps/api && DATABASE_URL=postgresql+asyncpg://history:history@localhost:5433/history_test REDIS_URL=redis://localhost:6380 pytest tests/ -v; EXIT_CODE=$$?; docker compose -f infra/docker-compose.test.yml down; exit $$EXIT_CODE

lint:
	cd apps/api && ruff check app/ tests/
```

- [ ] **Step 2: Verify Docker stack is running**

```bash
docker compose -f infra/docker-compose.yml --project-directory . ps
```

Expected: All containers `Up` including `history_postgres` and `history_api`.

- [ ] **Step 3: Run full dry-run to validate all 13 entities**

```bash
python -m data --dry-run
```

Expected:
```
DRY RUN: validating 13 entities
  [OK] achaemenid-persia: 2 phases valid, 0 errors
  [OK] carthage: 2 phases valid, 0 errors
  [OK] eastern-roman-empire: 1 phases valid, 0 errors
  [OK] germanic-tribes: 1 phases valid, 0 errors
  [OK] greek-city-states: 1 phases valid, 0 errors
  [OK] macedonian-empire: 2 phases valid, 0 errors
  [OK] numidia: 1 phases valid, 0 errors
  [OK] parthian-empire: 2 phases valid, 0 errors
  [OK] ptolemaic-egypt: 2 phases valid, 0 errors
  [OK] roman-empire: 4 phases valid, 0 errors
  [OK] roman-republic: 3 phases valid, 0 errors
  [OK] seleucid-empire: 3 phases valid, 0 errors
  [OK] western-roman-empire: 1 phases valid, 0 errors

All files valid.
```

- [ ] **Step 4: Run full ingest**

```bash
DATABASE_URL=postgresql://history:history@localhost:5432/history python -m data
```

Expected output includes all 13 entities with phase counts. Ends with:
```
Done: 13 entities, 25 territory phases inserted
```

- [ ] **Step 5: Flush Redis cache**

```bash
docker compose -f infra/docker-compose.yml --project-directory . exec redis redis-cli FLUSHALL
```

- [ ] **Step 6: Verify API returns territories**

```bash
curl "http://localhost:8000/api/v1/world/state?year=-264&zoom=4&min_x=-180&min_y=-90&max_x=180&max_y=90" -UseBasicParsing | python -c "import sys,json; data=json.load(sys.stdin); print(f'{len(data[\"features\"])} features at year -264')"
```

Expected: `3 features at year -264` (Roman Republic phase 2, Achaemenid phase 1, Ptolemaic phase 1 all active at -264).

- [ ] **Step 7: Open browser and verify map**

Open `http://localhost:3000`. Verify:
- At 264 BCE (default): Rome, Persia, Egypt visible on map
- Drag slider to 100 BCE: Roman Republic Phase 3 covers entire Mediterranean
- Drag slider to 100 CE: Roman Empire Phase 2 (peak), Parthia visible
- Drag slider to 400 CE: Western + Eastern Roman visible as separate entities
- Click a territory: EntityPanel shows entity name, type, color
- No error banner

- [ ] **Step 8: Commit final changes**

```bash
git add Makefile
git commit -m "feat(data): update Makefile with seed targets; full E2E verified"
```

---

## Self-Review

**Spec coverage check:**
- ✅ `packages/data/` standalone package with pyproject.toml (Task 1)
- ✅ `normalize.py` with `to_multipolygon`, `simplify_geom`, `validate_geom` (Task 2)
- ✅ `loader.py` with `Loader` class, psycopg2, upsert/delete/insert (Task 3)
- ✅ `ingest.py` orchestrator with `--entity` and `--dry-run` flags (Task 4)
- ✅ 13 entity YAML configs with year_start, year_end, phases (Task 5)
- ✅ ~25 GeoJSON phase files covering all entities (Tasks 6–8)
- ✅ Unit tests for normalize and loader (Tasks 2–3)
- ✅ Integration test with idempotency check (Task 9)
- ✅ Makefile targets: seed, seed-entity, seed-dry (Task 10)
- ✅ Runs locally against localhost:5432 with DATABASE_URL (Task 10)
- ✅ Idempotent: DELETE then INSERT territories per entity (Task 3, Task 9)
- ✅ Error handling: skip bad phase with warning, continue (Task 4)

**Type consistency check:**
- `Loader.upsert_entity` returns `str` (UUID as text) → used as `entity_id: str` in `_ingest_entity` ✅
- `Loader.insert_territory` takes `geom_wkt: str` → `geom.wkt` from Shapely is `str` ✅
- `to_multipolygon` returns `MultiPolygon` → `simplify_geom` accepts `MultiPolygon` ✅
- Phase `year_end: int | None` matches DB `year_end INT nullable` ✅
