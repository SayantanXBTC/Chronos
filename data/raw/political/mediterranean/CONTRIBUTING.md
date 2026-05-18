# Mediterranean Region — Contributor Guide

Entities in this region: Roman Republic, Roman Empire, Western Roman Empire, Eastern Roman Empire/Byzantine Empire, Macedonian Empire, Seleucid Empire, Ptolemaic Egypt, Greek City-States, Carthage, Numidia.

## Time Range
800 BCE – 1453 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~50–100 km tolerance acceptable for this era
- Coastlines should follow Mediterranean shoreline (modern, not paleo)

## Primary Sources
- Barrington Atlas of the Greek and Roman World (Talbert, 2000)
- AWMC (Ancient World Mapping Center) — awmc.unc.edu
- Pleiades Gazetteer for point references

## Phase Guidelines
- Roman Republic/Empire: use provincial boundaries where known
- Greek city-states: use Poleis territories, not just city points
- Do not project exact modern national borders onto ancient polities

## File Naming
`data/raw/political/mediterranean/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
