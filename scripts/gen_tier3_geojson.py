"""
Generate Shapely-validated GeoJSON phase files for Tier 3 entities.

Regions created:
  data/raw/political/west-asia/sasanian-empire/
  data/raw/political/south-asia/mughal-empire/
  data/raw/political/africa/mali-empire/
  data/raw/political/africa/songhai-empire/
  data/raw/political/americas/inca-empire/
  data/raw/political/americas/aztec-empire/

Run from repo root:
  python scripts/gen_tier3_geojson.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from shapely.geometry import mapping, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


def mp(polys: list[list[tuple[float, float]]]) -> MultiPolygon:
    geom = unary_union([Polygon(p) for p in polys])
    geom = make_valid(geom)
    if geom.geom_type == "Polygon":
        geom = MultiPolygon([geom])
    return geom


def save(geom: MultiPolygon, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fc = {"type": "Feature", "properties": {}, "geometry": mapping(geom)}
    path.write_text(json.dumps(fc, indent=2))
    print(f"  wrote {path}")


ROOT = Path(__file__).parent.parent / "data" / "raw" / "political"


# ---------------------------------------------------------------------------
# Sasanian Empire (west-asia)
# Core: Persia/Iraq/Iran plateau; Phase 2 adds Armenia, parts of Arabia
# ---------------------------------------------------------------------------
SASANIAN_CORE = [
    (35.0, 24.0), (61.0, 24.0), (66.0, 28.0), (66.0, 40.0),
    (58.0, 44.0), (44.0, 42.0), (38.0, 38.0), (36.0, 30.0), (35.0, 24.0),
]
SASANIAN_PEAK_EXT = [
    (35.0, 24.0), (66.0, 24.0), (66.0, 42.0), (55.0, 46.0),
    (44.0, 44.0), (36.0, 40.0), (34.0, 34.0), (35.0, 24.0),
]

save(mp([SASANIAN_CORE]), ROOT / "west-asia/sasanian-empire/phase-1.geojson")
save(mp([SASANIAN_PEAK_EXT]), ROOT / "west-asia/sasanian-empire/phase-2.geojson")

# ---------------------------------------------------------------------------
# Mughal Empire (south-asia)
# Phase 1: Babur/Humayun — north India core
# Phase 2: Akbar/Shah Jahan — peak extent covering most of subcontinent
# ---------------------------------------------------------------------------
MUGHAL_CORE = [
    (70.0, 22.0), (88.0, 22.0), (88.0, 35.0), (72.0, 36.0),
    (68.0, 30.0), (70.0, 22.0),
]
MUGHAL_PEAK = [
    (60.0, 20.0), (92.0, 20.0), (92.0, 36.0), (70.0, 38.0),
    (60.0, 34.0), (60.0, 20.0),
]

save(mp([MUGHAL_CORE]), ROOT / "south-asia/mughal-empire/phase-1.geojson")
save(mp([MUGHAL_PEAK]), ROOT / "south-asia/mughal-empire/phase-2.geojson")

# ---------------------------------------------------------------------------
# Mali Empire (africa/west)
# Phase 1: Sundiata core — upper Niger bend
# Phase 2: Mansa Musa peak — extends to Atlantic coast and Sahara edge
# ---------------------------------------------------------------------------
MALI_CORE = [
    (-12.0, 9.0), (2.0, 9.0), (4.0, 15.0), (-4.0, 20.0),
    (-10.0, 18.0), (-14.0, 13.0), (-12.0, 9.0),
]
MALI_PEAK = [
    (-18.0, 10.0), (4.0, 10.0), (6.0, 17.0), (-2.0, 22.0),
    (-10.0, 22.0), (-18.0, 16.0), (-18.0, 10.0),
]

save(mp([MALI_CORE]), ROOT / "africa/mali-empire/phase-1.geojson")
save(mp([MALI_PEAK]), ROOT / "africa/mali-empire/phase-2.geojson")

# ---------------------------------------------------------------------------
# Songhai Empire (africa/west)
# Single peak phase: Niger bend from Timbuktu to Gao, extending east
# ---------------------------------------------------------------------------
SONGHAI = [
    (-8.0, 11.0), (6.0, 11.0), (14.0, 14.0), (10.0, 20.0),
    (-2.0, 22.0), (-8.0, 18.0), (-10.0, 14.0), (-8.0, 11.0),
]

save(mp([SONGHAI]), ROOT / "africa/songhai-empire/phase-1.geojson")

# ---------------------------------------------------------------------------
# Inca Empire (americas)
# Phase 1: Pachacuti core — Cuzco to Lake Titicaca
# Phase 2: Huayna Capac peak — from Ecuador to central Chile
# ---------------------------------------------------------------------------
INCA_CORE = [
    (-72.0, -14.0), (-68.0, -14.0), (-66.0, -20.0),
    (-70.0, -24.0), (-74.0, -18.0), (-72.0, -14.0),
]
INCA_PEAK = [
    (-78.0, 2.0), (-75.0, 2.0), (-73.0, 0.0),
    (-66.0, -20.0), (-66.0, -38.0), (-72.0, -40.0),
    (-76.0, -32.0), (-80.0, -18.0), (-80.0, 2.0), (-78.0, 2.0),
]

save(mp([INCA_CORE]), ROOT / "americas/inca-empire/phase-1.geojson")
save(mp([INCA_PEAK]), ROOT / "americas/inca-empire/phase-2.geojson")

# ---------------------------------------------------------------------------
# Aztec Empire (Triple Alliance) (americas)
# Single phase: Central Mexico — Valley of Mexico + tribute states
# ---------------------------------------------------------------------------
AZTEC = [
    (-104.0, 16.0), (-94.0, 16.0), (-92.0, 18.0),
    (-94.0, 22.0), (-100.0, 22.0), (-104.0, 20.0), (-104.0, 16.0),
]

save(mp([AZTEC]), ROOT / "americas/aztec-empire/phase-1.geojson")

print("\nTier 3 GeoJSON generation complete.")
