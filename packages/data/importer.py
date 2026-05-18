"""Generic shapefile / GeoJSON importer for external historical datasets.

Usage:
    from data.importer import Importer
    imp = Importer(conn, source_config_path="packages/data/sources/cshapes.yml")
    imp.import_file("data/sources/cshapes/cshapes_2.0.shp")
"""
import json
import os
import uuid
from pathlib import Path
from typing import Any

import psycopg2.extensions
import yaml
from shapely.geometry import shape

from .loader import Loader
from .normalize import coerce_valid, simplify_geom, to_multipolygon, validate_geom


class ImportError(Exception):
    pass


def _load_source_config(config_path: str | Path) -> dict[str, Any]:
    with open(config_path) as f:
        return yaml.safe_load(f)


def _extract_field(feature_props: dict[str, Any], mapping: str | None) -> Any:
    if mapping is None:
        return None
    return feature_props.get(mapping)


def _import_geojson(
    path: str | Path,
    config: dict[str, Any],
    loader: Loader,
) -> tuple[int, int]:
    with open(path) as f:
        fc = json.load(f)

    features = fc.get("features", [])
    fields = config.get("fields", {})
    defaults = config.get("defaults", {})

    loaded = 0
    skipped = 0

    for feat in features:
        props = feat.get("properties", {}) or {}
        try:
            slug = _extract_field(props, fields.get("slug")) or str(uuid.uuid4())[:8]
            name = _extract_field(props, fields.get("name")) or slug
            entity_type = _extract_field(props, fields.get("type")) or defaults.get("type", "polity")
            color = _extract_field(props, fields.get("color")) or defaults.get("color", "#888888")
            year_start = int(_extract_field(props, fields.get("year_start")) or defaults.get("year_start", -500))
            year_end_raw = _extract_field(props, fields.get("year_end"))
            year_end = int(year_end_raw) if year_end_raw is not None else defaults.get("year_end")

            entity_id = loader.upsert_entity(slug, entity_type, color)
            loader.upsert_entity_name(entity_id, name, year_start, year_end)
            loader.delete_territories(entity_id)

            raw_geom = shape(feat["geometry"])
            geom = to_multipolygon(coerce_valid(raw_geom))
            if not validate_geom(geom):
                print(f"  WARNING: invalid geometry for {slug}, skipping")
                skipped += 1
                continue

            simplified = simplify_geom(geom)
            loader.insert_territory(
                entity_id,
                geom.wkt,
                simplified.wkt,
                year_start,
                year_end,
                confidence_type=defaults.get("confidence_type", "approximate"),
                confidence_score=defaults.get("confidence_score"),
                source_name=config.get("source_name"),
                source_url=config.get("source_url"),
                source_license=config.get("source_license"),
                data_version=config.get("data_version"),
                resolution_km=defaults.get("resolution_km"),
                importance=defaults.get("importance", 5),
                map_modes=defaults.get("map_modes", ["political"]),
            )
            loaded += 1
        except Exception as e:
            print(f"  WARNING: skipped feature: {e}")
            skipped += 1

    return loaded, skipped


def _import_shapefile(
    path: str | Path,
    config: dict[str, Any],
    loader: Loader,
) -> tuple[int, int]:
    try:
        import fiona
        from shapely.geometry import shape as shapely_shape
    except ImportError:
        raise ImportError("fiona is required for shapefile import: pip install fiona")

    fields = config.get("fields", {})
    defaults = config.get("defaults", {})

    loaded = 0
    skipped = 0

    with fiona.open(path) as src:
        for feat in src:
            props = dict(feat["properties"] or {})
            try:
                slug = str(_extract_field(props, fields.get("slug")) or uuid.uuid4())[:32].replace(" ", "-").lower()
                name = str(_extract_field(props, fields.get("name")) or slug)
                entity_type = str(_extract_field(props, fields.get("type")) or defaults.get("type", "polity"))
                color = str(_extract_field(props, fields.get("color")) or defaults.get("color", "#888888"))
                year_start = int(_extract_field(props, fields.get("year_start")) or defaults.get("year_start", -500))
                year_end_raw = _extract_field(props, fields.get("year_end"))
                year_end = int(year_end_raw) if year_end_raw is not None else defaults.get("year_end")

                entity_id = loader.upsert_entity(slug, entity_type, color)
                loader.upsert_entity_name(entity_id, name, year_start, year_end)
                loader.delete_territories(entity_id)

                raw_geom = shapely_shape(feat["geometry"])
                geom = to_multipolygon(coerce_valid(raw_geom))
                if not validate_geom(geom):
                    print(f"  WARNING: invalid geometry for {slug}, skipping")
                    skipped += 1
                    continue

                simplified = simplify_geom(geom)
                loader.insert_territory(
                    entity_id,
                    geom.wkt,
                    simplified.wkt,
                    year_start,
                    year_end,
                    confidence_type=defaults.get("confidence_type", "approximate"),
                    confidence_score=defaults.get("confidence_score"),
                    source_name=config.get("source_name"),
                    source_url=config.get("source_url"),
                    source_license=config.get("source_license"),
                    data_version=config.get("data_version"),
                    resolution_km=defaults.get("resolution_km"),
                    importance=defaults.get("importance", 5),
                    map_modes=defaults.get("map_modes", ["political"]),
                )
                loaded += 1
            except Exception as e:
                print(f"  WARNING: skipped feature: {e}")
                skipped += 1

    return loaded, skipped


class Importer:
    def __init__(self, conn: psycopg2.extensions.connection, source_config_path: str | Path) -> None:
        self.conn = conn
        self.config = _load_source_config(source_config_path)
        self.loader = Loader(conn)

    def import_file(self, path: str | Path) -> tuple[int, int]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Import file not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".geojson" or suffix == ".json":
            loaded, skipped = _import_geojson(path, self.config, self.loader)
        elif suffix == ".shp":
            loaded, skipped = _import_shapefile(path, self.config, self.loader)
        else:
            raise ImportError(f"Unsupported file type: {suffix}. Use .geojson or .shp")

        self.conn.commit()
        return loaded, skipped
