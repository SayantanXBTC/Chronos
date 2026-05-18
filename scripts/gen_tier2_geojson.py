"""Generate GeoJSON phase files for 5 Tier 2 entities."""
import json
from pathlib import Path
import shapely
from shapely.geometry import MultiPolygon, Polygon, mapping


def make_mp(poly_coords_list):
    polys = [Polygon(c) for c in poly_coords_list]
    mp = MultiPolygon(polys)
    if not mp.is_valid:
        mp = shapely.make_valid(mp)
    if mp.geom_type == "Polygon":
        mp = MultiPolygon([mp])
    elif mp.geom_type == "GeometryCollection":
        parts = [g for g in mp.geoms if g.geom_type == "Polygon"]
        mp = MultiPolygon(parts) if parts else MultiPolygon([Polygon(poly_coords_list[0])])
    return mp


def feature(mp, props):
    return {"type": "Feature", "geometry": mapping(mp), "properties": props}


def write(path, feat):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(feat, indent=2))
    print(f"  wrote {path}")


base = Path("data/raw/political")
ea = base / "east-asia"
sa = base / "south-asia"

print("== QIN DYNASTY ==")

# Unified China 221-206 BCE — first imperial unification
qin_core = [
    (100.0, 40.0), (110.5, 42.5), (121.0, 42.0), (122.0, 37.0),
    (121.5, 28.0), (116.0, 22.5), (109.0, 21.0), (103.5, 22.5),
    (100.5, 25.0), (98.0, 32.0), (100.0, 40.0),
]
qin_p1 = make_mp([qin_core])
write(ea / "qin-dynasty/phase-1.geojson", feature(qin_p1, {
    "year_start": -221, "year_end": -206, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "collapse",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== HAN DYNASTY ==")

# Phase 1: Western Han consolidation 206-87 BCE
han_p1_core = [
    (100.0, 40.0), (110.5, 42.5), (121.0, 42.0), (122.0, 37.0),
    (121.5, 28.0), (116.0, 22.5), (109.0, 21.0), (103.5, 22.5),
    (100.5, 25.0), (98.0, 32.0), (100.0, 40.0),
]
han_p1_vietnam = [
    (103.5, 22.5), (108.5, 21.0), (108.0, 17.0), (104.0, 17.5),
    (102.5, 19.5), (103.5, 22.5),
]
han_p1 = make_mp([han_p1_core, han_p1_vietnam])
write(ea / "han-dynasty/phase-1.geojson", feature(han_p1, {
    "year_start": -206, "year_end": -87, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

# Phase 2: Western Han peak + Eastern Han 87 BCE-220 CE
# Expansion into Tarim Basin, northern Korea, deeper Vietnam
han_p2_core = [
    (98.0, 42.0), (110.5, 44.5), (121.0, 42.0), (122.0, 37.0),
    (121.5, 28.0), (116.0, 22.5), (109.0, 21.0), (103.5, 22.5),
    (100.5, 25.0), (96.0, 36.0), (98.0, 42.0),
]
han_p2_tarim = [
    (76.0, 44.0), (84.0, 46.0), (92.0, 44.0), (94.0, 38.0),
    (88.0, 35.0), (80.0, 37.0), (76.0, 40.0), (76.0, 44.0),
]
han_p2_korea = [
    (121.0, 42.0), (129.0, 42.0), (129.0, 37.5), (126.5, 37.0),
    (124.5, 38.5), (121.0, 42.0),
]
han_p2_vietnam = [
    (103.5, 22.5), (108.5, 21.0), (107.5, 16.5), (104.0, 17.0),
    (102.5, 19.5), (103.5, 22.5),
]
han_p2 = make_mp([han_p2_core, han_p2_tarim, han_p2_korea, han_p2_vietnam])
write(ea / "han-dynasty/phase-2.geojson", feature(han_p2, {
    "year_start": -87, "year_end": 220, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "partition",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== TANG DYNASTY ==")

# Phase 1: Tang peak 618-755 CE — maximum Central Asian extent
tang_p1_core = [
    (98.0, 44.0), (112.0, 47.0), (121.0, 43.0), (122.0, 38.0),
    (121.5, 28.0), (116.0, 22.0), (109.0, 21.0), (103.5, 22.5),
    (100.5, 25.0), (97.0, 33.0), (98.0, 44.0),
]
tang_p1_central_asia = [
    (62.0, 44.0), (76.0, 45.0), (84.0, 47.0), (90.0, 44.0),
    (92.0, 39.0), (86.0, 35.0), (78.0, 34.0), (72.0, 37.0),
    (66.0, 40.0), (62.0, 42.0), (62.0, 44.0),
]
tang_p1_korea = [
    (121.0, 43.0), (129.0, 42.0), (129.0, 37.0), (126.0, 35.5),
    (124.5, 38.0), (121.0, 43.0),
]
tang_p1_vietnam = [
    (103.5, 22.5), (108.5, 21.0), (107.5, 17.0), (104.0, 17.5),
    (102.5, 20.0), (103.5, 22.5),
]
tang_p1 = make_mp([tang_p1_core, tang_p1_central_asia, tang_p1_korea, tang_p1_vietnam])
write(ea / "tang-dynasty/phase-1.geojson", feature(tang_p1, {
    "year_start": 618, "year_end": 755, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

# Phase 2: Late Tang 755-907 CE — lost Central Asia after An Lushan rebellion
tang_p2_core = [
    (100.0, 42.0), (112.0, 44.5), (121.0, 42.0), (122.0, 37.0),
    (121.5, 28.0), (116.0, 22.0), (109.0, 21.0), (103.5, 22.5),
    (100.5, 25.0), (98.0, 33.0), (100.0, 42.0),
]
tang_p2_vietnam = [
    (103.5, 22.5), (108.5, 21.0), (107.5, 17.0), (104.0, 17.5),
    (102.5, 20.0), (103.5, 22.5),
]
tang_p2 = make_mp([tang_p2_core, tang_p2_vietnam])
write(ea / "tang-dynasty/phase-2.geojson", feature(tang_p2, {
    "year_start": 755, "year_end": 907, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "collapse",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== MAURYA EMPIRE ==")

# Phase 1: Early Maurya 322-268 BCE — north India, Ganges plain, northwest
maurya_p1 = [
    (66.0, 36.0), (76.0, 37.5), (82.0, 36.0), (88.0, 34.0),
    (92.0, 27.0), (88.0, 22.0), (82.0, 16.0), (76.0, 14.5),
    (73.5, 16.0), (70.5, 22.0), (65.5, 28.0), (64.5, 32.0),
    (66.0, 36.0),
]
mau_p1 = make_mp([maurya_p1])
write(sa / "maurya-empire/phase-1.geojson", feature(mau_p1, {
    "year_start": -322, "year_end": -268, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

# Phase 2: Ashoka's Maurya 268-185 BCE — near full subcontinent
maurya_p2 = [
    (66.0, 36.0), (76.0, 37.5), (82.0, 36.0), (88.0, 34.0),
    (92.0, 27.0), (88.0, 22.0), (84.0, 14.0), (79.0, 9.5),
    (77.0, 8.5), (74.0, 12.0), (72.5, 18.0), (68.5, 22.0),
    (65.5, 28.0), (64.5, 32.0), (66.0, 36.0),
]
mau_p2 = make_mp([maurya_p2])
write(sa / "maurya-empire/phase-2.geojson", feature(mau_p2, {
    "year_start": -268, "year_end": -185, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "collapse",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== GUPTA EMPIRE ==")

# Phase 1: Gupta rise and peak 320-415 CE — northern India
gupta_p1 = [
    (70.5, 34.0), (76.0, 34.5), (82.0, 32.0), (88.0, 28.0),
    (92.0, 24.0), (88.0, 20.0), (82.0, 16.0), (76.0, 16.0),
    (72.5, 20.0), (70.0, 26.0), (68.5, 30.0), (70.5, 34.0),
]
gup_p1 = make_mp([gupta_p1])
write(sa / "gupta-empire/phase-1.geojson", feature(gup_p1, {
    "year_start": 320, "year_end": 415, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

# Phase 2: Gupta decline 415-550 CE — mainly Gangetic plain
gupta_p2 = [
    (74.0, 30.5), (80.0, 30.5), (84.5, 27.5), (88.0, 26.0),
    (88.0, 22.0), (84.0, 22.0), (80.0, 24.0), (76.0, 26.0),
    (74.0, 28.0), (74.0, 30.5),
]
gup_p2 = make_mp([gupta_p2])
write(sa / "gupta-empire/phase-2.geojson", feature(gup_p2, {
    "year_start": 415, "year_end": 550, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "collapse",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("\nDone — all 9 GeoJSON files written.")
