# Project Roadmap — Historical World Map

**Vision:** A production-grade interactive world history map covering 3000 BCE → 2026 CE. As the user drags the timeline slider, the entire world map dynamically redraws — borders shift, empires rise and fall, place names change, countries appear and disappear. Every frame is historically accurate for that exact year.

**Slider range:** 3000 BCE → 2026 CE (5000 years)
**Target scale:** Global coverage, every major civilization and political entity
**Accuracy target:** ±50km at zoom 4, ±10km at zoom 8, sourced from peer-reviewed datasets

---

## Status Legend
- ✅ Complete
- 🔄 In progress
- ⬜ Not started

---

## Milestone 0 — Backend Foundation ✅

**Goal:** Core backend infrastructure running in Docker.

**What was built:**
- FastAPI + SQLAlchemy async API (`apps/api/`)
- PostGIS database with full schema (entities, entity_names, territories, events, layers)
- Redis caching layer
- Alembic migrations
- Docker Compose stack (`infra/docker-compose.yml`)
- Test Docker stack (`infra/docker-compose.test.yml`)
- World state API endpoint: `GET /api/v1/world/state?year=&bbox=&zoom=`
- Redis cache with LRU snapshot preloading
- API test suite

**Key files:**
- `apps/api/app/main.py`
- `apps/api/app/routers/world.py`
- `apps/api/app/services/world_state.py`
- `apps/api/alembic/versions/0001_initial_schema.py`
- `infra/docker-compose.yml`

---

## Milestone 1 — Frontend ✅

**Goal:** Interactive map UI wired to backend.

**What was built:**
- Next.js 14 app (`apps/web/`)
- MapLibre GL map centered on Mediterranean
- Timeline slider (500 BCE → 500 CE at this stage)
- Territory polygon layer with entity colors (from `/world/state`)
- Entity panel (click territory → name, color, type, confidence)
- Loading overlay + error banner
- Hover highlight on territories
- LRU snapshot cache (frontend)
- Adjacent year preloading
- Zustand timeline store
- Full test suite (Vitest)

**Key files:**
- `apps/web/components/map/MapContainer.tsx`
- `apps/web/components/map/MapView.tsx`
- `apps/web/components/map/useTerritoryLayer.ts`
- `apps/web/components/timeline/TimelineSlider.tsx`
- `apps/web/components/entity/EntityPanel.tsx`
- `apps/web/store/timeline.ts`

---

## Data Ingest Pipeline ✅

**Goal:** CLI pipeline to load historical entities into PostGIS.

**What was built:**
- `packages/data/` standalone Python package
- `ingest.py` orchestrator with `--entity` and `--dry-run` flags
- `loader.py` — psycopg2 upsert/insert for entities and territories
- `normalize.py` — Polygon→MultiPolygon, simplify, validate
- 13 entity YAML configs (Mediterranean civilizations)
- 25 GeoJSON phase files (hand-drawn approximations — replaced in M2)
- Full unit + integration test suite
- Makefile targets: `seed`, `seed-entity`, `seed-dry`

**Entities loaded (approximate boundaries):**
Roman Republic, Roman Empire, Western Roman Empire, Eastern Roman Empire,
Achaemenid Persia, Macedonian Empire, Seleucid Empire, Ptolemaic Egypt,
Parthian Empire, Carthage, Greek City-States, Numidia, Germanic Tribes

**Note:** Current GeoJSON files are rectangular approximations. Replaced with accurate traced boundaries in M2.

---

## Milestone 2 — Data Accuracy, Map Style & Historical Place Names ⬜

**Goal:** Fix the data foundation before global expansion. M3 builds on this.

**Data strategy:** Hybrid free datasets
- 1886–2019: cShapes 2.0 (CC BY, global political borders)
- 1 CE–1886: OpenHistoricalMap (ODbL)
- 500 BCE–640 CE: Ancient World Mapping Center (CC BY 4.0)
- 3000 BCE–500 BCE: Manual traces from peer-reviewed atlases
- Physical base: MapLibre stripped style

**What gets built:**

### Data Pipeline
- `packages/data/importer.py` — generic shapefile + GeoJSON importer, source-aware
- `packages/data/sources/cshapes.yml` — cShapes field mappings
- `packages/data/sources/awmc.yml` — AWMC field mappings
- `packages/data/fetch_sources.py` — download + checksum-verify source datasets
- `packages/data/place_names_loader.py` — load ~300 historical cities
- Replace all 25 hand-drawn rectangle GeoJSONs with accurate traced boundaries
- Entity YAML configs: add source_name, source_url, source_license, data_version fields

### Database (Migration 0002)
- `territories`: add source_name, source_url, source_license, data_version columns
- New table: `data_sources` (registry of all datasets powering the app)
- New table: `place_names` (historical city/settlement labels with year ranges)
- Indexes: place_names by year range + GIST spatial index

### Map Style
- Strip modern political overlay from base map (country borders, country names, state borders)
- Keep physical geography (terrain, coastlines, rivers, ocean labels, mountain ranges)
- Custom style JSON: `apps/web/public/map-style/historical.json`
- Build script: `scripts/build-map-style.ts`

### API
- `GET /api/v1/place-names?year=&bbox=&zoom=` → GeoJSON FeatureCollection of historical cities
- `GET /api/v1/sources` → list of all data sources with license info
- `GET /api/v1/world/state` → add `source_name` to feature properties

### Frontend
- Timeline slider range: **3000 BCE → 2026 CE**
- New `usePlaceNamesLayer.ts` hook — historical city labels
- Map loads local stripped style instead of remote OpenFreemap
- EntityPanel: show source attribution per territory
- Attribution footer: list active data sources

### Testing
- `test_importer.py`, `test_place_names_loader.py`
- `test_place_names.py`, `test_sources.py`
- `usePlaceNamesLayer.test.ts`

**Success criteria:**
- All 25 phase GeoJSONs replaced with accurate traced boundaries
- No modern country names/borders visible on base map
- Historical city labels at zoom 3+ (Constantinople, Rome, Alexandria, etc.)
- Slider range 3000 BCE → 2026 CE
- Every territory has source_name in DB
- importer.py ingests shapefile or GeoJSON without code changes

**Design doc:** `docs/superpowers/specs/2026-05-17-m2-design.md`

---

## Milestone 3 — Global Coverage (3000 BCE → 2026 CE) ⬜

**Goal:** Full world coverage. This is the core product.

**What gets built:**

### Data — Ancient World (3000 BCE → 500 BCE)
- Mesopotamia: Sumer, Akkadian Empire, Babylonian Empire, Assyrian Empire
- Egypt: Old Kingdom, Middle Kingdom, New Kingdom, Late Period
- Indus Valley Civilization
- Minoan Crete, Mycenaean Greece
- Hittite Empire
- Phoenicia
- Zhou Dynasty China, Shang Dynasty

### Data — Classical World (500 BCE → 500 CE)
- Extend existing 13 Mediterranean entities with better boundaries (from M2)
- Maurya Empire, Gupta Empire (Indian subcontinent)
- Qin Dynasty, Han Dynasty, Three Kingdoms (China)
- Xiongnu Confederation
- Kingdom of Axum (Ethiopia)
- Kingdom of Kush (Sudan)
- Scythian Kingdoms

### Data — Medieval World (500 CE → 1500 CE)
- Byzantine Empire (all phases)
- Islamic Caliphates: Rashidun, Umayyad, Abbasid, Fatimid
- Mongol Empire + successor khanates
- Song, Tang, Ming, Yuan Dynasties (China)
- Sultanate of Delhi, Vijayanagara Empire
- Mali Empire, Songhai Empire, Ghana Empire
- Holy Roman Empire
- Frankish Kingdom → France
- Viking Age territories
- Kingdom of England, Scotland, Ireland
- Ottoman Empire (early phases)
- Kievan Rus → Russian principalities
- Aztec Empire, Maya city-states, Inca Empire
- Great Zimbabwe

### Data — Early Modern (1500 CE → 1886 CE)
- Ottoman Empire (peak + decline)
- Safavid Persia → Qajar Iran
- Mughal Empire
- Qing Dynasty
- European colonial empires: Spanish, Portuguese, Dutch, British, French
- Kingdom of France, Prussia, Austria-Habsburg
- Russian Empire (expansion phases)
- United States (territorial expansion)
- Latin American independence states
- Japanese Edo period → Meiji

### Data — Modern (1886 CE → 2026 CE)
- Import cShapes 2.0 dataset (covers this era globally, high accuracy)
- WWI/WWII border changes
- Decolonization (1940s–1970s)
- Soviet Union formation + dissolution
- German reunification
- Yugoslav dissolution
- Current borders

### Infrastructure
- Vector tile serving via `ST_AsMVT` (replaces GeoJSON API at this scale — required before M3 data ships)
- Pre-render tile cache for high-traffic years (-264, 0, 1000, 1492, 1800, 1945, 2000)
- Parallel import scripts for regional datasets

**Scale:** ~500–1000 entities, ~3000–5000 territory phases

---

## Milestone 4 — Events, Battles & Trade Routes ⬜

**Goal:** Turn map from "territory viewer" into "history viewer."

**What gets built:**
- Battle/siege markers as point layer (Battle of Marathon, Waterloo, Stalingrad, etc.)
- Migration flow arrows (Mongol expansion direction, Bantu migration, etc.)
- Trade route lines (Silk Road, Roman trade network, Hanseatic League)
- Timeline shows events as dots — click to see details panel
- Toggle overlays: territories only / battles only / trade routes / all
- `GET /api/v1/events?year=&bbox=` endpoint
- ~500 key historical events loaded

---

## Milestone 5 — Entity Intelligence ⬜

**Goal:** Rich information panel for every entity.

**What gets built:**
- Population estimates per phase (Rome at 100 CE: 50M empire, 1M city)
- Capital city marker per entity per phase
- Wikipedia summary integration (cached, not live)
- Key rulers list per phase
- Rise/fall narrative (1-2 sentences per entity)
- Related entities ("successor of", "rival of", "absorbed by")
- `entities.wiki_id` column for Wikipedia linking
- EntityPanel redesign: tabbed (Overview / Rulers / Territory)

---

## Milestone 6 — Discovery, Search & Animation ⬜

**Goal:** Make the app explorable and shareable.

**What gets built:**
- Search: type "Constantinople" → jumps to location, shows full history timeline for that point
- "What was here?" — click any map point → timeline of every entity controlling that spot
- Animate button — auto-advance timeline at 1x/10x/100x speed
- Share URL — encodes year + lat/lng + zoom (e.g., `/?y=-264&lat=41.9&lng=12.5&z=5`)
- Keyboard shortcuts: arrow keys advance year, space = play/pause
- Mobile responsive layout
- `GET /api/v1/location-history?lat=&lng=` — history at a point

---

## Milestone 7 — Vector Tiles & Performance ⬜

**Goal:** Scale to global coverage without performance degradation.

**Note:** Parts of M7 (ST_AsMVT infrastructure) are required before M3 data ships.

**What gets built:**
- Switch `/world/state` from GeoJSON to MVT (Mapbox Vector Tiles) via `ST_AsMVT`
- Frontend switches from GeoJSON source to vector tile source in MapLibre
- Pre-rendered tile cache in Redis for anchor years
- CDN edge caching for tile responses
- DB query optimization: spatial indexes tuned for bbox+year queries
- Benchmark: <200ms p95 for any year+bbox at zoom 4

---

## Milestone 8 — Production Infrastructure ⬜

**Goal:** Go live on the public internet.

**What gets built:**
- Deploy frontend: Vercel
- Deploy backend: Railway or Render (Docker)
- Managed PostGIS: Supabase or Neon
- Managed Redis: Upstash
- CI/CD: GitHub Actions (test → build → deploy on merge to main)
- Domain + SSL
- Error monitoring: Sentry
- Uptime monitoring: Better Uptime
- Rate limiting on API (100 req/min per IP)
- Environment config: `.env.production` with all secrets in Vercel/Railway env vars

---

## Milestone 9 — Community & Content ⬜

**Goal:** Self-sustaining content quality and developer ecosystem.

**What gets built:**
- Admin panel: add/edit/delete entities, territories, place names, events
- Source citation required for every territory polygon (enforced at import)
- User accounts: bookmark years/locations, save custom views
- Embed widget: `<iframe>` for any website to embed the map at a specific year
- Public API: documented REST API for developers (rate limited, API key required)
- Community corrections: submit boundary correction with source → review queue
- "Confidence" visualization: show uncertain boundaries differently (dashed, lighter)

---

## Technical Debt & Cross-Cutting Concerns

Track these across all milestones:

- **Year 0**: Already handled (`normalize_year` skips 0, BCE uses negative ints)
- **Geometry validity**: `validate_geom` already checks, add repair step for bad imports
- **Projection**: All data WGS84 (SRID 4326) — enforce at import
- **Null island**: Reject geometries at (0,0) — common data error
- **Antimeridian**: Handle territories crossing 180° longitude (Mongol Empire, Russian Empire)
- **Data licensing**: Every polygon must have traceable license before public launch
- **i18n**: Architecture supports multi-language place names (language column exists) — UI in M6+

---

## File Structure Reference

```
c:/History/
├── apps/
│   ├── api/                    FastAPI backend
│   └── web/                    Next.js frontend
├── packages/
│   └── data/                   Python ingest pipeline
├── data/
│   ├── raw/political/          GeoJSON phase files per entity
│   └── sources/                Downloaded external datasets (gitignored)
├── infra/
│   ├── docker-compose.yml      Dev stack
│   └── docker-compose.test.yml Test stack
└── docs/
    ├── roadmap.md              THIS FILE
    └── superpowers/
        ├── plans/              Implementation task plans per milestone
        └── specs/              Design docs per milestone
```
