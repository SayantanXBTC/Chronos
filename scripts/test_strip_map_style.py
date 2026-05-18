import json
import sys
from pathlib import Path

STYLE_PATH = Path("apps/web/public/map-style/historical.json")

KEEP_LAYERS = {
    "background", "natural_earth",
    "park", "park_outline",
    "landcover_wood", "landcover_grass", "landcover_ice",
    "landcover_wetland", "landcover_sand",
    "waterway_tunnel", "waterway_river", "waterway_other",
    "water",
}

def test_exact_layer_set():
    style = json.loads(STYLE_PATH.read_text())
    actual = {l["id"] for l in style["layers"]}
    assert actual == KEEP_LAYERS, f"Unexpected: {actual - KEEP_LAYERS}, missing: {KEEP_LAYERS - actual}"

COLOR_OVERRIDES_EXPECTED = {
    "background":    ("background-color", "#cfc4a8"),
    "water":         ("fill-color",       "#6e9ab5"),
    "waterway_river": ("line-color",      "#5d8fa8"),
    "waterway_other": ("line-color",      "#5d8fa8"),
    "waterway_tunnel": ("line-color",     "#5d8fa8"),
}

def test_all_color_overrides():
    style = json.loads(STYLE_PATH.read_text())
    layers_by_id = {l["id"]: l for l in style["layers"]}
    for layer_id, (prop, expected_val) in COLOR_OVERRIDES_EXPECTED.items():
        actual = layers_by_id[layer_id]["paint"][prop]
        assert actual == expected_val, f"{layer_id}.{prop}: expected {expected_val}, got {actual}"

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
