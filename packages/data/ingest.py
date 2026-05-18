import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
import yaml
from shapely.geometry import shape

from .loader import Loader
from .normalize import (
    MAX_VERTICES_LO, coerce_valid, count_vertices, simplify_geom_all,
    to_multipolygon, validate_geom,
)

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
    # 1. Try the direct path first (existing behaviour)
    full_path = DATA_DIR / relative_path
    if full_path.exists():
        with open(full_path) as f:
            return json.load(f)
    # 2. Recursive glob — supports regional subdirectories such as
    #    data/raw/political/mediterranean/roman-empire/phase-1.geojson
    matches = list(DATA_DIR.glob(f"**/{relative_path}"))
    if matches:
        with open(matches[0]) as f:
            return json.load(f)
    # 3. Fall back to the original path so the original FileNotFoundError is raised
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
            geom = to_multipolygon(coerce_valid(raw_geom))
            if not validate_geom(geom):
                print(f"    WARNING: invalid geometry in {path}, skipping")
                skipped += 1
                continue
            geom_hi, geom_med, geom_lo = simplify_geom_all(geom)
            v_hi = count_vertices(geom_hi)
            v_lo = count_vertices(geom_lo)
            if v_lo > MAX_VERTICES_LO:
                print(f"    WARNING: {path} geom_lo has {v_lo} vertices (budget {MAX_VERTICES_LO})")
            print(f"    LOD: hi={v_hi} med={count_vertices(geom_med)} lo={v_lo} vertices")
            loader.insert_territory(
                entity_id,
                geom_hi.wkt,
                geom_med.wkt,
                phase["year_start"],
                phase["year_end"],
                confidence_type=phase.get("confidence", "approximate"),
                confidence_score=phase.get("confidence_score"),
                source_name=config.get("source_name"),
                source_url=config.get("source_url"),
                source_license=config.get("source_license"),
                data_version=config.get("data_version"),
                resolution_km=config.get("resolution_km"),
                importance=config.get("importance", 5),
                map_modes=config.get("map_modes", ["political"]),
                geom_lo_wkt=geom_lo.wkt,
                date_precision=phase.get("date_precision", "approximate"),
                end_event_type=phase.get("end_event_type"),
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
                geom = to_multipolygon(coerce_valid(raw_geom))
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
