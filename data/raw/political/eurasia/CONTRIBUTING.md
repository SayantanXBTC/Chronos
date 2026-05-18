# Eurasia Region — Contributor Guide

Entities in this region: Mongol Empire.

## Time Range
1206 CE – 1370 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~200 km tolerance (steppe frontiers are inherently diffuse)
- Steppe zones: prefer conservative estimates; nomadic range ≠ administered territory

## Primary Sources
- Morgan, "The Mongols" (2nd ed., 2007)
- Allsen, "Mongol Imperialism" for administrative geography
- Lane, "Genghis Khan and Mongol Rule" for early expansion

## Phase Guidelines
- Phase 1 (Genghis Khan): rapid expansion phase — use conservative eastern/western extents
- Phase 2 (post-1260 division): show unified empire only until kurultai fragmentation
- Do not show Khanate successor states in this entity — they get separate entries

## File Naming
`data/raw/political/eurasia/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
