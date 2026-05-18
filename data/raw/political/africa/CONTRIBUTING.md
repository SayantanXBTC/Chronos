# Africa Region — Contributor Guide

Entities in this region: Mali Empire, Songhai Empire.

## Time Range
1200 CE – 1600 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~200 km tolerance (source data is sparse)
- Saharan desert boundaries: mark as approximate/low-confidence; follow trade routes not geography

## Primary Sources
- Nehemia Levtzion, "Ancient Ghana and Mali" (1973)
- UNESCO "General History of Africa" vol. IV (Medieval period)
- Stride & Ifeka, "Peoples and Empires of West Africa"

## Phase Guidelines
- Mali: Mansa Musa's realm is best-documented — earlier phases are more speculative
- Songhai: Niger River valley core is high-confidence; peripheral tributaries are approximate
- Do not conflate sphere of influence with administered territory

## File Naming
`data/raw/political/africa/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
