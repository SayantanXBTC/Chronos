# East Asia Region — Contributor Guide

Entities in this region: Qin Dynasty, Han Dynasty, Tang Dynasty.

## Time Range
300 BCE – 1000 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~100–200 km tolerance for this era and region size
- Include Tarim Basin where relevant (Han/Tang protectorates)

## Primary Sources
- CHGIS (China Historical GIS Project) — Harvard/Fudan — chgis.fas.harvard.edu
- Tan Qixiang, "Historical Atlas of China" (谭其骧历史地图集)
- Timothy Brook, "The Troubled Empire" (for Ming reference)

## Phase Guidelines
- Distinguish core territory from tributary/protectorate zones
- Korean peninsula: show only directly administered commanderies, not full tribute sphere
- Central Asia extent: show Dudu (Protectorate) boundary, not nomadic sphere of influence

## File Naming
`data/raw/political/east-asia/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
