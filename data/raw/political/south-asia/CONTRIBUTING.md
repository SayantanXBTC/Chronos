# South Asia Region — Contributor Guide

Entities in this region: Maurya Empire, Gupta Empire, Mughal Empire.

## Time Range
350 BCE – 1857 CE

## Geometry Standards
- Coordinate system: WGS84 (EPSG:4326)
- Format: GeoJSON Feature with MultiPolygon geometry
- Resolution: ~100–200 km tolerance
- Deccan plateau coverage: include where direct administration is attested

## Primary Sources
- Schwartzberg, "A Historical Atlas of South Asia" (1978, 1992)
- IGNCA (Indira Gandhi National Centre for the Arts) digital atlas resources
- Indian History Congress published boundary reconstructions

## Phase Guidelines
- Maurya: distinguish Ashokan core from peripheral territories with lower confidence
- Gupta: northern plains are high-confidence; Deccan extent is lower-confidence
- Mughal: use subah (provincial) boundaries where documented; mark frontier zones approximate

## File Naming
`data/raw/political/south-asia/<slug>/phase-N.geojson`

Each phase file is a single GeoJSON Feature (not FeatureCollection).
