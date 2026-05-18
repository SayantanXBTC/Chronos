# Americas Region — Contributor Guide

Entities in this region: Inca Empire (Tawantinsuyu), Aztec Empire (Triple Alliance).

## Time Range
1400 CE – 1533 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~100–200 km tolerance
- Andean spine: follow Cordillera extent; Amazon lowlands are approximate

## Primary Sources
- Rowe, "Inca Culture at the Time of the Spanish Conquest" (Handbook of South American Indians)
- Berdan & Anawalt, "The Essential Codex Mendoza" for Aztec tribute provinces
- Smith, "The Aztecs" (2003) for Triple Alliance territory
- D'Altroy, "The Incas" (2002) for Tawantinsuyu provincial system

## Phase Guidelines
- Inca: use the four suyus as a guide; Antisuyu (jungle) extent is lower-confidence
- Aztec: show core Triple Alliance territory plus confirmed tribute provinces
- Mark post-1492 period territories as approximate given rapid colonial disruption

## File Naming
`data/raw/political/americas/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
