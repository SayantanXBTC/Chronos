# Middle East Region — Contributor Guide

Entities in this region: Umayyad Caliphate, Abbasid Caliphate, Ottoman Empire.

## Time Range
600 CE – 1923 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~50–100 km tolerance; Ottoman era can use finer resolution
- Arabian peninsula desert zones: mark as approximate/low-confidence

## Primary Sources
- Al-Muqaddasi, "Ahsan al-Taqasim" for early Islamic geography
- Encyclopaedia of Islam (Brill) for administrative boundary descriptions
- Kiepert, "Formae Orbis Antiqui" (for classical reference)
- Ottoman survey maps (19th c.) for late-period Ottoman boundaries

## Phase Guidelines
- Umayyad/Abbasid: distinguish provinces (junds/wilayahs) from tribal zones
- Ottoman: use eyalet/vilayet boundaries where documented
- Nomadic tribal zones: prefer approximate confidence, wider polygons

## File Naming
`data/raw/political/middle-east/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
