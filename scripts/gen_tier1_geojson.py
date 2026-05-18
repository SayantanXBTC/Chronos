"""Generate GeoJSON phase files for 5 Tier 1 entities."""
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
med = base / "mediterranean"
me = base / "middle-east"
eur = base / "eurasia"

print("== BYZANTINE EMPIRE ==")

byz_p1_balkans = [
    (14.0, 45.5), (30.0, 46.0), (32.0, 44.0), (30.5, 43.0),
    (26.5, 41.0), (26.0, 40.5), (22.5, 37.0), (20.0, 38.0),
    (19.5, 41.5), (14.5, 44.5), (14.0, 45.5),
]
byz_p1_anatolia = [
    (26.0, 41.0), (38.0, 42.0), (40.5, 40.0), (40.0, 37.5),
    (37.5, 36.5), (36.0, 35.5), (29.0, 36.0), (26.5, 37.5),
    (26.0, 39.0), (26.0, 41.0),
]
byz_p1_levant_egypt = [
    (35.5, 36.5), (38.5, 37.0), (42.0, 36.0), (42.5, 33.0),
    (38.0, 33.5), (36.5, 32.0), (35.5, 29.5), (35.5, 22.0),
    (24.5, 22.0), (24.0, 31.0), (32.0, 31.5), (35.5, 36.5),
]
byz_p1 = make_mp([byz_p1_balkans, byz_p1_anatolia, byz_p1_levant_egypt])
write(med / "byzantine-empire/phase-1.geojson", feature(byz_p1, {
    "year_start": 330, "year_end": 610, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

byz_p2_balkans = [
    (14.0, 45.5), (30.0, 46.0), (32.0, 44.0), (30.5, 43.0),
    (26.5, 41.0), (22.5, 37.0), (20.0, 38.0), (19.5, 41.5),
    (14.5, 44.5), (14.0, 45.5),
]
byz_p2_anatolia = [
    (26.0, 41.0), (38.0, 42.0), (40.0, 39.0), (38.5, 37.0),
    (36.5, 36.0), (29.0, 36.0), (26.5, 37.5), (26.0, 39.0),
    (26.0, 41.0),
]
byz_p2 = make_mp([byz_p2_balkans, byz_p2_anatolia])
write(med / "byzantine-empire/phase-2.geojson", feature(byz_p2, {
    "year_start": 610, "year_end": 1071, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

byz_p3_thrace = [
    (25.0, 42.0), (32.0, 43.0), (30.5, 41.0), (26.5, 40.5),
    (22.5, 37.0), (21.0, 38.0), (22.0, 40.5), (25.0, 42.0),
]
byz_p3_w_anatolia = [
    (26.5, 40.5), (32.0, 41.0), (32.0, 38.0), (27.0, 37.0),
    (26.5, 38.5), (26.5, 40.5),
]
byz_p3 = make_mp([byz_p3_thrace, byz_p3_w_anatolia])
write(med / "byzantine-empire/phase-3.geojson", feature(byz_p3, {
    "year_start": 1071, "year_end": 1453, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "conquest",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== OTTOMAN EMPIRE ==")

ott_p1_balkans = [
    (14.0, 45.5), (30.0, 46.0), (32.0, 44.0), (30.0, 42.0),
    (26.5, 41.0), (22.5, 37.0), (20.0, 38.5), (19.5, 41.5),
    (14.0, 45.5),
]
ott_p1_anatolia = [
    (26.5, 41.5), (36.0, 42.0), (38.0, 39.5), (38.0, 37.5),
    (36.5, 36.0), (29.0, 36.0), (26.5, 37.5), (26.5, 41.5),
]
ott_p1 = make_mp([ott_p1_balkans, ott_p1_anatolia])
write(me / "ottoman-empire/phase-1.geojson", feature(ott_p1, {
    "year_start": 1299, "year_end": 1453, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

ott_p2_europe = [
    (14.0, 48.0), (32.0, 48.5), (35.0, 47.5), (32.0, 44.0),
    (28.0, 41.5), (22.5, 37.0), (20.0, 38.5), (19.0, 42.0),
    (14.0, 48.0),
]
ott_p2_anatolia_levant = [
    (26.5, 42.0), (44.0, 42.0), (44.0, 36.5), (40.5, 29.5),
    (38.0, 33.0), (36.5, 36.0), (28.0, 37.0), (26.5, 38.5),
    (26.5, 42.0),
]
ott_p2_egypt_arabia = [
    (24.5, 22.0), (51.0, 22.0), (51.0, 30.0), (43.0, 31.0),
    (38.5, 31.0), (37.0, 30.5), (36.5, 32.0), (36.0, 30.0),
    (35.5, 24.0), (24.5, 24.0), (24.5, 22.0),
]
ott_p2_n_africa = [
    (-2.0, 35.5), (24.5, 33.5), (24.5, 27.0), (12.0, 27.0),
    (-2.0, 32.0), (-2.0, 35.5),
]
ott_p2 = make_mp([ott_p2_europe, ott_p2_anatolia_levant, ott_p2_egypt_arabia, ott_p2_n_africa])
write(me / "ottoman-empire/phase-2.geojson", feature(ott_p2, {
    "year_start": 1453, "year_end": 1683, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

ott_p3_europe = [
    (14.0, 46.5), (27.0, 47.0), (30.0, 44.0), (28.0, 41.5),
    (22.5, 37.0), (20.0, 38.5), (19.0, 41.5), (14.0, 46.5),
]
ott_p3_anatolia_levant = [
    (26.5, 42.0), (44.0, 42.0), (44.0, 36.5), (40.5, 29.5),
    (38.0, 33.0), (36.5, 36.0), (28.0, 37.0), (26.5, 38.5),
    (26.5, 42.0),
]
ott_p3_egypt_arabia = [
    (24.5, 22.0), (51.0, 22.0), (51.0, 30.0), (38.5, 31.0),
    (36.5, 32.0), (36.0, 30.0), (35.5, 24.0), (24.5, 24.0),
    (24.5, 22.0),
]
ott_p3_n_africa = [
    (-2.0, 35.5), (16.0, 33.5), (16.0, 27.0), (12.0, 27.0),
    (-2.0, 32.0), (-2.0, 35.5),
]
ott_p3 = make_mp([ott_p3_europe, ott_p3_anatolia_levant, ott_p3_egypt_arabia, ott_p3_n_africa])
write(me / "ottoman-empire/phase-3.geojson", feature(ott_p3, {
    "year_start": 1683, "year_end": 1922, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "administrative_reorganization",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== MONGOL EMPIRE ==")

mon_p1_core = [
    (44.0, 48.0), (135.0, 50.0), (135.0, 35.0), (110.0, 25.0),
    (72.0, 20.0), (56.0, 24.0), (44.0, 35.0), (40.0, 43.0),
    (44.0, 48.0),
]
mon_p1 = make_mp([mon_p1_core])
write(eur / "mongol-empire/phase-1.geojson", feature(mon_p1, {
    "year_start": 1206, "year_end": 1260, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

mon_p2_core = [
    (40.0, 50.0), (135.0, 52.0), (135.0, 35.0), (110.0, 22.0),
    (70.0, 19.0), (52.0, 23.0), (40.0, 35.0), (37.0, 42.0),
    (40.0, 50.0),
]
mon_p2_russia = [
    (35.0, 55.0), (65.0, 60.0), (75.0, 55.0), (60.0, 45.0),
    (44.0, 47.0), (35.0, 50.0), (35.0, 55.0),
]
mon_p2 = make_mp([mon_p2_core, mon_p2_russia])
write(eur / "mongol-empire/phase-2.geojson", feature(mon_p2, {
    "year_start": 1260, "year_end": 1368, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "partition",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== ABBASID CALIPHATE ==")

abb_p1_core = [
    (34.0, 37.5), (38.5, 38.0), (65.0, 44.0), (74.0, 35.0),
    (65.0, 23.0), (55.0, 22.0), (44.0, 12.0), (40.0, 12.0),
    (37.0, 16.0), (37.0, 29.0), (35.5, 30.5), (35.5, 35.0),
    (34.0, 37.5),
]
abb_p1_egypt = [
    (24.5, 22.0), (35.5, 22.0), (35.5, 31.5), (32.0, 31.5),
    (24.5, 31.0), (24.5, 22.0),
]
abb_p1_n_africa = [
    (7.5, 29.0), (35.0, 33.5), (34.5, 30.0), (24.5, 30.0),
    (12.0, 27.0), (7.5, 29.0),
]
abb_p1 = make_mp([abb_p1_core, abb_p1_egypt, abb_p1_n_africa])
write(me / "abbasid-caliphate/phase-1.geojson", feature(abb_p1, {
    "year_start": 750, "year_end": 900, "date_precision": "approximate",
    "confidence_type": "approximate",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

abb_p2_core = [
    (38.0, 35.0), (48.5, 36.0), (48.5, 29.0), (43.0, 27.0),
    (39.0, 29.0), (38.0, 32.0), (38.0, 35.0),
]
abb_p2 = make_mp([abb_p2_core])
write(me / "abbasid-caliphate/phase-2.geojson", feature(abb_p2, {
    "year_start": 900, "year_end": 1258, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "conquest",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("== UMAYYAD CALIPHATE ==")

uma_iberia = [
    (-9.0, 36.0), (-5.0, 36.0), (3.5, 41.5), (-0.5, 44.0),
    (-9.0, 43.5), (-9.0, 36.0),
]
uma_n_africa = [
    (-5.5, 30.0), (35.5, 30.5), (36.0, 22.0), (24.5, 22.0),
    (12.0, 23.5), (-5.5, 30.0),
]
uma_east = [
    (34.0, 37.5), (38.5, 38.0), (65.0, 44.0), (74.0, 35.0),
    (65.0, 23.0), (55.0, 22.0), (44.0, 12.0), (40.0, 12.0),
    (37.0, 16.0), (37.0, 29.0), (35.5, 30.5), (35.5, 35.0),
    (34.0, 37.5),
]
uma_p1 = make_mp([uma_iberia, uma_n_africa, uma_east])
write(me / "umayyad-caliphate/phase-1.geojson", feature(uma_p1, {
    "year_start": 661, "year_end": 750, "date_precision": "approximate",
    "confidence_type": "approximate",
    "end_event_type": "collapse",
    "source_name": "Manual trace — approximate historical boundaries",
    "source_license": "CC0",
}))

print("\nDone — all 11 GeoJSON files written.")
