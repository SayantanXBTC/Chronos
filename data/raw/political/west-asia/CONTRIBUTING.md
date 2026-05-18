# West Asia Region — Contributor Guide

Entities in this region: Achaemenid Persia, Parthian Empire, Sasanian Empire.

## Time Range
550 BCE – 651 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~100–200 km tolerance
- Caucasus and Central Asia frontiers: mark approximate

## Primary Sources
- Wiesehöfer, "Ancient Persia" for Achaemenid boundaries
- Bivar, "The History of Eastern Iran" (Cambridge History of Iran vol. 3)
- Greatrex & Lieu, "The Roman Eastern Frontier and the Persian Wars" for Sasanian frontiers

## Phase Guidelines
- Achaemenid: use satrapy boundaries; eastern satrapies are approximate
- Sasanian: core plateau is high-confidence; Caucasus and Arabian fringe are approximate
- Do not include full Silk Road sphere — only areas with administrative presence

## File Naming
`data/raw/political/west-asia/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
