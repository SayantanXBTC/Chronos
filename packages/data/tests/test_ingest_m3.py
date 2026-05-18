"""M3-J: Tests for M3 entity configs (Tier 2 + Tier 3) and pipeline integration."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_ENTITIES_DIR = Path(__file__).parent.parent / "entities"
_DATA_DIR = _REPO_ROOT / "data" / "raw" / "political"


def _load_all_entity_configs() -> list[dict]:
    configs = []
    for yml_file in sorted(_ENTITIES_DIR.glob("*.yml")):
        with open(yml_file) as f:
            configs.append(yaml.safe_load(f))
    return configs


TIER2_SLUGS = {"qin-dynasty", "han-dynasty", "tang-dynasty", "maurya-empire", "gupta-empire"}
TIER3_SLUGS = {"sasanian-empire", "mughal-empire", "mali-empire", "songhai-empire", "inca-empire", "aztec-empire"}


class TestTier2EntityConfigs:
    def test_all_tier2_entities_have_yaml(self):
        slugs = {c["slug"] for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            assert slug in slugs, f"Missing entity YAML: {slug}"

    def test_tier2_entities_have_required_fields(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            cfg = configs[slug]
            assert "name" in cfg
            assert "type" in cfg
            assert "color" in cfg
            assert "year_start" in cfg
            assert "year_end" in cfg
            assert "phases" in cfg
            assert len(cfg["phases"]) >= 1

    def test_tier2_entities_have_source_license(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            cfg = configs[slug]
            assert cfg.get("source_license"), f"{slug} missing source_license"

    def test_tier2_entities_have_importance(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            cfg = configs[slug]
            assert 1 <= cfg.get("importance", 0) <= 10, f"{slug} importance out of range"

    def test_tier2_geojson_files_exist(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            cfg = configs[slug]
            for phase in cfg["phases"]:
                matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
                assert matches, f"GeoJSON not found: {phase['geometry']}"

    def test_tier2_geojson_files_are_valid_json(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER2_SLUGS:
            cfg = configs[slug]
            for phase in cfg["phases"]:
                matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
                if matches:
                    with open(matches[0]) as f:
                        data = json.load(f)
                    assert "geometry" in data or "type" in data, f"Invalid GeoJSON: {phase['geometry']}"


class TestTier3EntityConfigs:
    def test_all_tier3_entities_have_yaml(self):
        slugs = {c["slug"] for c in _load_all_entity_configs()}
        for slug in TIER3_SLUGS:
            assert slug in slugs, f"Missing entity YAML: {slug}"

    def test_tier3_entities_have_required_fields(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER3_SLUGS:
            cfg = configs[slug]
            assert "name" in cfg
            assert "type" in cfg
            assert "phases" in cfg
            assert len(cfg["phases"]) >= 1

    def test_tier3_geojson_files_exist(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER3_SLUGS:
            cfg = configs[slug]
            for phase in cfg["phases"]:
                matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
                assert matches, f"GeoJSON not found: {phase['geometry']} (entity: {slug})"

    def test_tier3_geojson_have_valid_geometry_type(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        for slug in TIER3_SLUGS:
            cfg = configs[slug]
            for phase in cfg["phases"]:
                matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
                if matches:
                    with open(matches[0]) as f:
                        data = json.load(f)
                    geom = data.get("geometry", {})
                    assert geom.get("type") in ("MultiPolygon", "Polygon"), \
                        f"Unexpected geometry type in {phase['geometry']}: {geom.get('type')}"

    def test_inca_empire_spans_south_america(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        cfg = configs["inca-empire"]
        for phase in cfg["phases"]:
            matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
            if matches:
                with open(matches[0]) as f:
                    data = json.load(f)
                from shapely.geometry import shape
                geom = shape(data["geometry"])
                bounds = geom.bounds  # (minx, miny, maxx, maxy)
                # Inca should be in western South America (lon < -60, lat < 10)
                assert bounds[0] < -60, "Inca empire should be west of -60°"
                assert bounds[1] < -10, "Inca empire should extend south of -10°"
                break

    def test_aztec_empire_in_central_mexico(self):
        configs = {c["slug"]: c for c in _load_all_entity_configs()}
        cfg = configs["aztec-empire"]
        for phase in cfg["phases"]:
            matches = list(_DATA_DIR.glob(f"**/{phase['geometry']}"))
            if matches:
                with open(matches[0]) as f:
                    data = json.load(f)
                from shapely.geometry import shape
                geom = shape(data["geometry"])
                cx, cy = geom.centroid.x, geom.centroid.y
                assert -110 < cx < -90, f"Aztec centroid lon unexpected: {cx}"
                assert 14 < cy < 25, f"Aztec centroid lat unexpected: {cy}"
                break


class TestAllEntitiesYearConsistency:
    def test_year_start_before_year_end(self):
        for cfg in _load_all_entity_configs():
            if cfg.get("year_end") is not None:
                assert cfg["year_start"] < cfg["year_end"], \
                    f"{cfg['slug']}: year_start {cfg['year_start']} >= year_end {cfg['year_end']}"

    def test_phases_within_entity_year_range(self):
        for cfg in _load_all_entity_configs():
            y_start = cfg.get("year_start")
            y_end = cfg.get("year_end")
            if y_start is None or y_end is None:
                continue
            for phase in cfg.get("phases", []):
                assert phase["year_start"] >= y_start, \
                    f"{cfg['slug']} phase starts before entity: {phase['year_start']} < {y_start}"
                if phase.get("year_end") is not None:
                    assert phase["year_end"] <= y_end, \
                        f"{cfg['slug']} phase ends after entity: {phase['year_end']} > {y_end}"

    def test_total_entity_count_at_least_twenty(self):
        configs = _load_all_entity_configs()
        assert len(configs) >= 20, f"Expected ≥20 entities, got {len(configs)}"
