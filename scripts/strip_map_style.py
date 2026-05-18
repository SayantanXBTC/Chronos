"""Regenerate apps/web/public/map-style/historical.json with modern layers removed."""
import json
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

COLOR_OVERRIDES = {
    "background": {"background-color": "#cfc4a8"},
    "water": {"fill-color": "#6e9ab5"},
    "waterway_river": {"line-color": "#5d8fa8"},
    "waterway_other": {"line-color": "#5d8fa8"},
    "waterway_tunnel": {"line-color": "#5d8fa8"},
}

def main():
    style = json.loads(STYLE_PATH.read_text(encoding="utf-8"))
    style["layers"] = [l for l in style["layers"] if l["id"] in KEEP_LAYERS]
    for layer in style["layers"]:
        if layer["id"] in COLOR_OVERRIDES:
            layer.setdefault("paint", {}).update(COLOR_OVERRIDES[layer["id"]])
    STYLE_PATH.write_text(json.dumps(style, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(style['layers'])} layers to {STYLE_PATH}")

if __name__ == "__main__":
    main()
