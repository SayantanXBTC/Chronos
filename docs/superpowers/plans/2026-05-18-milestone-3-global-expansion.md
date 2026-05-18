# Milestone 3 — Global Historical Expansion Planning Document

**Date:** 2026-05-18  
**Status:** Planning  
**Goal:** Transform from Mediterranean/Classical prototype into a genuinely global historical timeline engine.  
**Scope:** Data engineering, ingestion scaling, temporal expansion, rendering scalability, foundational schema for historical rigor. No AI, no vector tiles, no animation.

---

## 1. Global Data Acquisition Strategy

### Source Inventory

| Source | Coverage | Temporal Range | License | GIS Quality | Difficulty |
|--------|----------|---------------|---------|-------------|------------|
| **AWMC** | Mediterranean, Near East | 500 BCE–500 CE | CC BY-NC | High — peer reviewed | Low — clean SHP/GeoJSON |
| **OpenHistoricalMap (OHM)** | Global (sparse) | Any | ODbL | Variable — crowdsourced | Medium — export via Overpass |
| **cShapes 2.0** | Global states | 1886–2019 CE | CC BY | High — academic | Low — direct SHP download |
| **Euratlas** | Europe + Near East | 1–2000 CE (century intervals) | Commercial | High — hand-traced | High — commercial, manual trace |
| **Natural Earth** | Global physical | Modern only | Public domain | High | Low — already GeoJSON |
| **Pleiades** | Mediterranean places | Antiquity | CC BY | High | Medium — JSON API |
| **World Historical Gazetteer (WHG)** | Global place names | Any | CC BY | Medium | Medium — Linked Pasts format |
| **HGIS de las Indias** | Latin America | 1519–1812 | CC BY | High | Low — SHP available |
| **CHGIS (Harvard CGA)** | China | 221 BCE–2000 CE | CC BY-NC | High — academic | Medium — SHP + docs |
| **Georeferenced Historical Vector Data (GVHD)** | Asia + Middle East | Varies | Mixed | Variable | High |
| **Manual atlas tracing** | Any | Any | None | Low–Medium | Very High |

### Acquisition Priority Order

**Phase A — Free, clean, immediately ingestible:**
1. cShapes 2.0 → modern-era states (post-1886), anchors any entity touching modern period
2. AWMC → validates/replaces current Mediterranean hand-drawn polys
3. Natural Earth → coastlines, rivers, lakes for physical layer upgrade
4. WHG → place names expansion (global ancient gazetteer)

**Phase B — Free but requiring processing:**
5. OpenHistoricalMap → global medieval/ancient, export by bbox + time
6. HGIS de las Indias → pre-Columbian + colonial Americas
7. CHGIS → East Asian dynasties (Han, Tang, Song, Ming, Qing)
8. Pleiades → Mediterranean places supplement

**Phase C — Manual / semi-manual:**
9. Academic atlas tracing → India, sub-Saharan Africa, pre-CHGIS East Asia
10. Euratlas (if licensed) → highest quality for Europe 1–2000 CE

### Licensing Strategy

All ingested data needs `source_license` field populated (already in schema). Add license validation to schema linter. Reject rows with `source_license = NULL` from external sources. Flag `CC BY-NC` sources in registry — prohibits commercial use of downstream product.

---

## 2. Civilization Expansion Roadmap

### Entity Priority (by data availability × historical significance)

**Tier 1 — Data exists, ingest immediately:**
- Byzantine Empire (AWMC partial, OHM good)
- Ottoman Empire (OHM, cShapes for late period)
- Mongol Empire (OHM — well traced)
- Abbasid Caliphate (OHM)
- Umayyad Caliphate (OHM)

**Tier 2 — Requires sourcing/tracing, high priority:**
- Han Dynasty (CHGIS)
- Tang Dynasty (CHGIS)
- Qin Dynasty (CHGIS)
- Maurya Empire (B.C. Law's historical geography — manual trace)
- Gupta Empire (same)

**Tier 3 — Requires careful sourcing, best-effort:**
- Song/Ming/Qing dynasties (CHGIS)
- Mughal Empire (partial OHM)
- Sasanian Empire (partial OHM, AWMC edges)
- Mali Empire / Songhai Empire (academic manual only)
- Aztec Empire (HGIS adjacent datasets)
- Inca Empire (HGIS adjacent datasets)

### State-Type Taxonomy (see §16)

Each new entity must declare a `type` from the standardized taxonomy before ingest. Pre-assign:

| Entity | Type |
|--------|------|
| Byzantine Empire | empire |
| Ottoman Empire | sultanate |
| Mongol Empire | nomadic_empire |
| Abbasid / Umayyad Caliphate | caliphate |
| Han / Tang / Ming / Qing | dynasty |
| Qin | empire |
| Maurya / Gupta / Mughal | empire |
| Mali / Songhai | kingdom |
| Aztec | empire |
| Inca | empire |
| Sasanian | empire |

### Lineage Declarations (see §15)

Along with each entity ingest, declare lineage links:

| Parent | Relationship | Child | Year |
|--------|-------------|-------|------|
| roman-republic | evolved_into | roman-empire | -27 |
| roman-empire | split_from | western-roman-empire | 285 |
| roman-empire | continuation | eastern-roman-empire | 285 |
| eastern-roman-empire | continuation | byzantine-empire | 330 |
| mongol-empire | split_from | yuan-dynasty | 1271 |
| umayyad-caliphate | successor | abbasid-caliphate | 750 |

### Recommended Phase Slugs

```
han-dynasty        tang-dynasty       qin-dynasty
byzantine-empire   ottoman-empire     mongol-empire
umayyad-caliphate  abbasid-caliphate  maurya-empire
gupta-empire       mughal-empire      sasanian-empire
mali-empire        songhai-empire     aztec-empire
inca-empire
```

---

## 3. Temporal Expansion Strategy

### Current State

`SNAPSHOT_YEARS` in `app/services/world_state.py`:
```python
SNAPSHOT_YEARS = [y for y in range(-500, 501, 25) if y != 0]  # 40 snapshots
```

Slider: 0–5025 (maps -3000 → 2026). UI ready. Backend not ready.

### Recommended Approach: Adaptive Density

```
-3000 to -1000 BCE  →  250-year intervals  (8 snapshots)
-1000 to -500 BCE   →  100-year intervals  (5 snapshots)
-500 to  500 CE     →  25-year intervals   (40 snapshots — current)
 500 to 1500 CE     →  50-year intervals   (20 snapshots)
1500 to 1900 CE     →  25-year intervals   (16 snapshots)
1900 to 2026 CE     →  10-year intervals   (13 snapshots)
```

Total: ~102 snapshots vs 200 for naive fixed 25-year.

Implementation: replace `range(-500, 501, 25)` with explicit list or generator. `snap_to_snapshot()` already handles arbitrary lists.

### Temporal Uncertainty Integration

Snapshot snapping must account for date precision (see §17). When `date_precision = 'estimated'`, display soft UI indicator on timeline (future M4 feature). Backend stores precision but does not alter snapshot logic in M3.

### Year 0 Skip

Already handled. Slider math in `lib/year.ts` skips year 0. API validates `year != 0`.

### Migration Points

No DB schema change for snapshots — computed at query time. Update in:
- `apps/api/app/services/world_state.py`
- `apps/api/app/utils/year.py`
- `apps/web/lib/year.ts` `SNAPSHOT_YEARS`

---

## 4. Snapshot Scalability Analysis

### Current Baseline (M2)

- ~13 entities × 40 snapshots = 520 theoretical territory rows
- API response: ~15–40KB per snapshot at global bbox
- Redis TTL: 5 min, ~50 cache keys active at any time

### M3 Projected (50 entities, 102 snapshots)

- Max concurrent entities at any snapshot: ~15–25 (empires rise and fall)
- Payload at zoom 4: `simplified_geom` + properties × 20 entities ≈ 80–200KB per call
- Redis: 102 × 2 zoom tiers × 1 world bbox = 204 keys × ~100KB avg = **~20MB Redis**. Acceptable.

### Concern Thresholds

- **>500KB API payload**: mobile will feel it. Occurs when >50 complex polygons at once.
- **>500 concurrent entities globally**: viewport partitioning required. Not M3.
- **>5000 territory rows**: PostGIS GIST index handles to ~100K rows fine.

### PostGIS Index Strategy

Add composite index in migration 0003:
```sql
CREATE INDEX territories_geom_gist ON territories USING GIST(geom);
CREATE INDEX territories_geom_lo_gist ON territories USING GIST(geom_lo);
CREATE INDEX territories_year_start_end_idx ON territories (year_start, year_end)
  WHERE year_end IS NOT NULL;
CREATE INDEX place_names_importance_idx ON place_names(importance);
```

---

## 5. Global Ingestion Pipeline Architecture

### Current Pipeline (Keeps)

```
data/raw/political/<region>/<slug>/phase-N.geojson  →  ingest.py  →  loader.py  →  PostGIS
data/raw/physical/rivers.geojson                    →  rivers_loader.py          →  PostGIS
data/raw/place_names/ancient_cities.csv             →  place_names_loader.py     →  PostGIS
External SHP/GeoJSON                                →  importer.py               →  PostGIS
```

### M3 Additions

**Source registry:** `packages/data/sources/registry.yaml`

```yaml
sources:
  - id: cshapes-2.0
    name: cShapes 2.0
    url: https://icr.ethz.ch/data/cshapes/cshapes_2.0.zip
    sha256: <checksum>
    license: CC BY
    format: shapefile
    config: packages/data/sources/cshapes.yaml
    target_file: cshapes/cshapes_2.0.shp
```

**`fetch_sources.py`**: downloads registry entries, verifies SHA256, saves to `data/sources/<id>/`.

**Ingest CLI expansion:**
```bash
python -m data ingest --source cshapes-2.0
python -m data ingest --all-sources
python -m data ingest --entity roman-empire  # unchanged
python -m data lineage --declare lineage.yaml  # new: batch-declare entity_lineages
```

### File Organization at Scale

Partition `data/raw/political/` by region:
```
data/raw/political/
  mediterranean/    east-asia/    south-asia/
  middle-east/      americas/     africa/     eurasia/
```

Change ingest glob from `data/raw/political/*/` to `data/raw/political/**/**/` (recursive). No other code changes.

---

## 6. Geometry Simplification + LOD Strategy

### Recommended: 3-Tier LOD at Ingest Time

Add `geom_lo` column (migration 0003):
```sql
ALTER TABLE territories ADD COLUMN geom_lo geometry(MultiPolygon, 4326);
```

Ingest produces 3 tiers:
```python
TOLERANCE_HI  = 0.01   # zoom ≥ 9 — full detail
TOLERANCE_MED = 0.05   # zoom 5–8 — current simplified_geom
TOLERANCE_LO  = 0.5    # zoom ≤ 4 — coarse for world view
```

Query selects tier by zoom:
```sql
ST_AsGeoJSON(
  CASE
    WHEN :zoom >= 9 THEN t.geom
    WHEN :zoom >= 5 THEN t.simplified_geom
    ELSE t.geom_lo
  END
) AS geometry
```

Area filter at low zoom:
```sql
AND (:zoom >= 5 OR ST_Area(t.geom_lo) > 1.0)
```

### Adaptive Tolerance

```python
def adaptive_tolerance(zoom_target: int) -> float:
    pixels_per_degree = 256 * (2 ** zoom_target) / 360
    return 2.0 / pixels_per_degree
```

### Vertex Budget Enforcement

```python
MAX_VERTICES_LO = 1000
if geom_lo.geom.count_coordinates() > MAX_VERTICES_LO:
    geom_lo = geom_lo.simplify(tolerance * 2, preserve_topology=True)
```

---

## 7. Place Name Scaling Strategy

### Target: ~500–2000 globally (M3)

**Sources:**
- Pleiades → filter importance ≥ 5, convert JSON → CSV
- WHG → global medieval/ancient places
- GeoNames → modern city anchors for post-1500 CE
- Manual curation → East Asia, India, Americas

### Temporal Integrity

No two rows share `(lon, lat, name)` with overlapping time ranges. Enforce in validate.py.

### Label Density (API-level zoom filter)

```python
# place_names service
if zoom <= 3:
    WHERE importance >= 8
elif zoom <= 5:
    WHERE importance >= 6
else:
    WHERE importance >= 3
```

### Schema Additions

```sql
ALTER TABLE place_names ADD COLUMN name_local TEXT;     -- 長安, Κωνσταντινούπολις
ALTER TABLE place_names ADD COLUMN date_precision TEXT  -- exact/approximate/estimated
  NOT NULL DEFAULT 'approximate'
  CHECK (date_precision IN ('exact', 'approximate', 'estimated'));
```

---

## 8. Frontend Rendering Scalability Analysis

### MapLibre Performance Limits

| Polygons | Vertices total | Zoom behavior | Acceptable? |
|----------|---------------|---------------|-------------|
| ~20 | ~5K | Instant | Yes (M2 current) |
| ~50 | ~50K | Slight lag on pan | Yes |
| ~100 | ~200K | 100–300ms frame drops | Borderline |
| ~200+ | ~500K+ | Visible jank | No |

M3 realistic max at any snapshot: ~25–40 entities × ~500 vertices (geom_lo) = ~12,500 vertices. Within limits.

### Layer Z-Order (M3)

rivers-line → territories-fill → place-names-symbol (unchanged). Add `fill-opacity` interpolation on territories layer for overlapping empires.

### When Vector Tiles Become Unavoidable

>200 concurrent entities with full geometry = M7. Architecture guard now: keep source type configurable in `MapView.tsx`, never hardcode `"type": "geojson"` as sole path.

---

## 9. API Scalability Considerations

### Redis Caching Revision

204 keys × ~100KB avg = ~20MB Redis. Set `maxmemory 512mb` + `maxmemory-policy allkeys-lru` in Docker config.

### Response Compression

```python
# app/main.py
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

100KB GeoJSON → ~15KB gzip. Critical at global scale.

### Debug/Admin Endpoints (Developer-Only)

Add to `apps/api/app/routers/debug.py` — mounted at `/api/v1/debug/`, no auth but documented as internal:
```
GET /api/v1/debug/geometry?entity=<slug>   → geometry validity stats for entity
GET /api/v1/admin/stats                    → entity/territory/place_name counts by region
GET /api/v1/admin/coverage                 → region_coverage table dump
```

These endpoints are excluded from public API docs (`include_in_schema=False`).

---

## 10. Regional Loading Architecture

### M3 Preparation (Implement)

Frontend `MapContainer.tsx` passes actual viewport bbox from MapLibre instead of world bbox:
```typescript
const bounds = map.getBounds()
const bbox = [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()]
```

Full viewport partitioning → M6+. Continent-level Redis key sharding → defer.

---

## 11. Data Quality + Validation Workflows

### M2 Baseline

- `validate_geom()` — Shapely `is_valid`
- `coerce_valid()` — auto-repair via `make_valid()`
- Invalid geometries logged + skipped

### M3 Additions to `packages/data/validate.py`

```python
# Checks:
# 1. source_license non-null for external sources
# 2. year_start < year_end (when year_end not null)
# 3. color is valid hex (#[0-9A-Fa-f]{6})
# 4. importance in [1, 10]
# 5. confidence_type in {'exact','approximate','inferred','disputed'}
# 6. date_precision in {'exact','approximate','estimated'}
# 7. entity type in VALID_ENTITY_TYPES (see §16)
# 8. end_event_type in VALID_EVENT_TYPES or null (see §18)
# 9. WGS84 bounds: lon -180→180, lat -90→90
# 10. no self-intersecting rings
# 11. area > 0
# 12. no duplicate (lon, lat, name) with overlapping time ranges [place_names only]
```

### QA Tooling (see §20)

```bash
python -m data validate data/raw/political/east-asia/han-dynasty/phase-1.geojson
python -m data validate --all              # validate all raw files
python -m data qa --check-overlaps         # spatial + temporal overlap detection
python -m data qa --invalid-geoms          # list invalid geometries in DB
python -m data qa --temporal-gaps          # entities with year gaps between phases
python -m data stats                       # entity/territory/place_name counts by region + year range
python -m data diff --entity roman-empire  # DB state vs raw GeoJSON
python -m data audit --source cshapes-2.0  # all entities from given source
```

### CI Integration

```yaml
# .github/workflows/data-validate.yml
- run: python -m data validate --all
- run: python -m data qa --check-overlaps --fail-on-error
```

---

## 12. Contributor Workflow Recommendations

### Checklist for New Entity

1. Assign slug + type from taxonomy (§16)
2. Declare lineage links in `packages/data/lineages/<slug>.yaml` (§15)
3. Create `data/raw/political/<region>/<slug>/phase-N.geojson`
4. GeoJSON properties must include: `year_start`, `year_end`, `source_name`, `source_url`, `source_license`
5. Set `end_event_type` on phases that end via known historical event (§18)
6. Run `python -m data validate data/raw/political/<region>/<slug>/`
7. Run `python -m data ingest --entity <slug>`
8. Run `python -m data lineage --declare packages/data/lineages/<slug>.yaml`
9. Verify entity renders at correct years in dev map

### Source Provenance Enforcement

- External sources: `source_license` required, `source_url` required
- Manual traces: `source_name = "Manual trace from [Atlas Title, Year]"`, `confidence_type = "approximate"`, `date_precision = "estimated"`
- Reject PRs failing validate CI

### Geometry Versioning

GeoJSON tracked in git — git history is geometry history. Breaking re-trace → increment phase number. No additional tooling needed for MVP.

### Simplification Philosophy Reference

Contributors must read `docs/HISTORICAL_PHILOSOPHY.md` (§22) before submitting boundaries.

---

## 13. Risks of Global Expansion

### Data Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| No free dataset for East Asia pre-1000 CE | High | High | CHGIS + manual trace; accept approximate |
| OHM quality inconsistent across regions | High | Medium | Pre-ingest validation; skip bad features |
| Licensing violation (CC BY-NC downstream) | Medium | High | Source registry flags commercial-restricted sources |
| Temporal gaps (entity active, no GeoJSON) | High | Low | Entity listed but no territory renders — acceptable |
| CRS mismatch in external datasets | Low | High | Validate WGS84 at import |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Complex Mongol Empire polygon tanks API | Medium | High | Vertex budget enforcement at ingest; geom_lo tier |
| Redis memory pressure | Medium | Low | LRU eviction; maxmemory 512mb |
| PostGIS slow at 200+ entity scale | Low | High | GIST index; benchmark before shipping M3 |
| Frontend jank at zoom-out with 40+ territories | Medium | Medium | geom_lo + area filter |

### Scope Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| M3 expands indefinitely | High | High | Fix entity list at milestone start; strict defer policy |
| Manual tracing bottleneck | High | High | Tier 1 (automated ingest) first; trace only where no source |
| Lineage system creep (building UI prematurely) | Medium | Medium | Schema + data only in M3; no frontend lineage tree |

---

## 14. What Should and Should NOT Be Implemented in M3

### MUST implement

- [ ] Migration 0003 (all schema additions below)
- [ ] `geom_lo` + 3-tier LOD at ingest
- [ ] `entity_lineages` table + batch lineage loader
- [ ] `date_precision` field on territories + place_names
- [ ] `end_event_type` field on territories
- [ ] `territory_sources` table (schema only, no data migration)
- [ ] `region_coverage` table + CLI report
- [ ] Entity type taxonomy + CHECK constraint + validation
- [ ] SNAPSHOT_YEARS adaptive expansion
- [ ] Source registry YAML + `fetch_sources.py`
- [ ] `validate.py` schema linter (all 12 checks)
- [ ] QA CLI (`qa`, `stats`, `diff`, `audit` subcommands)
- [ ] Debug/admin API endpoints (internal only)
- [ ] GZip middleware
- [ ] Tier 1 entities ingested with lineage + type metadata
- [ ] Tier 2 entities (best-effort)
- [ ] `ancient_cities.csv` → 500+ globally
- [ ] `name_local` + `date_precision` on place_names
- [ ] Frontend viewport bbox
- [ ] `docs/HISTORICAL_PHILOSOPHY.md`
- [ ] CI data validation workflow

### SHOULD implement (if time allows)

- [ ] Tier 3 entities
- [ ] Importance-based zoom filtering in place_names API
- [ ] Contributor README files per region

### DEFER to M4+

- [ ] Frontend lineage tree / civilization graph UI
- [ ] Temporal uncertainty visualization (soft markers on timeline)
- [ ] `territory_sources` multi-citation data entry
- [ ] Full OHM global import (too noisy without curation)
- [ ] Vector tiles (M7)
- [ ] Viewport partitioning tile API (M6)
- [ ] Animated transitions
- [ ] AI narration / semantic search

---

## 15. Entity Lineage System

### Purpose

Many historical entities evolve, split, merge, or continue under new forms. Without lineage data, the system treats all civilizations as independent — losing essential historical continuity needed for future visualization, AI reasoning, and timeline coherence.

### Schema (migration 0003)

```sql
CREATE TABLE entity_lineages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    child_entity_id  UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN (
        'evolved_into', 'successor', 'continuation', 'split_from', 'merged_into'
    )),
    year            INTEGER NOT NULL,
    notes           TEXT,
    UNIQUE (parent_entity_id, child_entity_id, relationship_type)
);

CREATE INDEX entity_lineages_parent_idx ON entity_lineages(parent_entity_id);
CREATE INDEX entity_lineages_child_idx  ON entity_lineages(child_entity_id);
```

### Relationship Type Semantics

| Type | Meaning | Example |
|------|---------|---------|
| `evolved_into` | Same polity, changes form | Roman Republic → Roman Empire |
| `continuation` | Recognized successor state, direct continuity | Eastern Roman → Byzantine |
| `successor` | Replaces predecessor, different ruling group | Umayyad → Abbasid |
| `split_from` | Fragment of parent | Western Roman ← Roman Empire |
| `merged_into` | Absorbed by another | Subsidiary kingdoms → Mongol Empire |

### Ingestion Format

`packages/data/lineages/<slug>.yaml`:
```yaml
entity: roman-empire
lineages:
  - parent: roman-republic
    relationship: evolved_into
    year: -27
  - parent: roman-empire
    relationship: split_from  # roman-empire is parent of split
    # child is declared from the child's file
```

**Alternative**: declare all lineages in `data/raw/lineages/all.yaml` (flat list). Simpler for batch ingest.

### Loader

`packages/data/lineage_loader.py` — resolves slugs to UUIDs, bulk-upserts into `entity_lineages`. Idempotent on `(parent, child, relationship_type)` unique constraint.

### CLI

```bash
python -m data lineage --declare data/raw/lineages/all.yaml
python -m data lineage --show roman-empire  # prints lineage tree for entity
```

### Not In M3

No frontend lineage UI. No graph traversal API. Schema + data only.

---

## 16. Historical State-Type Taxonomy

### Problem

Current `entities.type` is a free-text field. Values like "empire", "dynasty", "caliphate" are used inconsistently. No validation. Downstream filtering and styling become unreliable.

### Standardized Taxonomy

```python
VALID_ENTITY_TYPES = {
    'empire',             # centralized, expansionist
    'kingdom',            # monarchical, regional
    'republic',           # non-monarchical governing body
    'dynasty',            # ruling family over defined territory
    'caliphate',          # Islamic religio-political state
    'sultanate',          # Islamic monarchy (Sultan as head)
    'tribal_confederation', # loose alliance of tribes
    'nomadic_empire',     # steppe-based mobile polity
    'city_state',         # single city + immediate hinterland
    'colony',             # dependent territory of another polity
    'protectorate',       # nominally autonomous, foreign-controlled
    'confederation',      # league of independent polities
}
```

### Schema Change (migration 0003)

```sql
-- Add CHECK constraint to existing entities.type column
-- First update any non-conforming values, then add constraint
ALTER TABLE entities ADD CONSTRAINT entities_type_check
  CHECK (type IN (
    'empire','kingdom','republic','dynasty','caliphate','sultanate',
    'tribal_confederation','nomadic_empire','city_state','colony',
    'protectorate','confederation'
  ));
```

### Validation

Add to `validate.py` check #7. Add to contributor checklist. Add to CI.

### Ingestion Implication

Existing Mediterranean entities must be audited for type conformance before migration 0003 runs. Add a pre-migration script that prints any non-conforming values.

### Future Use

- MapLibre paint expressions: different fill patterns per type
- Filter panel: "show only empires / republics"
- Semantic reasoning (M5+)

---

## 17. Temporal Uncertainty Metadata

### Problem

Ancient chronology is often approximate. Asserting exact years for events like the founding of Han Dynasty or collapse of Gupta Empire misrepresents scholarly consensus, which typically gives decade-range estimates.

### Schema Addition (migration 0003)

On `territories` table:
```sql
ALTER TABLE territories
  ADD COLUMN date_precision TEXT NOT NULL DEFAULT 'approximate'
  CHECK (date_precision IN ('exact', 'approximate', 'estimated'));
```

On `place_names` table (already planned in §7):
```sql
ALTER TABLE place_names
  ADD COLUMN date_precision TEXT NOT NULL DEFAULT 'approximate'
  CHECK (date_precision IN ('exact', 'approximate', 'estimated'));
```

### Semantic Definitions

| Value | Meaning | Use When |
|-------|---------|----------|
| `exact` | Year documented in primary sources | CE dates with textual confirmation |
| `approximate` | Year known within ±25 years | Most ancient Mediterranean entities |
| `estimated` | Year estimated within ±50–200 years | Pre-Hellenistic, prehistoric, East Asian ancient |

### Ingestion

Set at YAML config / GeoJSON properties level per phase. Default `approximate`. External datasets (AWMC, cShapes) → `approximate`. Manual traces from ancient sources → `estimated`.

### API Exposure

Include `date_precision` in territory properties in API response. No frontend rendering in M3 — data contract established for M4 uncertainty visualization.

### Not In M3

No UI uncertainty indicators. No snapping logic changes. Schema + data only.

---

## 18. Transition / Collapse Metadata

### Purpose

Every territory phase ends for a reason. Capturing the end-event type enables future timeline animation (phase-out effects), historical causality modeling, and event synchronization without a separate events system.

### Schema Addition (migration 0003)

```sql
ALTER TABLE territories
  ADD COLUMN end_event_type TEXT
  CHECK (end_event_type IN (
    'conquest', 'collapse', 'annexation', 'rebellion',
    'unification', 'succession', 'treaty', 'partition',
    'administrative_reorganization'
  ));
```

`NULL` = unknown or ongoing (year_end IS NULL territories).

### Semantics

| Type | Example |
|------|---------|
| `conquest` | Roman conquest of Carthage |
| `collapse` | Western Roman Empire 476 CE |
| `annexation` | Ptolemaic Egypt → Roman province |
| `rebellion` | Province breaks away |
| `unification` | Warring States → Qin unification |
| `succession` | Ruler dies, next phase begins |
| `treaty` | Territory ceded by peace treaty |
| `partition` | Mongol Empire division among sons |
| `administrative_reorganization` | Internal boundary change, same polity |

### Ingestion

Set in GeoJSON phase properties or YAML defaults. Contributors must set for phases with known `year_end`.

### Validation

`end_event_type` must be set whenever `year_end IS NOT NULL` and `date_precision IN ('exact','approximate')`. Warn (not error) when missing.

### Not In M3

No event animation. No event timeline UI. Data modeling only.

---

## 19. Territory Source Granularity Preparation

### Problem

Current model: one `source_name` / `source_url` per territory. Future historical polygons may combine multiple sources (e.g., eastern boundary from AWMC, western from OHM, northern from manual trace).

### M3 Action: Schema Stub Only

```sql
CREATE TABLE territory_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    territory_id    UUID NOT NULL REFERENCES territories(id) ON DELETE CASCADE,
    source_name     TEXT NOT NULL,
    source_url      TEXT,
    source_license  TEXT NOT NULL,
    contribution    TEXT,   -- e.g. 'northern_boundary', 'full_polygon', 'year_estimate'
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX territory_sources_territory_idx ON territory_sources(territory_id);
```

### Do NOT Migrate Existing Data in M3

`territories.source_name/source_url/source_license` remain the primary fields. `territory_sources` is empty in M3 — schema only. Migration 0004+ populates it when multi-citation is needed.

### Future Path

When a territory's boundary draws from >1 source: insert rows to `territory_sources`, leave `territories.source_name` as the primary/dominant source. API exposes `territory_sources` as optional `citations[]` array per feature — no frontend rendering yet.

---

## 20. Geometry QA + Internal Debug Tooling

### CLI QA Subcommands

Add to `packages/data/__main__.py`:

```bash
python -m data qa --check-overlaps
# Finds territories of DIFFERENT entities with overlapping years AND intersecting geometries.
# Expected: some overlap (empires contest borders). Flag only >50% area overlap as error.

python -m data qa --invalid-geoms
# Queries DB: SELECT slug, ST_IsValid(geom) FROM territories → lists invalid

python -m data qa --temporal-gaps
# Finds entities where max(year_end of phase N) < min(year_start of phase N+1)
# Indicates missing phase data

python -m data stats
# Prints:
#   entities: N total, by type, by region
#   territories: N total, avg vertices, avg area km²
#   place_names: N total, by importance tier
#   temporal coverage: earliest/latest year_start per region
#   geom_lo null count (should be 0 after full ingest)

python -m data diff --entity <slug>
# Compares entity territory count in DB vs phase-N.geojson files in data/raw/
# Flags: "DB has 3 territories, raw has 4 phases — possible ingest gap"

python -m data audit --source <source-id>
# Lists all territories in DB where source_name matches registry entry
# Shows: slug, year_start, year_end, date_precision, confidence_type
```

### Developer API Endpoints

`apps/api/app/routers/debug.py` — mounted at `/api/v1/debug/`, `include_in_schema=False`:

```python
GET /api/v1/debug/geometry?entity=<slug>
# Returns: {valid: bool, geom_vertices: int, simplified_vertices: int, geom_lo_vertices: int, area_km2: float}

GET /api/v1/admin/stats
# Returns: {entities: int, territories: int, place_names: int, lineages: int, regions: [...]}

GET /api/v1/admin/coverage
# Returns region_coverage table as JSON
```

No auth in M3. Document clearly as dev-only. Add to `.env.example`: `ENABLE_DEBUG_ENDPOINTS=true`.

### Not In M3

No HTML debug UI. No overlap visualization in browser. CLI + API endpoints only.

---

## 21. Regional Coverage + Confidence Mapping

### Purpose

Global coverage quality will vary massively. Need internal tracking of: which regions are well-covered, which are sparse, and what confidence level applies to each region × time period.

### Schema (migration 0003)

```sql
CREATE TABLE region_coverage (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_name     TEXT NOT NULL,      -- 'east_asia', 'mediterranean', 'africa', etc.
    year_start      INTEGER NOT NULL,
    year_end        INTEGER,
    completeness    TEXT NOT NULL CHECK (completeness IN ('complete','partial','sparse','none'))
                    DEFAULT 'none',
    entity_count    INTEGER DEFAULT 0,
    primary_source  TEXT,
    notes           TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### CLI Report

```bash
python -m data coverage-report
# Outputs table:
# Region        | BCE 3000-1000 | BCE 1000-500 | BCE 500-0 | CE 0-500 | CE 500-1500 | CE 1500-2000
# east_asia     | none          | sparse       | partial   | partial  | complete    | complete
# mediterranean | none          | sparse       | complete  | complete | partial     | sparse
# ...
```

Populated by running `python -m data stats --update-coverage` after each ingest batch.

### Not In M3

No frontend coverage overlay. No public-facing "data quality" UI. Internal tooling only.

---

## 22. Historical Simplification Philosophy

### Purpose

The platform inevitably simplifies disputed borders, nomadic zones, fuzzy influence areas, and ancient territorial ambiguity. Without explicit policy, different contributors will make different choices — producing inconsistent and potentially misleading historical data.

### Deliverable: `docs/HISTORICAL_PHILOSOPHY.md`

This document covers:

**1. Border Representation Policy**
- All borders are approximations unless `confidence_type = 'exact'` and `date_precision = 'exact'`
- Disputed borders: render as the dominant historical consensus, not modern political claims
- Nomadic empires: render core territory + maximum extent as separate phases

**2. Temporal Approximation Policy**
- Phase boundaries: use the historical event date when documented; estimate decade midpoint when not
- When scholarly consensus disagrees: use the median of cited dates; set `date_precision = 'estimated'`
- Never assert exact year for pre-600 BCE events without primary source citation

**3. Overlap Policy**
- Overlapping territories at same year are valid (contested regions, vassal states)
- Client renders overlapping polygons; Z-order by `importance` descending
- Do NOT merge or clip overlapping territories at ingest — preserve raw historical reality

**4. Missing Data Policy**
- Prefer no territory over a fabricated territory
- An entity can exist in `entities` table without any territory rows
- Blank territory = "presence known, extent unknown" — display in entity list but not on map

**5. Source Hierarchy**
1. Peer-reviewed academic GIS datasets (AWMC, CHGIS)
2. Well-curated crowdsourced datasets (OHM)
3. Manual traces from published historical atlases
4. Estimated approximations (lowest priority, `confidence_type = 'inferred'`)

---

## 23. Recommended Milestone/Task Breakdown

### M3-A: Foundation Schema (Week 1)

1. **Migration 0003** — all schema additions:
   - `territories.geom_lo`, `territories.date_precision`, `territories.end_event_type`
   - `entity_lineages` table
   - `territory_sources` table (empty)
   - `region_coverage` table
   - `place_names.name_local`, `place_names.date_precision`
   - `entities.type` CHECK constraint (after auditing existing data)
   - All new indexes
2. **Entity type audit** — pre-migration script to check existing entities.type values
3. **SNAPSHOT_YEARS adaptive expansion**
4. **GZip middleware**
5. **Adaptive 3-tier LOD in normalize.py**

### M3-B: Validation + QA Tooling (Week 1–2)

6. **validate.py** — all 12 checks
7. **qa subcommands** — overlaps, invalid-geoms, temporal-gaps
8. **stats + diff + audit subcommands**
9. **coverage-report**
10. **CI workflow** — data-validate.yml

### M3-C: Ingestion Infrastructure (Week 2)

11. **Source registry YAML**
12. **fetch_sources.py** — download + SHA256 verify
13. **lineage_loader.py** — slug → UUID resolver, upsert
14. **Ingest CLI expansion** — `--source`, `--all-sources`, `lineage --declare`
15. **Recursive glob for regional file structure**

### M3-D: Mediterranean Cleanup (Week 2–3)

16. **Replace 13 hand-drawn GeoJSONs** with AWMC-sourced traces
17. **Add date_precision + end_event_type** to all existing phases
18. **Declare lineages** for all existing entities
19. **Re-ingest** with new LOD pipeline
20. **Verify existing 189 tests still pass**

### M3-E: Tier 1 Expansion (Week 3–4)

21. **cShapes 2.0 source config + ingest** → Ottoman, Byzantine
22. **OHM export + ingest** → Mongol, Abbasid, Umayyad
23. **Lineage declarations** for all Tier 1
24. **Validate + coverage-report update**

### M3-F: Tier 2 Expansion (Week 4–6)

25. **CHGIS source config + ingest** → Han, Tang, Qin
26. **Manual traces** → Maurya, Gupta (B.C. Law atlas)
27. **Lineage declarations** for all Tier 2
28. **Validate + ingest**

### M3-G: Place Names + Debug Endpoints (Week 5–6)

29. **Pleiades JSON export** → filter + convert to CSV
30. **WHG dataset** → global medieval places
31. **Expand ancient_cities.csv** → 500+ with name_local + date_precision
32. **Importance-based zoom filter in API**
33. **Debug/admin API endpoints**
34. **docs/HISTORICAL_PHILOSOPHY.md**

### M3-H: Frontend + API Tuning (Week 6–7)

35. **Viewport bbox** in MapContainer → useTerritoryLayer
36. **geom_lo query tier** in world_state SQL
37. **Performance test** at 30+ entities
38. **Vertex budget enforcement** at ingest
39. **Redis maxmemory config** in docker-compose

### M3-I: Tier 3 + Contributor Docs (Week 7)

40. **Tier 3 entities** (best-effort: Inca, Aztec, Mali, Songhai, Sasanian, Mughal)
41. **Contributor README files** per region
42. **region_coverage** populated for all ingested regions

### M3-J: Test Suite (Week 7–8)

43. **test_validate.py** — all 12 validation checks
44. **test_lineage_loader.py** — slug resolution, upsert, duplicate handling
45. **test_lod_pipeline.py** — 3-tier simplification, vertex budget
46. **test_world_state_m3.py** — geom_lo tier selection, expanded snapshot years, date_precision in response
47. **test_entity_types.py** — taxonomy CHECK constraint enforcement
48. **test_qa_tools.py** — overlap detection, temporal gap detection
49. **test_debug_endpoints.py** — geometry stats endpoint, admin stats endpoint
50. **Integration test** — ingest Tier 1 entity, verify API at 3 zoom levels, verify lineage in DB

---

## 24. Success Criteria

- [ ] ≥15 global entities ingested with real historical boundaries (no hand-drawn rectangles)
- [ ] All entities have `type` from taxonomy, `date_precision`, at least one lineage link
- [ ] Snapshot range: -1000 BCE to 1900 CE minimum
- [ ] API response < 500ms at world bbox, zoom 4, 30 concurrent entities
- [ ] place_names: ≥500 globally distributed cities with `name_local` where applicable
- [ ] All existing 189 tests still passing
- [ ] M3 test suite: ≥50 new tests
- [ ] No entity ingested without `source_license` populated
- [ ] No entity ingested without `date_precision` set
- [ ] No phase with known `year_end` missing `end_event_type`
- [ ] MapLibre renders 30+ entity snapshot without frame drops at zoom 4
- [ ] `python -m data qa --check-overlaps` runs without fatal errors
- [ ] `docs/HISTORICAL_PHILOSOPHY.md` exists and is complete
- [ ] `entity_lineages` table contains ≥20 declared relationships
- [ ] `region_coverage` table populated for all ingested regions

---

*Planning document. Step-by-step TDD implementation plan follows as a separate document.*
