import json
import subprocess
import sys
from pathlib import Path

STYLE_PATH = Path("apps/web/public/map-style/historical.json")
MODERN_LAYER_PREFIXES = [
    "road_", "tunnel_", "bridge_", "building",
    "poi_", "airport", "highway-name", "highway-shield",
    "road_shield", "road_one_way",
    "aeroway_", "landuse_residential", "landuse_pitch",
    "landuse_track", "landuse_cemetery", "landuse_hospital",
    "landuse_school",
]

def test_no_modern_layers():
    style = json.loads(STYLE_PATH.read_text())
    layer_ids = [l["id"] for l in style["layers"]]
    violations = [lid for lid in layer_ids
                  if any(lid.startswith(p) or lid == p.rstrip("_") for p in MODERN_LAYER_PREFIXES)]
    assert not violations, f"Modern layers still present: {violations}"

def test_water_color_muted():
    style = json.loads(STYLE_PATH.read_text())
    water = next(l for l in style["layers"] if l["id"] == "water")
    assert water["paint"]["fill-color"] == "#6e9ab5"

def test_background_parchment():
    style = json.loads(STYLE_PATH.read_text())
    bg = next(l for l in style["layers"] if l["id"] == "background")
    assert bg["paint"]["background-color"] == "#cfc4a8"

def test_essential_layers_present():
    style = json.loads(STYLE_PATH.read_text())
    layer_ids = {l["id"] for l in style["layers"]}
    required = {"background", "water", "waterway_river", "natural_earth", "landcover_wood"}
    missing = required - layer_ids
    assert not missing, f"Required layers missing: {missing}"

if __name__ == "__main__":
    failures = []
    for name, fn in [(k, v) for k, v in globals().items() if k.startswith("test_")]:
        try:
            fn()
            print(f"  PASS {name}")
        except AssertionError as e:
            print(f"  FAIL {name}: {e}")
            failures.append(name)
    sys.exit(1 if failures else 0)
