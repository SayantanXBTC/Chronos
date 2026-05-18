# M4 — Temporal Exploration UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the historical map from a GIS demo into an immersive temporal exploration platform — users can drag through time, click civilizations, explore lineage chains, and understand world history visually.

**Architecture:** Pure UX milestone — no schema changes. Changes span: (1) MapLibre style JSON for base map atmosphere (strip modern roads/buildings/POIs), (2) FastAPI entity detail endpoint returning dates + lineage, (3) React component upgrades to EntityPanel and TimelineSlider, (4) MapView interaction polish with focus mode and hover tooltips, (5) Frontend entity search, (6) Redis startup cache warming. World state GeoJSON gains `year_start`/`year_end` fields on territory features.

**Tech Stack:** Next.js 14 + MapLibre GL 5.24.0 + Zustand 5 + TailwindCSS 4 (frontend), FastAPI + SQLAlchemy async + Redis (backend), PostgreSQL + PostGIS, pytest / vitest for tests.

**What is NOT in M4:** Capitals/cities data population (`entity_capitals` table remains empty), mobile responsiveness, autoplay mode, 3D globe, AI narration, vector tile migration.

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `apps/web/public/map-style/historical.json` | Modify | Strip road/building/POI layers; tune colors |
| `scripts/strip_map_style.py` | Create | Script to regenerate stripped historical.json |
| `apps/api/app/services/world_state.py` | Modify | Add `year_start`/`year_end` to feature properties |
| `apps/api/app/services/entity_service.py` | Create | Entity detail + lineage queries |
| `apps/api/app/routers/entities.py` | Modify | Implement full entity detail endpoint |
| `apps/web/types/index.ts` | Modify | Add `EntityDetail`, `LineageEntry`; update `EntityProperties` |
| `apps/web/lib/api.ts` | Modify | Add `fetchEntityDetail` |
| `apps/web/lib/year.ts` | Modify | Add `ERA_MARKERS` and `getEraForYear` |
| `apps/web/store/timeline.ts` | Modify | Add `currentEntities` field |
| `apps/web/components/entity/EntityPanel.tsx` | Modify | Full panel: dates, lineage, contemporaries |
| `apps/web/components/entity/LineageTree.tsx` | Create | Lineage predecessor/successor visualization |
| `apps/web/components/timeline/TimelineSlider.tsx` | Modify | Keyboard nav, year input, era markers |
| `apps/web/components/map/MapView.tsx` | Modify | Focus mode (dim non-selected), hover tooltip |
| `apps/web/components/map/MapContainer.tsx` | Modify | Pass `selectedSlug` to MapView |
| `apps/web/components/map/useTerritoryLayer.ts` | Modify | Populate `currentEntities` in store |
| `apps/web/components/ui/SearchBar.tsx` | Create | Entity search dropdown |
| `apps/api/app/services/cache_service.py` | Modify | Add `warm_startup_cache` helper |
| `apps/api/app/main.py` | Modify | Add startup cache warming task |
| `apps/api/tests/test_entity_detail.py` | Create | Backend entity service tests |
| `apps/web/__tests__/entityPanel.test.tsx` | Create | EntityPanel component tests |
| `apps/web/__tests__/timelineSlider.test.tsx` | Create | TimelineSlider keyboard/era tests |

---

## Task M4-A: Strip Historical Base Map

**Files:**
- Create: `scripts/strip_map_style.py`
- Modify: `apps/web/public/map-style/historical.json`

The current `historical.json` (4792 lines) contains every OpenMapTiles layer including roads, buildings, POIs, airports, and tunnel infrastructure — all anachronistic. Removing them transforms the visual to a physical geography base focused on terrain, water, and land cover.

**Layers to KEEP** (remove everything else):
```
background
natural_earth
park
park_outline
landcover_wood
landcover_grass
landcover_ice
landcover_wetland
landcover_sand
waterway_tunnel
waterway_river
waterway_other
water
```

**Color tuning on kept layers:**
- `background.paint.background-color`: `"#f8f4f0"` → `"#cfc4a8"` (warm parchment)
- `water.paint.fill-color`: `"rgb(158,189,255)"` → `"#6e9ab5"` (muted aged blue)
- `waterway_river.paint.line-color`: `"#a0c8f0"` → `"#5d8fa8"`
- `waterway_other.paint.line-color`: `"#a0c8f0"` → `"#5d8fa8"`
- `waterway_tunnel.paint.line-color`: `"#a0c8f0"` → `"#5d8fa8"`

- [ ] **Step 1: Write failing test**

Create `scripts/test_strip_map_style.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

STYLE_PATH = Path("apps/web/public/map-style/historical.json")
MODERN_LAYER_PREFIXES = [
    "road_", "tunnel_", "bridge_", "building",
    "poi_", "airport", "highway-name", "highway-shield",
    "road_shield", "road_one_way",
    "aeroway_", "landuse_residential", "landuse_pitch",
    "landuse_track", "landuse_cemetery", "landuse_hospital",
    "landuse_school",
]

def test_no_modern_layers():
    style = json.loads(STYLE_PATH.read_text())
    layer_ids = [l["id"] for l in style["layers"]]
    violations = [lid for lid in layer_ids
                  if any(lid.startswith(p) or lid == p.rstrip("_") for p in MODERN_LAYER_PREFIXES)]
    assert not violations, f"Modern layers still present: {violations}"

def test_water_color_muted():
    style = json.loads(STYLE_PATH.read_text())
    water = next(l for l in style["layers"] if l["id"] == "water")
    assert water["paint"]["fill-color"] == "#6e9ab5"

def test_background_parchment():
    style = json.loads(STYLE_PATH.read_text())
    bg = next(l for l in style["layers"] if l["id"] == "background")
    assert bg["paint"]["background-color"] == "#cfc4a8"

def test_essential_layers_present():
    style = json.loads(STYLE_PATH.read_text())
    layer_ids = {l["id"] for l in style["layers"]}
    required = {"background", "water", "waterway_river", "natural_earth", "landcover_wood"}
    missing = required - layer_ids
    assert not missing, f"Required layers missing: {missing}"

if __name__ == "__main__":
    failures = []
    for name, fn in [(k, v) for k, v in globals().items() if k.startswith("test_")]:
        try:
            fn()
            print(f"  PASS {name}")
        except AssertionError as e:
            print(f"  FAIL {name}: {e}")
            failures.append(name)
    sys.exit(1 if failures else 0)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd c:/History
python scripts/test_strip_map_style.py
```

Expected: FAIL — modern layers still present, colors not yet changed.

- [ ] **Step 3: Create strip script and run it**

Create `scripts/strip_map_style.py`:

```python
"""Regenerate apps/web/public/map-style/historical.json with modern layers removed."""
import json
from pathlib import Path

STYLE_PATH = Path("apps/web/public/map-style/historical.json")

KEEP_LAYERS = {
    "background", "natural_earth",
    "park", "park_outline",
    "landcover_wood", "landcover_grass", "landcover_ice",
    "landcover_wetland", "landcover_sand",
    "waterway_tunnel", "waterway_river", "waterway_other",
    "water",
}

COLOR_OVERRIDES = {
    "background": {"background-color": "#cfc4a8"},
    "water": {"fill-color": "#6e9ab5"},
    "waterway_river": {"line-color": "#5d8fa8"},
    "waterway_other": {"line-color": "#5d8fa8"},
    "waterway_tunnel": {"line-color": "#5d8fa8"},
}

def main():
    style = json.loads(STYLE_PATH.read_text(encoding="utf-8"))
    style["layers"] = [l for l in style["layers"] if l["id"] in KEEP_LAYERS]
    for layer in style["layers"]:
        if layer["id"] in COLOR_OVERRIDES:
            layer.setdefault("paint", {}).update(COLOR_OVERRIDES[layer["id"]])
    STYLE_PATH.write_text(json.dumps(style, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(style['layers'])} layers to {STYLE_PATH}")

if __name__ == "__main__":
    main()
```

Run it:

```bash
cd c:/History
python scripts/strip_map_style.py
```

Expected: `Wrote 13 layers to apps/web/public/map-style/historical.json`

- [ ] **Step 4: Run test to verify it passes**

```bash
python scripts/test_strip_map_style.py
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Visual smoke test**

```bash
cd apps/web && npm run dev
```

Open `http://localhost:3000` in browser. Verify:
- No road lines, no building outlines, no POI dots or labels
- Ocean/seas visible as muted blue (`#6e9ab5`)
- Land background warm parchment (`#cfc4a8`)
- Rivers still visible in muted blue
- Historical territory fills and place name labels render over clean terrain

- [ ] **Step 6: Commit**

```bash
git add scripts/strip_map_style.py scripts/test_strip_map_style.py apps/web/public/map-style/historical.json
git commit -m "feat(m4-a): strip historical base map — remove roads/buildings/POIs, tune palette"
```

---

## Task M4-B: Entity Detail + Lineage API

**Files:**
- Create: `apps/api/app/services/entity_service.py`
- Modify: `apps/api/app/routers/entities.py`
- Modify: `apps/api/app/services/world_state.py` (add year_start/year_end to features)
- Create: `apps/api/tests/test_entity_detail.py`

The `/api/v1/entities/{slug}` endpoint currently returns `{"slug": slug}`. This task implements the full entity detail query (dates, lineage predecessors/successors) and adds `year_start`/`year_end` to world state features.

### Sub-task B1: world_state.py — add year_start/year_end

- [ ] **Step 1: Write failing test for year_start in features**

Add to `apps/api/tests/test_world_state_m3.py` at the end of `TestFeatureCollectionStructure`:

```python
def test_feature_has_year_start_and_year_end(self):
    """Territory year_start and year_end must be in feature properties."""
    rows = [
        {
            "entity_id": "uuid-1", "slug": "roman-empire", "type": "empire",
            "color": "#c0392b", "name": "Roman Empire",
            "confidence_type": "approximate", "source_name": None,
            "importance": 9, "year_start": -27, "year_end": 476,
            "geometry": {"type": "MultiPolygon", "coordinates": []},
        }
    ]
    svc = self._make_svc(rows)
    result = asyncio.get_event_loop().run_until_complete(
        svc.get_state(year=-264, bbox=(-180, -90, 180, 90), zoom=4)
    )
    props = result["features"][0]["properties"]
    assert props["year_start"] == -27
    assert props["year_end"] == 476
```

Run: `pytest apps/api/tests/test_world_state_m3.py::TestFeatureCollectionStructure::test_feature_has_year_start_and_year_end -v`
Expected: FAIL — KeyError or AssertionError.

- [ ] **Step 2: Modify WORLD_STATE_SQL to select year_start and year_end**

Edit `apps/api/app/services/world_state.py` — replace `WORLD_STATE_SQL`:

```python
WORLD_STATE_SQL = text("""
    SELECT
        e.id::text              AS entity_id,
        e.slug                  AS slug,
        e.type                  AS type,
        e.color                 AS color,
        en.name                 AS name,
        t.confidence_type       AS confidence_type,
        t.source_name           AS source_name,
        COALESCE(t.importance, 5) AS importance,
        t.year_start            AS year_start,
        t.year_end              AS year_end,
        ST_AsGeoJSON(
            CASE
                WHEN :zoom <= 4 THEN COALESCE(t.geom_lo, t.simplified_geom)
                WHEN :zoom <= 8 THEN t.simplified_geom
                ELSE t.geom
            END
        )::json                 AS geometry
    FROM territories t
    JOIN entities e ON t.entity_id = e.id
    JOIN entity_names en
        ON en.entity_id = e.id
        AND en.year_start <= :year
        AND (en.year_end IS NULL OR en.year_end > :year)
        AND en.is_primary = true
    WHERE
        t.year_start <= :year
        AND (t.year_end IS NULL OR t.year_end > :year)
        AND t.geom && ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 4326)
    ORDER BY e.slug
""")
```

Edit the `get_state` method's feature builder loop in the same file:

```python
features.append({
    "type": "Feature",
    "id": row["slug"],
    "geometry": row["geometry"],
    "properties": {
        "entity_id": row["entity_id"],
        "slug": row["slug"],
        "name": row["name"],
        "type": row["type"],
        "color": row["color"],
        "confidence": row["confidence_type"],
        "confidence_type": row["confidence_type"],
        "source_name": row["source_name"],
        "importance": row["importance"],
        "year_start": row["year_start"],
        "year_end": row["year_end"],
    },
})
```

- [ ] **Step 3: Update existing test mocks that need year_start/year_end**

In `apps/api/tests/test_world_state_m3.py`, update `_make_svc` helper rows to include `year_start` and `year_end`. The `_make_svc` mock should provide these in every row dict. Add to any existing row stubs:

```python
"year_start": -264,
"year_end": None,
```

Also update `apps/web/__tests__/timeline.test.ts` — the two mock `EntityProperties` objects need these fields. Add:
```typescript
year_start: -27,
year_end: 476,
```

Run: `pytest apps/api/tests/test_world_state_m3.py -v`
Expected: all pass.

### Sub-task B2: entity_service.py

- [ ] **Step 4: Write failing test for entity detail service**

Create `apps/api/tests/test_entity_detail.py`:

```python
"""Tests for entity_service.py."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.entity_service import EntityService


def _make_db(rows_by_call: list):
    """Build mock AsyncSession that returns successive result sets per execute call."""
    db = AsyncMock()
    results = []
    for rows in rows_by_call:
        mapping_rows = [dict(r) for r in rows]
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = mapping_rows
        mock_result.mappings.return_value.first.return_value = mapping_rows[0] if mapping_rows else None
        results.append(mock_result)
    db.execute = AsyncMock(side_effect=results)
    return db


class TestGetEntityDetail:
    def _entity_row(self):
        return {
            "entity_id": "uuid-aaa",
            "slug": "roman-empire",
            "type": "empire",
            "color": "#c0392b",
            "name": "Roman Empire",
            "year_start": -27,
            "year_end": 476,
            "source_name": "Manual trace",
            "confidence_type": "approximate",
            "importance": 9,
        }

    def test_returns_none_for_unknown_slug(self):
        db = _make_db([[]])  # no rows
        svc = EntityService(db=db)
        result = asyncio.get_event_loop().run_until_complete(
            svc.get_entity_detail("nonexistent-slug")
        )
        assert result is None

    def test_returns_entity_fields(self):
        db = _make_db([[self._entity_row()], [], []])  # entity row, no predecessors, no successors
        svc = EntityService(db=db)
        result = asyncio.get_event_loop().run_until_complete(
            svc.get_entity_detail("roman-empire")
        )
        assert result is not None
        assert result["slug"] == "roman-empire"
        assert result["name"] == "Roman Empire"
        assert result["year_start"] == -27
        assert result["year_end"] == 476
        assert result["type"] == "empire"
        assert result["color"] == "#c0392b"

    def test_returns_lineage_structure(self):
        predecessor = {
            "slug": "roman-republic",
            "name": "Roman Republic",
            "relationship_type": "evolved_into",
            "year": -27,
            "notes": "Augustus",
        }
        successor = {
            "slug": "western-roman-empire",
            "name": "Western Roman Empire",
            "relationship_type": "split_from",
            "year": 285,
            "notes": None,
        }
        db = _make_db([[self._entity_row()], [predecessor], [successor]])
        svc = EntityService(db=db)
        result = asyncio.get_event_loop().run_until_complete(
            svc.get_entity_detail("roman-empire")
        )
        assert "lineage" in result
        assert len(result["lineage"]["predecessors"]) == 1
        assert result["lineage"]["predecessors"][0]["slug"] == "roman-republic"
        assert result["lineage"]["predecessors"][0]["relationship_type"] == "evolved_into"
        assert len(result["lineage"]["successors"]) == 1
        assert result["lineage"]["successors"][0]["slug"] == "western-roman-empire"

    def test_empty_lineage_when_no_relations(self):
        db = _make_db([[self._entity_row()], [], []])
        svc = EntityService(db=db)
        result = asyncio.get_event_loop().run_until_complete(
            svc.get_entity_detail("roman-empire")
        )
        assert result["lineage"]["predecessors"] == []
        assert result["lineage"]["successors"] == []

    def test_lineage_entry_missing_notes_is_none(self):
        predecessor = {
            "slug": "roman-republic",
            "name": "Roman Republic",
            "relationship_type": "evolved_into",
            "year": -27,
            "notes": None,
        }
        db = _make_db([[self._entity_row()], [predecessor], []])
        svc = EntityService(db=db)
        result = asyncio.get_event_loop().run_until_complete(
            svc.get_entity_detail("roman-empire")
        )
        assert result["lineage"]["predecessors"][0]["notes"] is None


class TestEntityDetailRouter:
    def test_404_for_unknown_slug(self):
        from fastapi.testclient import TestClient
        from unittest.mock import AsyncMock, patch
        from app.main import app

        with patch("app.routers.entities.EntityService") as MockSvc:
            instance = MockSvc.return_value
            instance.get_entity_detail = AsyncMock(return_value=None)
            client = TestClient(app)
            resp = client.get("/api/v1/entities/nonexistent")
        assert resp.status_code == 404

    def test_200_for_known_slug(self):
        from fastapi.testclient import TestClient
        from unittest.mock import AsyncMock, patch
        from app.main import app

        detail = {
            "slug": "roman-empire", "name": "Roman Empire", "type": "empire",
            "color": "#c0392b", "year_start": -27, "year_end": 476,
            "source_name": None, "confidence_type": "approximate", "importance": 9,
            "lineage": {"predecessors": [], "successors": []},
        }
        with patch("app.routers.entities.EntityService") as MockSvc:
            instance = MockSvc.return_value
            instance.get_entity_detail = AsyncMock(return_value=detail)
            client = TestClient(app)
            resp = client.get("/api/v1/entities/roman-empire")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "roman-empire"
        assert "lineage" in resp.json()
```

Run: `pytest apps/api/tests/test_entity_detail.py -v`
Expected: ImportError — `app.services.entity_service` not found.

- [ ] **Step 5: Create entity_service.py**

Create `apps/api/app/services/entity_service.py`:

```python
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_DETAIL_SQL = text("""
    SELECT
        e.id::text              AS entity_id,
        e.slug,
        e.type,
        e.color,
        en.name,
        MIN(t.year_start)       AS year_start,
        MAX(t.year_end)         AS year_end,
        MAX(t.source_name)      AS source_name,
        MAX(t.confidence_type)  AS confidence_type,
        MAX(COALESCE(t.importance, 5)) AS importance
    FROM entities e
    JOIN entity_names en ON en.entity_id = e.id AND en.is_primary = true
    JOIN territories t ON t.entity_id = e.id
    WHERE e.slug = :slug
    GROUP BY e.id, e.slug, e.type, e.color, en.name
    ORDER BY en.year_start DESC
    LIMIT 1
""")

_PREDECESSORS_SQL = text("""
    SELECT
        pe.slug,
        pen.name,
        el.relationship_type,
        el.year,
        el.notes
    FROM entity_lineages el
    JOIN entities pe ON pe.id = el.parent_entity_id
    JOIN (
        SELECT DISTINCT ON (entity_id) entity_id, name
        FROM entity_names
        WHERE is_primary = true
        ORDER BY entity_id, year_start DESC
    ) pen ON pen.entity_id = pe.id
    WHERE el.child_entity_id = :entity_id
    ORDER BY el.year
""")

_SUCCESSORS_SQL = text("""
    SELECT
        ce.slug,
        cen.name,
        el.relationship_type,
        el.year,
        el.notes
    FROM entity_lineages el
    JOIN entities ce ON ce.id = el.child_entity_id
    JOIN (
        SELECT DISTINCT ON (entity_id) entity_id, name
        FROM entity_names
        WHERE is_primary = true
        ORDER BY entity_id, year_start DESC
    ) cen ON cen.entity_id = ce.id
    WHERE el.parent_entity_id = :entity_id
    ORDER BY el.year
""")


class EntityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entity_detail(self, slug: str) -> dict[str, Any] | None:
        row_result = await self.db.execute(_ENTITY_DETAIL_SQL, {"slug": slug})
        row = row_result.mappings().first()
        if row is None:
            return None

        entity_id = row["entity_id"]

        pred_result = await self.db.execute(_PREDECESSORS_SQL, {"entity_id": entity_id})
        predecessors = [
            {
                "slug": r["slug"],
                "name": r["name"],
                "relationship_type": r["relationship_type"],
                "year": r["year"],
                "notes": r["notes"],
            }
            for r in pred_result.mappings().all()
        ]

        succ_result = await self.db.execute(_SUCCESSORS_SQL, {"entity_id": entity_id})
        successors = [
            {
                "slug": r["slug"],
                "name": r["name"],
                "relationship_type": r["relationship_type"],
                "year": r["year"],
                "notes": r["notes"],
            }
            for r in succ_result.mappings().all()
        ]

        return {
            "slug": row["slug"],
            "name": row["name"],
            "type": row["type"],
            "color": row["color"],
            "year_start": row["year_start"],
            "year_end": row["year_end"],
            "source_name": row["source_name"],
            "confidence_type": row["confidence_type"],
            "importance": row["importance"],
            "lineage": {
                "predecessors": predecessors,
                "successors": successors,
            },
        }
```

- [ ] **Step 6: Implement entities.py router**

Replace `apps/api/app/routers/entities.py` entirely:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.entity_service import EntityService

router = APIRouter()


@router.get("/{slug}")
async def get_entity(slug: str, db: AsyncSession = Depends(get_db)):
    svc = EntityService(db=db)
    result = await svc.get_entity_detail(slug)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Entity '{slug}' not found")
    return result
```

- [ ] **Step 7: Run tests**

```bash
pytest apps/api/tests/test_entity_detail.py -v
```

Expected: all 7 tests PASS.

```bash
pytest apps/api/tests/ -v
```

Expected: all existing tests still pass.

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/services/entity_service.py apps/api/app/routers/entities.py \
        apps/api/app/services/world_state.py apps/api/tests/test_entity_detail.py \
        apps/api/tests/test_world_state_m3.py
git commit -m "feat(m4-b): entity detail API — dates, lineage chain, year_start/year_end on world state features"
```

---

## Task M4-C: Enhanced Entity Panel

**Files:**
- Modify: `apps/web/types/index.ts`
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/store/timeline.ts`
- Modify: `apps/web/components/map/useTerritoryLayer.ts`
- Create: `apps/web/components/entity/LineageTree.tsx`
- Modify: `apps/web/components/entity/EntityPanel.tsx`
- Create: `apps/web/__tests__/entityPanel.test.tsx`

The EntityPanel currently shows: name, type, boundary confidence, source. M4-C expands it to show dates, lineage chain, and contemporaries (entities active at the same year, derived from the current world state features already in the store).

- [ ] **Step 1: Write failing tests**

Create `apps/web/__tests__/entityPanel.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature, EntityDetail } from '@/types'

vi.mock('@/lib/api', () => ({
  fetchEntityDetail: vi.fn(),
}))

const mockEntity: EntityFeature = {
  type: 'Feature',
  id: 'roman-empire',
  geometry: { type: 'MultiPolygon', coordinates: [] },
  properties: {
    entity_id: 'uuid-aaa',
    slug: 'roman-empire',
    name: 'Roman Empire',
    type: 'empire',
    color: '#c0392b',
    confidence: 'approximate',
    confidence_type: 'approximate',
    source_name: 'Manual trace',
    importance: 9,
    year_start: -27,
    year_end: 476,
  },
}

const mockDetail: EntityDetail = {
  slug: 'roman-empire',
  name: 'Roman Empire',
  type: 'empire',
  color: '#c0392b',
  year_start: -27,
  year_end: 476,
  source_name: 'Manual trace',
  confidence_type: 'approximate',
  importance: 9,
  lineage: {
    predecessors: [
      { slug: 'roman-republic', name: 'Roman Republic', relationship_type: 'evolved_into', year: -27, notes: null },
    ],
    successors: [
      { slug: 'western-roman-empire', name: 'Western Roman Empire', relationship_type: 'split_from', year: 285, notes: null },
    ],
  },
}

describe('EntityPanel', () => {
  beforeEach(() => {
    useTimelineStore.setState({
      selectedEntity: null,
      currentEntities: [],
      year: 100,
    })
    vi.clearAllMocks()
  })

  it('renders nothing when no entity selected', () => {
    const { container } = render(<EntityPanel />)
    expect(container.firstChild).toBeNull()
  })

  it('shows entity name', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    expect(screen.getByText('Roman Empire')).toBeDefined()
  })

  it('shows dates once detail loads', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText(/27 BCE/)).toBeDefined())
    expect(screen.getByText(/476 CE/)).toBeDefined()
  })

  it('shows predecessor in lineage', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Roman Republic')).toBeDefined())
  })

  it('shows successor in lineage', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Western Roman Empire')).toBeDefined())
  })

  it('shows contemporaries from currentEntities', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    const contemporary: EntityFeature = {
      ...mockEntity,
      id: 'han-dynasty',
      properties: { ...mockEntity.properties, slug: 'han-dynasty', name: 'Han Dynasty', entity_id: 'uuid-bbb' },
    }
    useTimelineStore.setState({
      selectedEntity: mockEntity,
      currentEntities: [mockEntity, contemporary],
    })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Han Dynasty')).toBeDefined())
  })

  it('close button deselects entity', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    const user = userEvent.setup()
    render(<EntityPanel />)
    await user.click(screen.getByLabelText('Close entity panel'))
    expect(useTimelineStore.getState().selectedEntity).toBeNull()
  })
})
```

Run: `cd apps/web && npm run test -- --run __tests__/entityPanel.test.tsx`
Expected: many failures — types not updated, functions not implemented.

- [ ] **Step 2: Update types/index.ts**

Add to `apps/web/types/index.ts` after existing interfaces:

```typescript
export interface LineageEntry {
  slug: string
  name: string
  relationship_type: string
  year: number
  notes: string | null
}

export interface EntityDetail {
  slug: string
  name: string
  type: string
  color: string
  year_start: number
  year_end: number | null
  source_name: string | null
  confidence_type: string
  importance: number
  lineage: {
    predecessors: LineageEntry[]
    successors: LineageEntry[]
  }
}
```

Also add `year_start` and `year_end` to the existing `EntityProperties` interface:

```typescript
export interface EntityProperties {
  entity_id: string
  slug: string
  name: string
  type: string
  color: string
  confidence: string
  confidence_type: string
  source_name: string | null
  importance: number
  year_start: number
  year_end: number | null
}
```

- [ ] **Step 3: Add fetchEntityDetail to api.ts**

Edit `apps/web/lib/api.ts`, add function after existing exports:

```typescript
export async function fetchEntityDetail(slug: string): Promise<EntityDetail | null> {
  const resp = await fetch(`${API_BASE}/api/v1/entities/${slug}`)
  if (resp.status === 404) return null
  if (!resp.ok) throw new Error(`fetchEntityDetail: ${resp.status}`)
  return resp.json() as Promise<EntityDetail>
}
```

Also add `EntityDetail` to the import from `@/types` at the top of api.ts.

- [ ] **Step 4: Add currentEntities to store**

Edit `apps/web/store/timeline.ts`:

```typescript
import { create } from 'zustand'
import type { EntityFeature } from '@/types'

export interface Viewport {
  minX: number
  minY: number
  maxX: number
  maxY: number
  zoom: number
}

const DEFAULT_VIEWPORT: Viewport = {
  minX: -180, minY: -90, maxX: 180, maxY: 90, zoom: 4,
}

interface TimelineState {
  year: number
  selectedEntity: EntityFeature | null
  currentEntities: EntityFeature[]
  isLoading: boolean
  error: string | null
  viewport: Viewport
  setYear: (year: number) => void
  setSelectedEntity: (entity: EntityFeature | null) => void
  setCurrentEntities: (entities: EntityFeature[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setViewport: (viewport: Viewport) => void
}

export const useTimelineStore = create<TimelineState>((set) => ({
  year: -264,
  selectedEntity: null,
  currentEntities: [],
  isLoading: false,
  error: null,
  viewport: DEFAULT_VIEWPORT,
  setYear: (year) => set({ year }),
  setSelectedEntity: (selectedEntity) => set({ selectedEntity }),
  setCurrentEntities: (currentEntities) => set({ currentEntities }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setViewport: (viewport) => set({ viewport }),
}))
```

- [ ] **Step 5: Populate currentEntities in useTerritoryLayer.ts**

Edit `apps/web/components/map/useTerritoryLayer.ts`. After the line that calls `mapRef.current?.updateTerritories(data)`, add:

```typescript
useTimelineStore.getState().setCurrentEntities(data.features)
```

Import `useTimelineStore` at the top if not already imported.

- [ ] **Step 6: Create LineageTree.tsx**

Create `apps/web/components/entity/LineageTree.tsx`:

```typescript
'use client'

import type { LineageEntry } from '@/types'
import { yearToDisplay } from '@/lib/year'

const RELATIONSHIP_LABELS: Record<string, string> = {
  evolved_into: 'evolved into',
  successor: 'succeeded by',
  continuation: 'continued as',
  split_from: 'split into',
  merged_into: 'merged into',
}

interface LineageTreeProps {
  predecessors: LineageEntry[]
  successors: LineageEntry[]
}

export function LineageTree({ predecessors, successors }: LineageTreeProps) {
  if (predecessors.length === 0 && successors.length === 0) return null

  return (
    <div className="mt-3 pt-3 border-t border-white/10">
      <h3 className="text-white/40 text-xs uppercase tracking-widest mb-2">Lineage</h3>
      {predecessors.length > 0 && (
        <div className="mb-2">
          <div className="text-white/30 text-xs mb-1">Preceded by</div>
          {predecessors.map((entry) => (
            <div key={entry.slug} className="flex items-baseline gap-2 text-sm py-0.5">
              <span className="text-amber-300/80 font-medium truncate">{entry.name}</span>
              <span className="text-white/30 text-xs flex-shrink-0">
                {RELATIONSHIP_LABELS[entry.relationship_type] ?? entry.relationship_type}
              </span>
              <span className="text-white/30 text-xs flex-shrink-0">{yearToDisplay(entry.year)}</span>
            </div>
          ))}
        </div>
      )}
      {successors.length > 0 && (
        <div>
          <div className="text-white/30 text-xs mb-1">Succeeded by</div>
          {successors.map((entry) => (
            <div key={entry.slug} className="flex items-baseline gap-2 text-sm py-0.5">
              <span className="text-amber-300/80 font-medium truncate">{entry.name}</span>
              <span className="text-white/30 text-xs flex-shrink-0">
                {RELATIONSHIP_LABELS[entry.relationship_type] ?? entry.relationship_type}
              </span>
              <span className="text-white/30 text-xs flex-shrink-0">{yearToDisplay(entry.year)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 7: Rewrite EntityPanel.tsx**

Replace `apps/web/components/entity/EntityPanel.tsx` entirely:

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchEntityDetail } from '@/lib/api'
import { yearToDisplay } from '@/lib/year'
import { LineageTree } from './LineageTree'
import type { EntityDetail } from '@/types'

const CONFIDENCE_LABELS: Record<string, string> = {
  exact: 'Exact boundary',
  approximate: 'Approximate boundary',
  inferred: 'Inferred boundary',
  disputed: 'Disputed boundary',
}

export function EntityPanel() {
  const entity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const currentEntities = useTimelineStore((s) => s.currentEntities)
  const year = useTimelineStore((s) => s.year)
  const [detail, setDetail] = useState<EntityDetail | null>(null)

  useEffect(() => {
    if (!entity) {
      setDetail(null)
      return
    }
    setDetail(null)
    fetchEntityDetail(entity.properties.slug).then(setDetail).catch(() => {})
  }, [entity?.properties.slug])

  if (!entity) return null

  const { name, type, color, confidence_type, source_name } = entity.properties
  const confidenceLabel = CONFIDENCE_LABELS[confidence_type] ?? confidence_type

  const contemporaries = currentEntities.filter(
    (f) => f.properties.slug !== entity.properties.slug
  )

  const yearStart = detail?.year_start ?? entity.properties.year_start
  const yearEnd = detail?.year_end ?? entity.properties.year_end

  return (
    <div
      className="absolute top-4 right-4 w-80 max-h-[calc(100vh-6rem)] overflow-y-auto bg-black/85 backdrop-blur-md text-white rounded-xl p-5 border border-white/10 shadow-2xl"
      role="complementary"
      aria-label={`Entity: ${name}`}
    >
      <button
        onClick={() => setSelectedEntity(null)}
        className="absolute top-3 right-4 text-white/40 hover:text-white text-xl leading-none transition-colors"
        aria-label="Close entity panel"
      >
        ×
      </button>

      {/* Header */}
      <div className="flex items-center gap-3 mb-3 pr-6">
        <div
          className="w-4 h-4 rounded-sm flex-shrink-0 border border-white/20"
          style={{ backgroundColor: color }}
          aria-hidden="true"
        />
        <h2 className="font-bold text-lg leading-tight">{name}</h2>
      </div>

      {/* Core info */}
      <dl className="space-y-1 text-sm">
        <div className="flex gap-2">
          <dt className="text-white/40 w-16 flex-shrink-0">Type</dt>
          <dd className="text-white/80 capitalize">{type}</dd>
        </div>
        {(yearStart !== undefined) && (
          <div className="flex gap-2">
            <dt className="text-white/40 w-16 flex-shrink-0">Dates</dt>
            <dd className="text-white/80">
              {yearToDisplay(yearStart)} – {yearEnd !== null && yearEnd !== undefined ? yearToDisplay(yearEnd) : 'present'}
            </dd>
          </div>
        )}
        <div className="flex gap-2">
          <dt className="text-white/40 w-16 flex-shrink-0">Boundary</dt>
          <dd className="text-white/60 text-xs leading-relaxed">{confidenceLabel}</dd>
        </div>
        {source_name && (
          <div className="flex gap-2">
            <dt className="text-white/40 w-16 flex-shrink-0">Source</dt>
            <dd className="text-white/50 text-xs leading-relaxed">{source_name}</dd>
          </div>
        )}
      </dl>

      {/* Lineage */}
      {detail && (
        <LineageTree
          predecessors={detail.lineage.predecessors}
          successors={detail.lineage.successors}
        />
      )}

      {/* Contemporaries */}
      {contemporaries.length > 0 && (
        <div className="mt-3 pt-3 border-t border-white/10">
          <h3 className="text-white/40 text-xs uppercase tracking-widest mb-2">
            Contemporaries in {yearToDisplay(year)}
          </h3>
          <div className="space-y-1">
            {contemporaries.slice(0, 8).map((f) => (
              <div key={f.properties.slug} className="flex items-center gap-2 text-sm">
                <div
                  className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                  style={{ backgroundColor: f.properties.color }}
                  aria-hidden="true"
                />
                <span className="text-white/70 truncate">{f.properties.name}</span>
              </div>
            ))}
            {contemporaries.length > 8 && (
              <div className="text-white/30 text-xs">+{contemporaries.length - 8} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 8: Run tests**

```bash
cd apps/web && npm run test -- --run __tests__/entityPanel.test.tsx
```

Expected: all 7 tests pass.

```bash
npm run test -- --run
```

Expected: all existing tests pass.

- [ ] **Step 9: Commit**

```bash
git add apps/web/types/index.ts apps/web/lib/api.ts apps/web/store/timeline.ts \
        apps/web/components/map/useTerritoryLayer.ts \
        apps/web/components/entity/EntityPanel.tsx \
        apps/web/components/entity/LineageTree.tsx \
        apps/web/__tests__/entityPanel.test.tsx
git commit -m "feat(m4-c): enhanced entity panel — dates, lineage chain, contemporaries"
```

---

## Task M4-D: Timeline UX Upgrade

**Files:**
- Modify: `apps/web/lib/year.ts`
- Modify: `apps/web/components/timeline/TimelineSlider.tsx`
- Create: `apps/web/__tests__/timelineSlider.test.tsx`

Adds keyboard navigation (←/→ move to prev/next snapshot), a click-to-edit year display, and era marker ticks.

**Era definitions:**
```
Ancient:      -3000 to -500
Classical:    -500 to 500
Medieval:     500 to 1500
Early Modern: 1500 to 1800
Modern:       1800 to 2026
```

- [ ] **Step 1: Write failing tests**

Create `apps/web/__tests__/timelineSlider.test.tsx`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { useTimelineStore } from '@/store/timeline'
import { ERA_MARKERS, snapToPrevSnapshot, snapToNextSnapshot } from '@/lib/year'

beforeEach(() => {
  useTimelineStore.setState({ year: -264 })
})

describe('ERA_MARKERS', () => {
  it('contains Ancient, Classical, Medieval, Early Modern, Modern', () => {
    const labels = ERA_MARKERS.map((e) => e.label)
    expect(labels).toContain('Ancient')
    expect(labels).toContain('Classical')
    expect(labels).toContain('Medieval')
    expect(labels).toContain('Early Modern')
    expect(labels).toContain('Modern')
  })

  it('each marker has year and label', () => {
    ERA_MARKERS.forEach((m) => {
      expect(typeof m.year).toBe('number')
      expect(typeof m.label).toBe('string')
    })
  })
})

describe('snapToPrevSnapshot', () => {
  it('moves to previous snapshot year', () => {
    const prev = snapToPrevSnapshot(-264)
    expect(prev).toBeLessThan(-264)
  })

  it('does not go below minimum snapshot', () => {
    const prev = snapToPrevSnapshot(-3000)
    expect(prev).toBe(-3000)
  })
})

describe('snapToNextSnapshot', () => {
  it('moves to next snapshot year', () => {
    const next = snapToNextSnapshot(-264)
    expect(next).toBeGreaterThan(-264)
  })

  it('does not exceed maximum snapshot', () => {
    const next = snapToNextSnapshot(2026)
    expect(next).toBe(2026)
  })
})

describe('TimelineSlider keyboard navigation', () => {
  it('ArrowRight advances year', () => {
    render(<TimelineSlider />)
    const slider = screen.getByRole('slider', { name: /timeline year/i })
    fireEvent.keyDown(slider, { key: 'ArrowRight' })
    expect(useTimelineStore.getState().year).toBeGreaterThan(-264)
  })

  it('ArrowLeft retreats year', () => {
    render(<TimelineSlider />)
    const slider = screen.getByRole('slider', { name: /timeline year/i })
    fireEvent.keyDown(slider, { key: 'ArrowLeft' })
    expect(useTimelineStore.getState().year).toBeLessThan(-264)
  })

  it('renders era labels', () => {
    render(<TimelineSlider />)
    expect(screen.getByText('Classical')).toBeDefined()
    expect(screen.getByText('Medieval')).toBeDefined()
  })
})
```

Run: `cd apps/web && npm run test -- --run __tests__/timelineSlider.test.tsx`
Expected: ImportError on `ERA_MARKERS`, `snapToPrevSnapshot`, `snapToNextSnapshot`.

- [ ] **Step 2: Add ERA_MARKERS and snapshot navigation helpers to year.ts**

Edit `apps/web/lib/year.ts`, add at the end (after existing exports):

```typescript
export interface EraMark {
  year: number
  label: string
}

export const ERA_MARKERS: EraMark[] = [
  { year: -3000, label: 'Ancient' },
  { year: -500,  label: 'Classical' },
  { year: 500,   label: 'Medieval' },
  { year: 1500,  label: 'Early Modern' },
  { year: 1800,  label: 'Modern' },
]

export function snapToPrevSnapshot(year: number): number {
  const idx = SNAPSHOT_YEARS.indexOf(year)
  if (idx <= 0) return SNAPSHOT_YEARS[0]
  return SNAPSHOT_YEARS[idx - 1]
}

export function snapToNextSnapshot(year: number): number {
  const idx = SNAPSHOT_YEARS.indexOf(year)
  if (idx < 0) {
    // year not a snapshot — snap forward to nearest snapshot above
    const above = SNAPSHOT_YEARS.find((y) => y > year)
    return above ?? SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]
  }
  if (idx >= SNAPSHOT_YEARS.length - 1) return SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]
  return SNAPSHOT_YEARS[idx + 1]
}
```

Note: `SNAPSHOT_YEARS` must be exported from `year.ts`. If it's not already, add `export` to its declaration.

- [ ] **Step 3: Rewrite TimelineSlider.tsx**

Replace `apps/web/components/timeline/TimelineSlider.tsx` entirely:

```typescript
'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { useTimelineStore } from '@/store/timeline'
import {
  yearToDisplay,
  sliderToYear,
  yearToSlider,
  ERA_MARKERS,
  snapToPrevSnapshot,
  snapToNextSnapshot,
  SNAPSHOT_YEARS,
} from '@/lib/year'

const SLIDER_MIN = 0
const SLIDER_MAX = 5025

const YEAR_MIN = SNAPSHOT_YEARS[0]
const YEAR_MAX = SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]

function eraPercent(year: number): number {
  return ((yearToSlider(year) - SLIDER_MIN) / (SLIDER_MAX - SLIDER_MIN)) * 100
}

export function TimelineSlider() {
  const year = useTimelineStore((s) => s.year)
  const setYear = useTimelineStore((s) => s.setYear)
  const [editing, setEditing] = useState(false)
  const [editValue, setEditValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  function handleSliderChange(e: React.ChangeEvent<HTMLInputElement>) {
    setYear(sliderToYear(Number(e.target.value)))
  }

  function handleSliderKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      setYear(snapToNextSnapshot(year))
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      setYear(snapToPrevSnapshot(year))
    }
  }

  function startEditing() {
    setEditValue(String(Math.abs(year)))
    setEditing(true)
  }

  useEffect(() => {
    if (editing && inputRef.current) inputRef.current.focus()
  }, [editing])

  function commitEdit() {
    const raw = parseInt(editValue, 10)
    if (!isNaN(raw)) {
      const signed = editValue.toLowerCase().includes('b') ? -raw : raw
      const clamped = Math.max(YEAR_MIN, Math.min(YEAR_MAX, signed === 0 ? 1 : signed))
      setYear(clamped)
    }
    setEditing(false)
  }

  function handleEditKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') commitEdit()
    if (e.key === 'Escape') setEditing(false)
  }

  return (
    <div className="absolute bottom-0 left-0 right-0 px-8 pb-6 pt-12 bg-gradient-to-t from-black/90 to-transparent pointer-events-none select-none">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        {/* Year display / edit */}
        <div className="text-center mb-3">
          {editing ? (
            <input
              ref={inputRef}
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={commitEdit}
              onKeyDown={handleEditKeyDown}
              className="bg-transparent border-b border-amber-400 text-white text-3xl font-bold text-center w-40 outline-none tracking-widest"
              aria-label="Enter year"
            />
          ) : (
            <button
              onClick={startEditing}
              className="text-white text-3xl font-bold tracking-widest drop-shadow-lg hover:text-amber-300 transition-colors"
              aria-label={`Current year: ${yearToDisplay(year)}. Click to jump to year.`}
              title="Click to jump to year"
            >
              {yearToDisplay(year)}
            </button>
          )}
        </div>

        {/* Era markers row */}
        <div className="relative h-5 mb-1">
          {ERA_MARKERS.map((era) => (
            <button
              key={era.label}
              onClick={() => setYear(era.year === -3000 ? -3000 : era.year + 1)}
              style={{ left: `${eraPercent(era.year)}%` }}
              className="absolute -translate-x-1/2 text-white/35 text-xs hover:text-amber-300 transition-colors leading-none"
              title={`Jump to ${era.label} era`}
            >
              {era.label}
            </button>
          ))}
        </div>

        {/* Slider */}
        <div className="relative">
          <input
            type="range"
            min={SLIDER_MIN}
            max={SLIDER_MAX}
            step={1}
            value={yearToSlider(year)}
            onChange={handleSliderChange}
            onKeyDown={handleSliderKeyDown}
            aria-label="Timeline year"
            className="w-full h-1.5 cursor-pointer accent-amber-400 rounded-full"
          />
        </div>

        {/* Min/max labels */}
        <div className="flex justify-between text-white/40 text-xs mt-1.5 font-mono">
          <span>3000 BCE</span>
          <span>1 BCE / 1 CE</span>
          <span>2026 CE</span>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```bash
cd apps/web && npm run test -- --run __tests__/timelineSlider.test.tsx
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/year.ts apps/web/components/timeline/TimelineSlider.tsx \
        apps/web/__tests__/timelineSlider.test.tsx
git commit -m "feat(m4-d): timeline UX — keyboard nav, era markers, click-to-edit year"
```

---

## Task M4-E: Territory Focus Mode + Hover Tooltip

**Files:**
- Modify: `apps/web/components/map/MapView.tsx`
- Modify: `apps/web/components/map/MapContainer.tsx`

When an entity is selected: dim all other territories to 15% opacity, highlight selected to 75%. On territory hover: show a MapLibre popup with entity name and territory dates.

- [ ] **Step 1: Add selectedSlug prop to MapView**

In `apps/web/components/map/MapView.tsx`, update `MapViewProps`:

```typescript
export interface MapViewProps {
  onEntitySelect: (entity: EntityFeature | null) => void
  onViewportChange?: (viewport: Viewport) => void
  selectedSlug?: string | null
}
```

Update the component signature:

```typescript
const MapView = forwardRef<MapViewHandle, MapViewProps>(
  ({ onEntitySelect, onViewportChange, selectedSlug }, ref) => {
```

Add a ref to mirror selectedSlug (like onViewportChange pattern):

```typescript
const selectedSlugRef = useRef(selectedSlug)
useEffect(() => { selectedSlugRef.current = selectedSlug }, [selectedSlug])
```

Add a new `useEffect` that fires when `selectedSlug` changes (after the map init effect):

```typescript
useEffect(() => {
  const map = mapRef.current
  if (!map || !map.isStyleLoaded()) return

  if (selectedSlug) {
    map.setPaintProperty('territories-fill', 'fill-opacity', [
      'case',
      ['==', ['get', 'slug'], selectedSlug], 0.75,
      ['boolean', ['feature-state', 'hover'], false], 0.55,
      0.15,
    ])
    map.setPaintProperty('territories-border', 'line-opacity', [
      'case',
      ['==', ['get', 'slug'], selectedSlug], 1.0,
      0.3,
    ])
  } else {
    map.setPaintProperty('territories-fill', 'fill-opacity', [
      'case',
      ['boolean', ['feature-state', 'hover'], false], 0.65,
      0.4,
    ])
    map.setPaintProperty('territories-border', 'line-opacity', 0.9)
  }
}, [selectedSlug])
```

Add hover tooltip using `maplibregl.Popup`. Inside the `map.on('load', ...)` handler, after the click/hover setup, add:

```typescript
// Hover tooltip
const popup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
  offset: 8,
  className: 'history-tooltip',
})

map.on('mousemove', 'territories-fill', (e) => {
  if (!e.features?.length) return
  const props = e.features[0].properties as EntityProperties
  const yearStart = props.year_start
  const yearEnd = props.year_end
  const dateStr = yearStart !== undefined
    ? `${yearToDisplay(yearStart)} – ${yearEnd !== null && yearEnd !== undefined ? yearToDisplay(yearEnd) : 'present'}`
    : ''
  popup
    .setLngLat(e.lngLat)
    .setHTML(`<div class="font-semibold">${props.name}</div>${dateStr ? `<div class="text-xs opacity-70">${dateStr}</div>` : ''}`)
    .addTo(map)
})

map.on('mouseleave', 'territories-fill', () => {
  popup.remove()
})
```

Add import for `yearToDisplay` at the top of MapView.tsx:
```typescript
import { yearToDisplay } from '@/lib/year'
```

Add popup CSS to `apps/web/app/globals.css` (or layout.tsx if using inline styles). Add after existing styles:

```css
.history-tooltip .maplibregl-popup-content {
  background: rgba(0, 0, 0, 0.85);
  color: white;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.history-tooltip .maplibregl-popup-tip {
  border-top-color: rgba(0,0,0,0.85);
}
```

- [ ] **Step 2: Pass selectedSlug from MapContainer**

Edit `apps/web/components/map/MapContainer.tsx`. The `MapView` component is rendered there. Pass the prop:

```typescript
const selectedSlug = useTimelineStore((s) => s.selectedEntity?.properties.slug ?? null)

// In JSX:
<MapView
  ref={mapRef}
  onEntitySelect={setSelectedEntity}
  onViewportChange={handleViewportChange}
  selectedSlug={selectedSlug}
/>
```

- [ ] **Step 3: Smoke test visually**

```bash
cd apps/web && npm run dev
```

Open `http://localhost:3000`. Click a territory. Verify:
- Selected territory is bright (75% opacity)
- All other territories dim to 15% opacity
- Hovering a territory shows popup with name + dates
- Clicking empty space deselects and all territories return to 40% opacity

- [ ] **Step 4: Commit**

```bash
git add apps/web/components/map/MapView.tsx apps/web/components/map/MapContainer.tsx
git commit -m "feat(m4-e): territory focus mode — dim non-selected, hover tooltip with dates"
```

---

## Task M4-F: Frontend Entity Search

**Files:**
- Create: `apps/web/components/ui/SearchBar.tsx`
- Modify: `apps/web/components/map/MapContainer.tsx`

A search bar in the top-left corner that filters entity names from the current world state and selects the entity on click.

- [ ] **Step 1: Create SearchBar.tsx**

Create `apps/web/components/ui/SearchBar.tsx`:

```typescript
'use client'

import { useState, useRef, useEffect } from 'react'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

export function SearchBar() {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const currentEntities = useTimelineStore((s) => s.currentEntities)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const containerRef = useRef<HTMLDivElement>(null)

  const trimmed = query.trim().toLowerCase()
  const results: EntityFeature[] = trimmed.length < 1
    ? []
    : currentEntities
        .filter((f) => f.properties.name.toLowerCase().includes(trimmed))
        .slice(0, 10)

  function select(entity: EntityFeature) {
    setSelectedEntity(entity)
    setQuery('')
    setOpen(false)
  }

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  return (
    <div ref={containerRef} className="absolute top-4 left-4 w-64 z-10">
      <input
        type="search"
        value={query}
        onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
        onFocus={() => setOpen(true)}
        placeholder="Search civilizations…"
        className="w-full bg-black/70 backdrop-blur-md text-white placeholder-white/30 rounded-lg px-3 py-2 text-sm border border-white/10 outline-none focus:border-amber-400/50 transition-colors"
        aria-label="Search civilizations"
        aria-expanded={open && results.length > 0}
        aria-haspopup="listbox"
        role="combobox"
        autoComplete="off"
      />
      {open && results.length > 0 && (
        <ul
          className="mt-1 bg-black/90 backdrop-blur-md rounded-lg border border-white/10 shadow-2xl overflow-hidden"
          role="listbox"
          aria-label="Search results"
        >
          {results.map((entity) => (
            <li key={entity.properties.slug}>
              <button
                onClick={() => select(entity)}
                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/80 hover:bg-white/10 transition-colors text-left"
                role="option"
              >
                <div
                  className="w-3 h-3 rounded-sm flex-shrink-0"
                  style={{ backgroundColor: entity.properties.color }}
                  aria-hidden="true"
                />
                <span className="truncate">{entity.properties.name}</span>
                <span className="text-white/30 text-xs flex-shrink-0 capitalize ml-auto">
                  {entity.properties.type}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Add SearchBar to MapContainer**

Edit `apps/web/components/map/MapContainer.tsx`, import and render `SearchBar`:

```typescript
import { SearchBar } from '@/components/ui/SearchBar'

// In JSX, inside the container div, alongside other overlays:
<SearchBar />
```

- [ ] **Step 3: Smoke test**

```bash
cd apps/web && npm run dev
```

Open `http://localhost:3000`. Type "roman" in search bar. Verify dropdown shows "Roman Empire", "Roman Republic", etc. Click one — entity panel opens for that civilization.

- [ ] **Step 4: Commit**

```bash
git add apps/web/components/ui/SearchBar.tsx apps/web/components/map/MapContainer.tsx
git commit -m "feat(m4-f): entity search bar — filter and select civilizations from current world state"
```

---

## Task M4-G: Redis Startup Cache Warming

**Files:**
- Modify: `apps/api/app/services/cache_service.py`
- Modify: `apps/api/app/main.py`

On API startup, warm the Redis cache for high-value snapshot years at world zoom so first page loads are instant. Warms in background (non-blocking).

**Key years to warm** (25 years spaced, full world, zoom 4 — covers typical first-visit range):
```python
WARM_YEARS = list(range(-500, 501, 25)) + [1000, 1250, 1500, 1750, 2000]
# Skip year 0
WARM_YEARS = [y for y in WARM_YEARS if y != 0]
```

- [ ] **Step 1: Add warm_startup_cache to cache_service.py**

Edit `apps/api/app/services/cache_service.py`, add:

```python
WARM_YEARS = [y for y in list(range(-500, 501, 25)) + [1000, 1250, 1500, 1750, 2000] if y != 0]

async def is_world_state_cached(self, year: int, layer: str, zoom: int) -> bool:
    """Check if full-world snapshot is cached at given zoom."""
    tile_x = int(-180 // 10)  # -18 (full world)
    tile_y = int(-90 // 10)   # -9
    key = f"worldstate:{year}:{layer}:{zoom}:{tile_x}:{tile_y}"
    return await self.redis.exists(key) == 1
```

- [ ] **Step 2: Add startup event to main.py**

Edit `apps/api/app/main.py`, add after the app initialization and before the include_router calls:

```python
import asyncio
from app.database import async_session_factory
from app.cache import get_redis_client
from app.services.world_state import WorldStateService, SNAPSHOT_YEARS
from app.services.cache_service import CacheService, WARM_YEARS

async def _warm_cache_task():
    """Background task: pre-populate Redis for common snapshot years."""
    await asyncio.sleep(2)  # let the app fully start first
    try:
        redis = await get_redis_client()
        cache = CacheService(redis=redis)
        async with async_session_factory() as db:
            svc = WorldStateService(db=db)
            warmed = 0
            for year in WARM_YEARS:
                if year not in SNAPSHOT_YEARS:
                    continue
                if await cache.is_world_state_cached(year, "political", 4):
                    continue
                result = await svc.get_state(
                    year=year, bbox=(-180, -90, 180, 90), zoom=4
                )
                await cache.set_world_state(year, "political", 4, -18, -9, result)
                warmed += 1
            print(f"[startup] Cache warmed: {warmed} snapshots")
    except Exception as e:
        print(f"[startup] Cache warming failed (non-fatal): {e}")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_warm_cache_task())
```

Note: `get_redis_client` returns an async Redis client directly (not a generator). Check `apps/api/app/cache.py` — if it's `get_redis` as a dependency generator, create a separate `get_redis_client()` function that returns the raw client, or reuse the existing pattern. If `cache.py` has `get_redis()` as a FastAPI dependency (yields), you need to call it differently in a non-request context. Use:

```python
# If cache.py has: async def get_redis(): yield redis_client
# Then use the redis client from settings directly:
from aioredis import from_url
from app.config import settings

redis = await from_url(settings.redis_url, decode_responses=True)
```

Adjust based on what `cache.py` actually exports.

- [ ] **Step 3: Verify startup warming**

```bash
cd c:/History
docker compose -f infra/docker-compose.yml restart api
docker compose -f infra/docker-compose.yml logs api --follow
```

Expected log output: `[startup] Cache warmed: N snapshots` (N > 0 on first run, 0 on restart since already cached).

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/services/cache_service.py apps/api/app/main.py
git commit -m "feat(m4-g): Redis startup cache warming — pre-populate common snapshot years"
```

---

## Task M4-H: Visual Atmosphere Polish

**Files:**
- Modify: `apps/web/components/timeline/TimelineSlider.tsx` (accent color refinement — already done in M4-D)
- Modify: `apps/web/components/ui/AttributionFooter.tsx` (style cleanup)
- Modify: `apps/web/components/ui/LoadingOverlay.tsx` (badge style refinement)

Minor visual touches that complete the historical aesthetic without adding new features. Three specific changes:

1. **Loading overlay**: change "Loading" text to use amber accent and improve layout
2. **Attribution footer**: adjust to match the new darker map background
3. **Slider thumb**: already amber-400 from M4-D — ensure consistent

- [ ] **Step 1: Read current LoadingOverlay**

```bash
cat apps/web/components/ui/LoadingOverlay.tsx
```

- [ ] **Step 2: Polish LoadingOverlay**

Replace `apps/web/components/ui/LoadingOverlay.tsx` content to add a subtle pulsing amber dot:

```typescript
'use client'

import { useTimelineStore } from '@/store/timeline'

export function LoadingOverlay() {
  const isLoading = useTimelineStore((s) => s.isLoading)
  const error = useTimelineStore((s) => s.error)

  if (!isLoading && !error) return null

  return (
    <div
      className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/75 backdrop-blur-md text-white text-sm px-4 py-2 rounded-full border border-white/10 shadow-lg"
      role="status"
      aria-live="polite"
    >
      {isLoading && (
        <>
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" aria-hidden="true" />
          <span>Loading…</span>
        </>
      )}
      {error && (
        <>
          <span className="w-2 h-2 rounded-full bg-red-400" aria-hidden="true" />
          <span className="text-red-300">{error}</span>
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Smoke test**

```bash
cd apps/web && npm run dev
```

Open `http://localhost:3000`. Drag timeline slider to see loading indicator pulse amber while fetching. Verify it disappears after data loads.

- [ ] **Step 4: Commit**

```bash
git add apps/web/components/ui/LoadingOverlay.tsx
git commit -m "feat(m4-h): visual atmosphere — loading indicator refinement, amber pulse"
```

---

## Task M4-I: M4 Test Suite Completion

**Files:**
- Modify: `apps/api/tests/test_entity_detail.py` (add integration coverage)
- Modify: `apps/web/__tests__/entityPanel.test.tsx` (finalize)
- Modify: `apps/web/__tests__/timelineSlider.test.tsx` (finalize)

Run the full test suite, fix any failures introduced by M4, verify coverage of new code.

- [ ] **Step 1: Run full backend test suite**

```bash
cd c:/History
pytest apps/api/tests/ -v --tb=short 2>&1 | tail -30
```

Expected: all tests pass. Fix any failures before continuing.

Common failure patterns:
- `test_world_state_m3.py` mocks missing `year_start`/`year_end` in row dicts → add to any row stubs
- `test_place_names.py` unaffected (different service)
- `test_debug_endpoints.py` unaffected

- [ ] **Step 2: Run full frontend test suite**

```bash
cd apps/web && npm run test -- --run
```

Expected: all tests pass. Fix any TypeScript type failures from `EntityProperties` changes (add `year_start: number, year_end: number | null` to all mock objects in test files).

Files that may need mock updates:
- `apps/web/__tests__/timeline.test.ts` — two mock EntityProperties need `year_start: -27, year_end: 476`
- `apps/web/__tests__/usePlaceNamesLayer.test.ts` — unaffected (different types)
- `apps/web/__tests__/useRiversLayer.test.ts` — unaffected

- [ ] **Step 3: Add backend snapshot test for entity detail**

Add to `apps/api/tests/test_entity_detail.py` a live DB integration test (skipped unless `HISTORY_TEST_DB` env var set):

```python
import os
import pytest

@pytest.mark.skipif(
    not os.environ.get("HISTORY_TEST_DB"),
    reason="requires live DB"
)
def test_roman_empire_detail_live():
    """Smoke test against live DB: roman-empire must have lineage predecessors."""
    import asyncio, psycopg2
    from app.database import async_session_factory
    from app.services.entity_service import EntityService

    async def run():
        async with async_session_factory() as db:
            svc = EntityService(db=db)
            return await svc.get_entity_detail("roman-empire")

    result = asyncio.get_event_loop().run_until_complete(run())
    assert result is not None
    assert result["name"] == "Roman Empire"
    assert len(result["lineage"]["predecessors"]) >= 1
```

- [ ] **Step 4: Count and verify test coverage**

```bash
pytest apps/api/tests/ -v --tb=short | grep -E "passed|failed|error"
cd apps/web && npm run test -- --run | grep -E "Tests|pass|fail"
```

Expected:
- Backend: ≥ 80 tests passing (prev 64 + ~16 new from M4-B/M4-I)
- Frontend: ≥ 20 tests passing (prev ~10 + ~13 new from M4-C/M4-D)

- [ ] **Step 5: Final commit**

```bash
git add apps/api/tests/ apps/web/__tests__/
git commit -m "test(m4-i): complete M4 test suite — entity detail, timeline keyboard, entity panel"
```

---

## Self-Review

### Spec Coverage

| Spec Priority | Covered by |
|---------------|-----------|
| 1. Historical Base Map | M4-A ✓ |
| 2. Entity Exploration Panel | M4-B + M4-C ✓ |
| 3. Timeline Experience | M4-D ✓ |
| 4. Historical Context Awareness | M4-C contemporaries ✓ |
| 5. Redis Snapshot Caching | M4-G ✓ |
| 6. Territory Interaction Polish | M4-E ✓ |
| 7. Lineage Visualization | M4-C LineageTree ✓ |
| 8. Capitals & Historical Cities | **DEFERRED to M5** — no data exists yet |
| 9. Search & Discovery | M4-F ✓ |
| 10. Historical Atmosphere & Identity | M4-A + M4-H ✓ |

### Placeholder Scan

No TBD/TODO markers. All code blocks contain actual implementations.

### Type Consistency

- `EntityProperties.year_start/year_end` added in M4-B, used in M4-C (EntityPanel), M4-E (MapView tooltip)
- `EntityDetail` defined in M4-C types/index.ts, used in EntityPanel, api.ts
- `LineageEntry` defined in M4-C types/index.ts, used in LineageTree
- `ERA_MARKERS`, `snapToPrevSnapshot`, `snapToNextSnapshot` defined in M4-D year.ts, used in TimelineSlider
- `currentEntities: EntityFeature[]` added to store in M4-C, populated in useTerritoryLayer in M4-C, read in EntityPanel and SearchBar
- `selectedSlug` prop on MapViewProps added in M4-E, passed from MapContainer in M4-E

All types introduced in earlier tasks match usage in later tasks.

### What Is NOT in M4

- `entity_capitals` table data — table exists, no cities data ingested; capitals rendering deferred to M5
- Autoplay / playback mode — omitted (complex state machine, low ROI vs M5 data work)
- Mobile layout — omitted (desktop-first; would need significant responsive redesign)
- Accessibility deep work — basic aria-labels maintained from existing code; full audit deferred
- Full lineage graph explorer — simple list in LineageTree is sufficient for M4
