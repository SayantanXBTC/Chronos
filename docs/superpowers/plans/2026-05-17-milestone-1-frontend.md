# Milestone 1: Interactive Temporal Map Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A user can drag a global timeline slider (-500 BCE to 500 CE) and watch civilization territory borders update dynamically on a fullscreen world map. Smooth experience with no map reinitialization on year change and no unnecessary rerenders.

**Architecture:** MapLibre GL JS map instance lives in a `useRef` and is initialized exactly once. Year changes from a Zustand store flow through a debounced hook (`useTerritoryLayer`) that fetches GeoJSON from the backend API and calls `source.setData()` — no layer or map recreation ever occurs. MapView exposes an imperative handle via `forwardRef` + `useImperativeHandle` so the parent hook can push data without MapView subscribing to Zustand directly. SSR is bypassed for MapView using Next.js `dynamic` import. An LRU in-memory cache (max 50 entries) avoids redundant network requests. Each fetch is protected by an `AbortController` so rapid slider movement cancels in-flight requests.

**Tech Stack:** Next.js 14 (App Router, TypeScript, Tailwind CSS), MapLibre GL JS, Zustand, Vitest + React Testing Library. Backend: FastAPI on port 8000 (Milestone 0, already complete).

---

## File Map

```
apps/web/
  app/
    page.tsx                           # Renders <MapContainer />
    layout.tsx                         # html + body h-full overflow-hidden bg-zinc-900
    globals.css                        # @tailwind base/components/utilities
  components/
    map/
      MapContainer.tsx                 # Client: dynamic MapView + all overlays + useTerritoryLayer
      MapView.tsx                      # Client: MapLibre init, source, layers, hover/click handlers
      useTerritoryLayer.ts             # Hook: year watch → debounce → fetch → setData
    timeline/
      TimelineSlider.tsx               # Range input 0-999, yearToDisplay label, Zustand setYear
    entity/
      EntityPanel.tsx                  # Absolute panel: entity name, color badge, type, confidence
    ui/
      LoadingOverlay.tsx               # Spinner overlay when isLoading=true; error banner otherwise
  lib/
    api.ts                             # fetchWorldState(year, {signal?}), fetchSnapshots()
    year.ts                            # yearToDisplay, sliderToYear, yearToSlider, snapToSnapshot, SNAPSHOT_YEARS
    cache.ts                           # SnapshotCache class (Map<number, WorldStateResponse>, maxSize=50)
  store/
    timeline.ts                        # Zustand: { year, selectedEntity, isLoading, error, setters }
  types/
    index.ts                           # EntityProperties, EntityFeature, WorldStateResponse interfaces
  __tests__/
    year.test.ts                       # Tests for all year.ts exports
    cache.test.ts                      # Tests for SnapshotCache
    api.test.ts                        # Tests for fetchWorldState, fetchSnapshots (mock fetch)
    timeline.test.ts                   # Tests for useTimelineStore
  vitest.config.ts
  vitest.setup.ts
```

---

## Task 1: Next.js Scaffold + Dependencies

**Files:**
- Create: `apps/web/` (entire Next.js app scaffold)
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/vitest.setup.ts`
- Modify: `apps/web/package.json` (add test scripts)
- Modify: `apps/web/.env.local` (add env vars)
- Modify: root `.env` (add NEXT_PUBLIC vars)
- Modify: `apps/web/app/layout.tsx` (h-full, overflow-hidden)

- [ ] Step 1: Scaffold the Next.js app from the repo root. Accept all defaults when prompted.

```bash
cd c:/History && npx create-next-app@latest apps/web --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*"
```

Expected: `apps/web/` directory created with `app/`, `public/`, `package.json`, `tsconfig.json`, `tailwind.config.ts`, `next.config.ts`.

- [ ] Step 2: Install runtime dependencies.

```bash
cd c:/History/apps/web && npm install maplibre-gl zustand
```

- [ ] Step 3: Install dev/test dependencies.

```bash
cd c:/History/apps/web && npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom @types/geojson
```

- [ ] Step 4: Create `apps/web/vitest.config.ts`.

```typescript
// apps/web/vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
})
```

- [ ] Step 5: Create `apps/web/vitest.setup.ts`.

```typescript
// apps/web/vitest.setup.ts
import '@testing-library/jest-dom'
```

- [ ] Step 6: Add test scripts to `apps/web/package.json`. Open the file and add to the `"scripts"` object:

```json
"test": "vitest run",
"test:watch": "vitest"
```

Full scripts block should look like:
```json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] Step 7: Create `apps/web/.env.local` with the following content (create the file if it does not exist):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAP_STYLE=https://tiles.openfreemap.org/styles/liberty
```

- [ ] Step 8: Add the same variables to the root `.env` file (append, do not remove existing lines):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAP_STYLE=https://tiles.openfreemap.org/styles/liberty
```

- [ ] Step 9: Replace `apps/web/app/layout.tsx` with the following (sets `h-full` on `<html>` and `h-full overflow-hidden bg-zinc-900` on `<body>`):

```typescript
// apps/web/app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'History Platform',
  description: 'Interactive temporal world map',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden bg-zinc-900">{children}</body>
    </html>
  )
}
```

- [ ] Step 10: Verify dev server starts without errors.

```bash
cd c:/History/apps/web && npm run dev
```

Navigate to `http://localhost:3000` — the default Next.js page should render. Stop with Ctrl+C.

- [ ] Step 11: Commit.

```bash
cd c:/History && git add apps/web && git commit -m "feat: scaffold Next.js 14 app with MapLibre, Zustand, Vitest"
```

---

## Task 2: Shared Types + Year Utilities (TDD)

**Files:**
- Create: `apps/web/types/index.ts`
- Create: `apps/web/__tests__/year.test.ts`
- Create: `apps/web/lib/year.ts`

- [ ] Step 1: Create `apps/web/types/index.ts` with all shared TypeScript interfaces used throughout the app.

```typescript
// apps/web/types/index.ts
import type { Feature, MultiPolygon } from 'geojson'

/**
 * Properties returned on each GeoJSON feature from the backend.
 */
export interface EntityProperties {
  entity_id: string
  slug: string
  name: string
  type: string          // e.g. "empire", "kingdom", "republic"
  color: string         // CSS hex color, e.g. "#C0392B"
  confidence: string    // e.g. "approximate", "certain"
}

/**
 * A single GeoJSON Feature for a historical entity territory.
 */
export type EntityFeature = Feature<MultiPolygon, EntityProperties>

/**
 * The full response from GET /api/v1/world/state
 */
export interface WorldStateResponse {
  type: 'FeatureCollection'
  year: number
  snapshot_year: number
  features: EntityFeature[]
}

/**
 * Response from GET /api/v1/world/snapshots
 */
export interface SnapshotsResponse {
  snapshots: number[]
}
```

- [ ] Step 2: Write all tests for `lib/year.ts` BEFORE implementing it. Run vitest and confirm all tests FAIL (expected — the module does not exist yet).

```typescript
// apps/web/__tests__/year.test.ts
import { describe, it, expect } from 'vitest'
import { yearToDisplay, sliderToYear, yearToSlider, snapToSnapshot, SNAPSHOT_YEARS } from '@/lib/year'

describe('SNAPSHOT_YEARS', () => {
  it('has 40 values', () => { expect(SNAPSHOT_YEARS).toHaveLength(40) })
  it('starts at -500', () => { expect(SNAPSHOT_YEARS[0]).toBe(-500) })
  it('ends at 500', () => { expect(SNAPSHOT_YEARS[39]).toBe(500) })
  it('excludes 0', () => { expect(SNAPSHOT_YEARS).not.toContain(0) })
  it('contains -475', () => { expect(SNAPSHOT_YEARS).toContain(-475) })
  it('contains 25', () => { expect(SNAPSHOT_YEARS).toContain(25) })
})

describe('yearToDisplay', () => {
  it('negative year is BCE', () => { expect(yearToDisplay(-264)).toBe('264 BCE') })
  it('positive year is CE', () => { expect(yearToDisplay(117)).toBe('117 CE') })
  it('throws on 0', () => { expect(() => yearToDisplay(0)).toThrow() })
  it('-1 is 1 BCE', () => { expect(yearToDisplay(-1)).toBe('1 BCE') })
  it('1 is 1 CE', () => { expect(yearToDisplay(1)).toBe('1 CE') })
  it('-500 is 500 BCE', () => { expect(yearToDisplay(-500)).toBe('500 BCE') })
  it('500 is 500 CE', () => { expect(yearToDisplay(500)).toBe('500 CE') })
})

describe('sliderToYear / yearToSlider roundtrip', () => {
  it('slider 0 → year -500', () => { expect(sliderToYear(0)).toBe(-500) })
  it('slider 499 → year -1', () => { expect(sliderToYear(499)).toBe(-1) })
  it('slider 500 → year 1', () => { expect(sliderToYear(500)).toBe(1) })
  it('slider 999 → year 500', () => { expect(sliderToYear(999)).toBe(500) })
  it('year -500 roundtrips', () => { expect(sliderToYear(yearToSlider(-500))).toBe(-500) })
  it('year -1 roundtrips', () => { expect(sliderToYear(yearToSlider(-1))).toBe(-1) })
  it('year 1 roundtrips', () => { expect(sliderToYear(yearToSlider(1))).toBe(1) })
  it('year 500 roundtrips', () => { expect(sliderToYear(yearToSlider(500))).toBe(500) })
  it('yearToSlider throws on 0', () => { expect(() => yearToSlider(0)).toThrow() })
})

describe('snapToSnapshot', () => {
  it('-264 snaps to -275', () => { expect(snapToSnapshot(-264)).toBe(-275) })
  it('-500 snaps to -500', () => { expect(snapToSnapshot(-500)).toBe(-500) })
  it('-275 snaps to itself', () => { expect(snapToSnapshot(-275)).toBe(-275) })
  it('100 snaps to 100', () => { expect(snapToSnapshot(100)).toBe(100) })
  it('110 snaps to 100', () => { expect(snapToSnapshot(110)).toBe(100) })
  it('1 snaps to 25 — no, 1 is between -25 and 25; largest snapshot <= 1 is 25... wait: snapshots go -25 then 25; largest <= 1 should be -25', () => {
    // -25 is the last negative snapshot before the gap; 25 is the first positive.
    // snapToSnapshot(1) => largest snapshot year that is <= 1 => -25
    expect(snapToSnapshot(1)).toBe(-25)
  })
  it('25 snaps to itself', () => { expect(snapToSnapshot(25)).toBe(25) })
})
```

Run (expect failures):
```bash
cd c:/History/apps/web && npm test -- year
```

- [ ] Step 3: Create `apps/web/lib/year.ts`. After creating, run tests again and confirm all PASS.

```typescript
// apps/web/lib/year.ts

/**
 * Snapshot years available from the backend: -500 to 500 in steps of 25, skipping 0.
 * Total: 40 values (-500, -475, ..., -25, 25, ..., 500).
 */
export const SNAPSHOT_YEARS: readonly number[] = [
  -500, -475, -450, -425, -400, -375, -350, -325, -300,
  -275, -250, -225, -200, -175, -150, -125, -100,  -75,
   -50,  -25,   25,   50,   75,  100,  125,  150,  175,
   200,  225,  250,  275,  300,  325,  350,  375,  400,
   425,  450,  475,  500,
]

/**
 * Convert an integer year (no year 0) to a human-readable string.
 * -264 → "264 BCE", 117 → "117 CE"
 * Throws if year === 0.
 */
export function yearToDisplay(year: number): string {
  if (year === 0) throw new RangeError('Year 0 does not exist in this calendar system')
  return year < 0 ? `${Math.abs(year)} BCE` : `${year} CE`
}

/**
 * Map slider value (0–999) to calendar year (-500..-1 then 1..500), skipping year 0.
 * v < 500 → v - 500   (0→-500, 499→-1)
 * v >= 500 → v - 499  (500→1, 999→500)
 */
export function sliderToYear(value: number): number {
  return value < 500 ? value - 500 : value - 499
}

/**
 * Map calendar year to slider value (inverse of sliderToYear).
 * Throws if year === 0.
 * y < 0 → y + 500  (-500→0, -1→499)
 * y > 0 → y + 499  (1→500, 500→999)
 */
export function yearToSlider(year: number): number {
  if (year === 0) throw new RangeError('Year 0 does not exist in this calendar system')
  return year < 0 ? year + 500 : year + 499
}

/**
 * Find the largest snapshot year that is less than or equal to the given year.
 * If the year is smaller than all snapshots, returns the smallest snapshot.
 */
export function snapToSnapshot(year: number): number {
  let result = SNAPSHOT_YEARS[0]
  for (const snap of SNAPSHOT_YEARS) {
    if (snap <= year) {
      result = snap
    } else {
      break
    }
  }
  return result
}
```

Run tests:
```bash
cd c:/History/apps/web && npm test -- year
```

Expected: all tests PASS.

- [ ] Step 4: Commit.

```bash
cd c:/History && git add apps/web/types apps/web/lib/year.ts apps/web/__tests__/year.test.ts && git commit -m "feat: shared types + year utilities with full test coverage"
```

---

## Task 3: API Client (TDD)

**Files:**
- Create: `apps/web/__tests__/api.test.ts`
- Create: `apps/web/lib/api.ts`

- [ ] Step 1: Write tests for `lib/api.ts` FIRST. Run vitest and confirm FAIL.

```typescript
// apps/web/__tests__/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchWorldState, fetchSnapshots } from '@/lib/api'

const mockResponse = (data: unknown, ok = true) =>
  Promise.resolve({
    ok,
    status: ok ? 200 : 500,
    json: () => Promise.resolve(data),
  } as Response)

beforeEach(() => { vi.restoreAllMocks() })

describe('fetchWorldState', () => {
  it('calls correct URL with year param', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] })
    )
    await fetchWorldState(-264)
    expect(spy).toHaveBeenCalledWith(
      expect.stringContaining('year=-264'),
      expect.anything()
    )
  })

  it('includes required query params', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] })
    )
    await fetchWorldState(-264)
    const url = spy.mock.calls[0][0] as string
    expect(url).toContain('zoom=4')
    expect(url).toContain('min_x=-180')
    expect(url).toContain('max_x=180')
  })

  it('throws on non-ok response', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse({}, false))
    await expect(fetchWorldState(-264)).rejects.toThrow('API error')
  })

  it('passes AbortSignal when provided', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: 100, snapshot_year: 100, features: [] })
    )
    const controller = new AbortController()
    await fetchWorldState(100, { signal: controller.signal })
    const init = spy.mock.calls[0][1] as RequestInit
    expect(init.signal).toBe(controller.signal)
  })

  it('returns parsed WorldStateResponse', async () => {
    const payload = { type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] }
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse(payload))
    const result = await fetchWorldState(-264)
    expect(result.year).toBe(-264)
    expect(result.type).toBe('FeatureCollection')
  })
})

describe('fetchSnapshots', () => {
  it('returns snapshots array', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ snapshots: [-500, -475] })
    )
    const result = await fetchSnapshots()
    expect(result).toEqual([-500, -475])
  })

  it('throws on non-ok response', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse({}, false))
    await expect(fetchSnapshots()).rejects.toThrow('API error')
  })
})
```

Run (expect failures):
```bash
cd c:/History/apps/web && npm test -- api
```

- [ ] Step 2: Create `apps/web/lib/api.ts`.

```typescript
// apps/web/lib/api.ts
import type { WorldStateResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

/**
 * Fetch the world GeoJSON state for a given year.
 * Sends zoom + bounding-box params required by the backend.
 * Pass an AbortSignal to cancel in-flight requests when the year changes.
 */
export async function fetchWorldState(
  year: number,
  options?: { signal?: AbortSignal }
): Promise<WorldStateResponse> {
  const params = new URLSearchParams({
    year: String(year),
    zoom: '4',
    min_x: '-180',
    min_y: '-90',
    max_x: '180',
    max_y: '90',
  })
  const res = await fetch(`${API_BASE}/api/v1/world/state?${params}`, {
    signal: options?.signal,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json() as Promise<WorldStateResponse>
}

/**
 * Fetch the list of available snapshot years from the backend.
 */
export async function fetchSnapshots(): Promise<number[]> {
  const res = await fetch(`${API_BASE}/api/v1/world/snapshots`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  const data = await res.json()
  return (data as { snapshots: number[] }).snapshots
}
```

- [ ] Step 3: Run tests and confirm all PASS.

```bash
cd c:/History/apps/web && npm test -- api
```

- [ ] Step 4: Commit.

```bash
cd c:/History && git add apps/web/lib/api.ts apps/web/__tests__/api.test.ts && git commit -m "feat: API client with abort signal support and full test coverage"
```

---

## Task 4: Zustand Timeline Store (TDD)

**Files:**
- Create: `apps/web/__tests__/timeline.test.ts`
- Create: `apps/web/store/timeline.ts`

- [ ] Step 1: Write tests for the Zustand store FIRST. Run vitest and confirm FAIL.

```typescript
// apps/web/__tests__/timeline.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

beforeEach(() => {
  useTimelineStore.setState({
    year: -264,
    selectedEntity: null,
    isLoading: false,
    error: null,
  })
})

describe('useTimelineStore', () => {
  it('initial year is -264', () => {
    expect(useTimelineStore.getState().year).toBe(-264)
  })

  it('setYear updates year', () => {
    useTimelineStore.getState().setYear(100)
    expect(useTimelineStore.getState().year).toBe(100)
  })

  it('setYear to negative value works', () => {
    useTimelineStore.getState().setYear(-400)
    expect(useTimelineStore.getState().year).toBe(-400)
  })

  it('setLoading toggles isLoading to true', () => {
    useTimelineStore.getState().setLoading(true)
    expect(useTimelineStore.getState().isLoading).toBe(true)
  })

  it('setLoading toggles isLoading to false', () => {
    useTimelineStore.setState({ isLoading: true })
    useTimelineStore.getState().setLoading(false)
    expect(useTimelineStore.getState().isLoading).toBe(false)
  })

  it('setError sets error string', () => {
    useTimelineStore.getState().setError('Network error')
    expect(useTimelineStore.getState().error).toBe('Network error')
  })

  it('setError clears error with null', () => {
    useTimelineStore.setState({ error: 'some error' })
    useTimelineStore.getState().setError(null)
    expect(useTimelineStore.getState().error).toBeNull()
  })

  it('setSelectedEntity updates entity', () => {
    const fakeEntity: EntityFeature = {
      type: 'Feature',
      id: 'rome',
      geometry: { type: 'MultiPolygon', coordinates: [] },
      properties: {
        slug: 'roman-empire',
        name: 'Roman Empire',
        type: 'empire',
        color: '#C0392B',
        confidence: 'approximate',
        entity_id: 'abc-123',
      },
    }
    useTimelineStore.getState().setSelectedEntity(fakeEntity)
    expect(useTimelineStore.getState().selectedEntity?.id).toBe('rome')
    expect(useTimelineStore.getState().selectedEntity?.properties.name).toBe('Roman Empire')
  })

  it('setSelectedEntity clears with null', () => {
    const fakeEntity: EntityFeature = {
      type: 'Feature',
      id: 'rome',
      geometry: { type: 'MultiPolygon', coordinates: [] },
      properties: {
        slug: 'roman-empire',
        name: 'Roman Empire',
        type: 'empire',
        color: '#C0392B',
        confidence: 'approximate',
        entity_id: 'abc-123',
      },
    }
    useTimelineStore.setState({ selectedEntity: fakeEntity })
    useTimelineStore.getState().setSelectedEntity(null)
    expect(useTimelineStore.getState().selectedEntity).toBeNull()
  })
})
```

Run (expect failures):
```bash
cd c:/History/apps/web && npm test -- timeline
```

- [ ] Step 2: Create `apps/web/store/timeline.ts`.

```typescript
// apps/web/store/timeline.ts
import { create } from 'zustand'
import type { EntityFeature } from '@/types'

interface TimelineState {
  /** Current calendar year. Negative = BCE, positive = CE. Year 0 does not exist. */
  year: number
  /** The entity the user clicked on, or null if nothing is selected. */
  selectedEntity: EntityFeature | null
  /** True while a fetch for world state is in progress. */
  isLoading: boolean
  /** Error message if the most recent fetch failed, null otherwise. */
  error: string | null
  setYear: (year: number) => void
  setSelectedEntity: (entity: EntityFeature | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useTimelineStore = create<TimelineState>((set) => ({
  year: -264,
  selectedEntity: null,
  isLoading: false,
  error: null,
  setYear: (year) => set({ year }),
  setSelectedEntity: (selectedEntity) => set({ selectedEntity }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}))
```

- [ ] Step 3: Run tests and confirm all PASS.

```bash
cd c:/History/apps/web && npm test -- timeline
```

- [ ] Step 4: Commit.

```bash
cd c:/History && git add apps/web/store apps/web/__tests__/timeline.test.ts && git commit -m "feat: Zustand timeline store with full test coverage"
```

---

## Task 5: GeoJSON Cache (TDD)

**Files:**
- Create: `apps/web/__tests__/cache.test.ts`
- Create: `apps/web/lib/cache.ts`

- [ ] Step 1: Write cache tests FIRST. Run vitest and confirm FAIL.

```typescript
// apps/web/__tests__/cache.test.ts
import { describe, it, expect } from 'vitest'
import { SnapshotCache } from '@/lib/cache'
import type { WorldStateResponse } from '@/types'

const makeData = (year: number): WorldStateResponse => ({
  type: 'FeatureCollection',
  year,
  snapshot_year: year,
  features: [],
})

describe('SnapshotCache', () => {
  it('returns undefined for missing key', () => {
    const c = new SnapshotCache()
    expect(c.get(-264)).toBeUndefined()
  })

  it('returns stored value', () => {
    const c = new SnapshotCache()
    c.set(-264, makeData(-264))
    expect(c.get(-264)?.year).toBe(-264)
  })

  it('has() returns false for missing key', () => {
    const c = new SnapshotCache()
    expect(c.has(-264)).toBe(false)
  })

  it('has() returns true after set', () => {
    const c = new SnapshotCache()
    c.set(100, makeData(100))
    expect(c.has(100)).toBe(true)
  })

  it('size() returns 0 for empty cache', () => {
    const c = new SnapshotCache()
    expect(c.size()).toBe(0)
  })

  it('size() increments with each set', () => {
    const c = new SnapshotCache()
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    expect(c.size()).toBe(2)
  })

  it('evicts oldest when maxSize reached', () => {
    const c = new SnapshotCache(3)
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    c.set(3, makeData(3))
    c.set(4, makeData(4))  // triggers eviction of key 1
    expect(c.size()).toBe(3)
    expect(c.has(1)).toBe(false)
    expect(c.has(4)).toBe(true)
  })

  it('evicts in insertion order (LRU)', () => {
    const c = new SnapshotCache(2)
    c.set(10, makeData(10))
    c.set(20, makeData(20))
    c.set(30, makeData(30))  // evicts 10
    expect(c.has(10)).toBe(false)
    expect(c.has(20)).toBe(true)
    expect(c.has(30)).toBe(true)
  })

  it('overwriting existing key does not grow beyond maxSize', () => {
    const c = new SnapshotCache(2)
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    c.set(1, makeData(1))  // overwrite, should not evict
    expect(c.size()).toBe(2)
    expect(c.has(1)).toBe(true)
    expect(c.has(2)).toBe(true)
  })

  it('default maxSize is 50', () => {
    const c = new SnapshotCache()
    for (let i = 0; i < 50; i++) c.set(i, makeData(i))
    expect(c.size()).toBe(50)
    c.set(50, makeData(50))
    expect(c.size()).toBe(50)
    expect(c.has(0)).toBe(false)
  })
})
```

Run (expect failures):
```bash
cd c:/History/apps/web && npm test -- cache
```

- [ ] Step 2: Create `apps/web/lib/cache.ts`.

```typescript
// apps/web/lib/cache.ts
import type { WorldStateResponse } from '@/types'

/**
 * In-memory LRU cache for WorldStateResponse objects, keyed by year.
 * Evicts the oldest-inserted entry when maxSize is exceeded.
 * JavaScript's Map preserves insertion order, which enables simple FIFO eviction.
 */
export class SnapshotCache {
  private cache = new Map<number, WorldStateResponse>()
  private maxSize: number

  constructor(maxSize = 50) {
    this.maxSize = maxSize
  }

  get(year: number): WorldStateResponse | undefined {
    return this.cache.get(year)
  }

  set(year: number, data: WorldStateResponse): void {
    // If key already exists, delete it first so re-insertion moves it to the end
    if (this.cache.has(year)) {
      this.cache.delete(year)
    } else if (this.cache.size >= this.maxSize) {
      // Evict the oldest entry (first key in insertion order)
      const firstKey = this.cache.keys().next().value as number
      this.cache.delete(firstKey)
    }
    this.cache.set(year, data)
  }

  has(year: number): boolean {
    return this.cache.has(year)
  }

  size(): number {
    return this.cache.size
  }
}

/**
 * Singleton cache instance shared across the app.
 * Import this in useTerritoryLayer and anywhere else that needs the cache.
 */
export const snapshotCache = new SnapshotCache()
```

- [ ] Step 3: Run tests and confirm all PASS.

```bash
cd c:/History/apps/web && npm test -- cache
```

- [ ] Step 4: Run the full test suite to make sure nothing regresses.

```bash
cd c:/History/apps/web && npm test
```

Expected: all tests in `year.test.ts`, `api.test.ts`, `timeline.test.ts`, and `cache.test.ts` pass.

- [ ] Step 5: Commit.

```bash
cd c:/History && git add apps/web/lib/cache.ts apps/web/__tests__/cache.test.ts && git commit -m "feat: LRU snapshot cache with full test coverage"
```

---

## Task 6: MapView Component

**Files:**
- Create: `apps/web/components/map/MapView.tsx`

MapView owns the MapLibre instance lifecycle. It:
- Is a Client Component (`'use client'`)
- Initializes the map exactly ONCE in a `useEffect` with an empty dependency array
- Exposes `{ updateTerritories(data) }` via `forwardRef` + `useImperativeHandle`
- Never subscribes to Zustand; all data comes through the imperative handle
- Accepts `onEntitySelect` as a prop so the parent can wire click → store
- Adds `territories` source with `generateId: true` and two layers on `map.on('load')`

- [ ] Step 1: Create `apps/web/components/map/MapView.tsx` with the full implementation.

```typescript
// apps/web/components/map/MapView.tsx
'use client'

import { useEffect, useRef, forwardRef, useImperativeHandle } from 'react'
import maplibregl, { Map as MaplibreMap, GeoJSONSource } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { WorldStateResponse, EntityFeature, EntityProperties } from '@/types'

const MAP_STYLE =
  process.env.NEXT_PUBLIC_MAP_STYLE ??
  'https://tiles.openfreemap.org/styles/liberty'

const EMPTY_FC: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features: [] }

export interface MapViewHandle {
  updateTerritories: (data: WorldStateResponse) => void
}

export interface MapViewProps {
  onEntitySelect: (entity: EntityFeature | null) => void
}

const MapView = forwardRef<MapViewHandle, MapViewProps>(({ onEntitySelect }, ref) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MaplibreMap | null>(null)
  // Keep onEntitySelect in a ref so the closure inside map.on('load') always sees the latest version
  const onEntitySelectRef = useRef(onEntitySelect)
  useEffect(() => { onEntitySelectRef.current = onEntitySelect }, [onEntitySelect])

  useImperativeHandle(ref, () => ({
    updateTerritories(data: WorldStateResponse) {
      const source = mapRef.current?.getSource('territories') as GeoJSONSource | undefined
      source?.setData(data as unknown as GeoJSON.FeatureCollection)
    },
  }))

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: [20, 30],
      zoom: 2,
      minZoom: 1,
      maxZoom: 10,
    })

    map.on('load', () => {
      // ── Source ──────────────────────────────────────────────────────────
      map.addSource('territories', {
        type: 'geojson',
        data: EMPTY_FC,
        generateId: true,   // assigns numeric IDs needed for setFeatureState hover
      })

      // ── Fill layer ──────────────────────────────────────────────────────
      map.addLayer({
        id: 'territories-fill',
        type: 'fill',
        source: 'territories',
        paint: {
          'fill-color': ['coalesce', ['get', 'color'], '#888888'],
          'fill-opacity': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            0.65,   // hovered
            0.4,    // default
          ],
        },
      })

      // ── Border layer ─────────────────────────────────────────────────────
      map.addLayer({
        id: 'territories-border',
        type: 'line',
        source: 'territories',
        paint: {
          'line-color': ['coalesce', ['get', 'color'], '#888888'],
          'line-width': 1.5,
          'line-opacity': 0.9,
        },
      })

      // ── Hover state ──────────────────────────────────────────────────────
      let hoveredId: number | null = null

      map.on('mousemove', 'territories-fill', (e) => {
        if (!e.features?.length) return
        map.getCanvas().style.cursor = 'pointer'
        if (hoveredId !== null) {
          map.setFeatureState({ source: 'territories', id: hoveredId }, { hover: false })
        }
        hoveredId = e.features[0].id as number
        map.setFeatureState({ source: 'territories', id: hoveredId }, { hover: true })
      })

      map.on('mouseleave', 'territories-fill', () => {
        map.getCanvas().style.cursor = ''
        if (hoveredId !== null) {
          map.setFeatureState({ source: 'territories', id: hoveredId }, { hover: false })
          hoveredId = null
        }
      })

      // ── Click: select entity ─────────────────────────────────────────────
      map.on('click', 'territories-fill', (e) => {
        if (!e.features?.length) return
        const feature = e.features[0]
        const props = feature.properties as EntityProperties
        const entity: EntityFeature = {
          type: 'Feature',
          id: props.slug,
          geometry: feature.geometry as GeoJSON.MultiPolygon,
          properties: props,
        }
        onEntitySelectRef.current(entity)
      })

      // ── Click: deselect when hitting empty area ─────────────────────────
      map.on('click', (e) => {
        const features = map.queryRenderedFeatures(e.point, {
          layers: ['territories-fill'],
        })
        if (!features.length) onEntitySelectRef.current(null)
      })
    })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, []) // empty deps — map is initialized ONCE, never recreated

  return <div ref={containerRef} className="w-full h-full" />
})

MapView.displayName = 'MapView'
export default MapView
```

- [ ] Step 2: Verify the component types check cleanly.

```bash
cd c:/History/apps/web && npx tsc --noEmit
```

Fix any type errors before proceeding.

- [ ] Step 3: Manual smoke test — temporarily add MapView to `app/page.tsx` without SSR guard (to test in isolation), run dev, confirm world map renders at `http://localhost:3000`. Then revert `app/page.tsx` to the default; Task 12 wires everything together properly.

- [ ] Step 4: Commit.

```bash
cd c:/History && git add apps/web/components/map/MapView.tsx && git commit -m "feat: MapView component with MapLibre lifecycle, hover, and click handlers"
```

---

## Task 7: useTerritoryLayer Hook

**Files:**
- Create: `apps/web/components/map/useTerritoryLayer.ts`

This hook is the bridge between the Zustand `year` state and MapView's imperative `updateTerritories` handle. It implements:
1. Watch `year` from Zustand
2. On change: cancel any in-flight request, wait 150ms (debounce)
3. Check cache — if hit, call `updateTerritories` immediately (no loading state)
4. If miss: create new `AbortController`, set `isLoading=true`, fetch, cache result, call `updateTerritories`, set `isLoading=false`
5. After success: fire-and-forget preload of ±2 adjacent snapshot years

- [ ] Step 1: Create `apps/web/components/map/useTerritoryLayer.ts`.

```typescript
// apps/web/components/map/useTerritoryLayer.ts
import { useEffect, useRef, useCallback } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchWorldState } from '@/lib/api'
import { snapshotCache } from '@/lib/cache'
import { snapToSnapshot, SNAPSHOT_YEARS } from '@/lib/year'
import type { MapViewHandle } from './MapView'

/**
 * Silently preload up to 2 adjacent snapshot years in each direction.
 * Failures are swallowed — preloading is best-effort.
 */
async function preloadAdjacent(year: number): Promise<void> {
  const snapped = snapToSnapshot(year)
  const idx = SNAPSHOT_YEARS.indexOf(snapped)
  const candidates = [
    SNAPSHOT_YEARS[idx - 1],
    SNAPSHOT_YEARS[idx + 1],
    SNAPSHOT_YEARS[idx - 2],
    SNAPSHOT_YEARS[idx + 2],
  ].filter((y): y is number => y !== undefined && !snapshotCache.has(y))

  for (const y of candidates) {
    try {
      const data = await fetchWorldState(y)
      snapshotCache.set(y, data)
    } catch {
      // Preload failures are intentionally silent
    }
  }
}

/**
 * Watches the Zustand `year`, debounces 150ms, then fetches + updates the map source.
 * @param mapRef - ref to the MapViewHandle exposing `updateTerritories`
 */
export function useTerritoryLayer(mapRef: React.RefObject<MapViewHandle | null>): void {
  const year = useTimelineStore((s) => s.year)
  const setLoading = useTimelineStore((s) => s.setLoading)
  const setError = useTimelineStore((s) => s.setError)

  const abortRef = useRef<AbortController | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const fetchAndUpdate = useCallback(
    async (yr: number) => {
      // Cache hit — no loading spinner, instant update
      const cached = snapshotCache.get(yr)
      if (cached) {
        mapRef.current?.updateTerritories(cached)
        return
      }

      // Cancel any previous in-flight request
      abortRef.current?.abort()
      abortRef.current = new AbortController()

      setLoading(true)
      setError(null)

      try {
        const data = await fetchWorldState(yr, { signal: abortRef.current.signal })
        snapshotCache.set(yr, data)
        mapRef.current?.updateTerritories(data)
        // Fire-and-forget: preload adjacent years so future slider moves feel instant
        preloadAdjacent(yr)
      } catch (err) {
        // AbortError is expected when the slider moves again before fetch completes
        if ((err as Error).name !== 'AbortError') {
          setError('Failed to load world state. Is the API running?')
        }
      } finally {
        setLoading(false)
      }
    },
    [mapRef, setLoading, setError]
  )

  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchAndUpdate(year)
    }, 150)

    return () => clearTimeout(debounceRef.current)
  }, [year, fetchAndUpdate])
}
```

- [ ] Step 2: Verify TypeScript types.

```bash
cd c:/History/apps/web && npx tsc --noEmit
```

- [ ] Step 3: Manual verification (requires Docker stack running).

Start the backend: `make dev` from repo root (or `docker compose up`).
Start Next.js: `cd apps/web && npm run dev`.

After wiring in Task 12, confirm territory polygons appear for year -264 at `http://localhost:3000`.

- [ ] Step 4: Commit.

```bash
cd c:/History && git add apps/web/components/map/useTerritoryLayer.ts && git commit -m "feat: useTerritoryLayer hook with debounce, abort, cache, and adjacent preload"
```

---

## Task 8: Timeline Slider

**Files:**
- Create: `apps/web/components/timeline/TimelineSlider.tsx`

- [ ] Step 1: Create `apps/web/components/timeline/TimelineSlider.tsx`.

The slider uses a 0–999 integer range input and maps values through `sliderToYear` / `yearToSlider`. The display label is rendered above the track. A gradient overlay sits behind the slider so it is readable over the map.

```typescript
// apps/web/components/timeline/TimelineSlider.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'
import { yearToDisplay, sliderToYear, yearToSlider } from '@/lib/year'

export function TimelineSlider() {
  const year = useTimelineStore((s) => s.year)
  const setYear = useTimelineStore((s) => s.setYear)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setYear(sliderToYear(Number(e.target.value)))
  }

  return (
    <div className="absolute bottom-0 left-0 right-0 px-8 pb-8 pt-12 bg-gradient-to-t from-black/85 to-transparent pointer-events-none">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        {/* Year label */}
        <div className="text-center text-white text-3xl font-bold mb-4 tracking-widest drop-shadow-lg">
          {yearToDisplay(year)}
        </div>

        {/* Range input */}
        <input
          type="range"
          min={0}
          max={999}
          step={1}
          value={yearToSlider(year)}
          onChange={handleChange}
          aria-label="Timeline year"
          className="w-full h-1.5 cursor-pointer accent-amber-400 rounded-full"
        />

        {/* Axis labels */}
        <div className="flex justify-between text-white/50 text-xs mt-2 font-mono select-none">
          <span>500 BCE</span>
          <span>1 BCE / 1 CE</span>
          <span>500 CE</span>
        </div>
      </div>
    </div>
  )
}
```

- [ ] Step 2: Verify TypeScript and run all tests.

```bash
cd c:/History/apps/web && npx tsc --noEmit && npm test
```

- [ ] Step 3: Commit.

```bash
cd c:/History && git add apps/web/components/timeline && git commit -m "feat: TimelineSlider with year-0-skipping math and gradient overlay"
```

---

## Task 9: Entity Panel

**Files:**
- Create: `apps/web/components/entity/EntityPanel.tsx`

- [ ] Step 1: Create `apps/web/components/entity/EntityPanel.tsx`.

The panel is absolutely positioned top-right. It reads `selectedEntity` from Zustand and renders null if nothing is selected. A close button calls `setSelectedEntity(null)`.

```typescript
// apps/web/components/entity/EntityPanel.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'

export function EntityPanel() {
  const entity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)

  if (!entity) return null

  const { name, type, color, confidence } = entity.properties

  return (
    <div
      className="absolute top-4 right-4 w-72 bg-black/80 backdrop-blur-md text-white rounded-xl p-5 border border-white/10 shadow-2xl"
      role="complementary"
      aria-label={`Entity: ${name}`}
    >
      {/* Close button */}
      <button
        onClick={() => setSelectedEntity(null)}
        className="absolute top-3 right-4 text-white/40 hover:text-white text-xl leading-none transition-colors"
        aria-label="Close entity panel"
      >
        ×
      </button>

      {/* Title row: color swatch + name */}
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-5 h-5 rounded flex-shrink-0 border border-white/20"
          style={{ backgroundColor: color }}
          aria-hidden="true"
        />
        <h2 className="font-bold text-lg leading-tight pr-4">{name}</h2>
      </div>

      {/* Details */}
      <dl className="space-y-1 text-sm">
        <div className="flex gap-2">
          <dt className="text-white/50 w-20 flex-shrink-0">Type</dt>
          <dd className="text-white/80 capitalize">{type}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="text-white/50 w-20 flex-shrink-0">Data</dt>
          <dd className="text-white/80 capitalize">{confidence}</dd>
        </div>
      </dl>
    </div>
  )
}
```

- [ ] Step 2: Verify TypeScript and run all tests.

```bash
cd c:/History/apps/web && npx tsc --noEmit && npm test
```

- [ ] Step 3: Commit.

```bash
cd c:/History && git add apps/web/components/entity && git commit -m "feat: EntityPanel showing name, color, type, confidence"
```

---

## Task 10: Loading + Error Overlay

**Files:**
- Create: `apps/web/components/ui/LoadingOverlay.tsx`

- [ ] Step 1: Create `apps/web/components/ui/LoadingOverlay.tsx`.

The overlay is centered at the top of the screen. It shows a spinner pill when `isLoading=true`, an error pill when `error` is non-null and not loading. Both have `pointer-events-none` so they do not block map interaction.

```typescript
// apps/web/components/ui/LoadingOverlay.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'

export function LoadingOverlay() {
  const isLoading = useTimelineStore((s) => s.isLoading)
  const error = useTimelineStore((s) => s.error)

  if (!isLoading && !error) return null

  return (
    <div
      className="absolute top-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      {isLoading && (
        <div className="bg-black/70 backdrop-blur-sm text-white/80 text-xs px-3 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
          <div
            className="w-3 h-3 border border-white/40 border-t-white rounded-full animate-spin"
            aria-hidden="true"
          />
          Loading...
        </div>
      )}
      {error && !isLoading && (
        <div className="bg-red-900/80 backdrop-blur-sm text-red-200 text-xs px-3 py-1.5 rounded-full shadow-lg">
          {error}
        </div>
      )}
    </div>
  )
}
```

- [ ] Step 2: Verify TypeScript and run all tests.

```bash
cd c:/History/apps/web && npx tsc --noEmit && npm test
```

- [ ] Step 3: Commit.

```bash
cd c:/History && git add apps/web/components/ui && git commit -m "feat: LoadingOverlay with spinner pill and error banner"
```

---

## Task 11: MapContainer Assembly + Full Page Layout

**Files:**
- Create: `apps/web/components/map/MapContainer.tsx`
- Modify: `apps/web/app/page.tsx`
- Verify: `apps/web/app/layout.tsx` (should already be correct from Task 1)

This task wires all pieces together. `MapContainer` is a Client Component that:
1. Creates the `mapRef` and passes it to `useTerritoryLayer` (hook) and `MapView` (via forwardRef)
2. Loads `MapView` via `dynamic(..., { ssr: false })` to avoid SSR canvas errors
3. Renders all overlay components: `TimelineSlider`, `EntityPanel`, `LoadingOverlay`

- [ ] Step 1: Create `apps/web/components/map/MapContainer.tsx`.

```typescript
// apps/web/components/map/MapContainer.tsx
'use client'

import dynamic from 'next/dynamic'
import { useRef } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { LoadingOverlay } from '@/components/ui/LoadingOverlay'
import { useTerritoryLayer } from './useTerritoryLayer'
import type { MapViewHandle } from './MapView'

// SSR must be disabled: MapLibre uses browser canvas APIs not available in Node.
const MapView = dynamic(() => import('./MapView'), { ssr: false })

export function MapContainer() {
  const mapRef = useRef<MapViewHandle | null>(null)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)

  // Hook: watches year → debounce → fetch → updateTerritories
  useTerritoryLayer(mapRef)

  return (
    <div className="relative w-full h-full bg-zinc-900">
      {/* Map fills the entire container */}
      <MapView ref={mapRef} onEntitySelect={setSelectedEntity} />

      {/* Overlays — rendered on top of the map */}
      <LoadingOverlay />
      <EntityPanel />
      <TimelineSlider />
    </div>
  )
}
```

- [ ] Step 2: Replace `apps/web/app/page.tsx` with:

```typescript
// apps/web/app/page.tsx
import { MapContainer } from '@/components/map/MapContainer'

export default function Home() {
  return <MapContainer />
}
```

- [ ] Step 3: Confirm `apps/web/app/layout.tsx` matches the Task 1 version (should already be correct):

```typescript
// apps/web/app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'History Platform',
  description: 'Interactive temporal world map',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden bg-zinc-900">{children}</body>
    </html>
  )
}
```

- [ ] Step 4: Run TypeScript check and all tests.

```bash
cd c:/History/apps/web && npx tsc --noEmit && npm test
```

All tests must PASS; zero TypeScript errors.

- [ ] Step 5: Manual integration smoke test (API not required for map tiles).

```bash
cd c:/History/apps/web && npm run dev
```

Navigate to `http://localhost:3000`. Verify:
- Fullscreen world map renders (OpenFreeMap tiles)
- Slider is visible at bottom with "264 BCE" label
- Loading spinner appears briefly then disappears (or shows error if API is not running — that is acceptable at this stage)

- [ ] Step 6: Commit.

```bash
cd c:/History && git add apps/web/components/map/MapContainer.tsx apps/web/app/page.tsx && git commit -m "feat: MapContainer assembly — full layout wired with all overlays"
```

---

## Task 12: End-to-End Manual Verification

**Files:**
- No new files. This task validates the full system.

This is the first task that requires the Docker backend stack to be running.

- [ ] Step 1: Start the backend stack from the repo root.

```bash
cd c:/History && make dev-build
# If make is not available:
# docker compose up --build -d
```

Wait for API to be healthy:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","env":"development"}
```

- [ ] Step 2: Start the Next.js frontend.

```bash
cd c:/History/apps/web && npm run dev
```

- [ ] Step 3: Run through the acceptance checklist.

Navigate to `http://localhost:3000` and verify each item:

1. - [ ] Fullscreen world map renders (OpenFreeMap tiles load)
2. - [ ] Year label shows "264 BCE" on initial load
3. - [ ] Territory polygons visible (Rome, Han Dynasty, etc.) — colored regions on the map
4. - [ ] Drag slider left toward 0 (← 500 BCE direction) → territory borders update
5. - [ ] Drag slider right past center (1 CE direction) → territory borders update
6. - [ ] Hover over a territory polygon → opacity increases (hover state active)
7. - [ ] Mouse leaves territory → opacity returns to normal
8. - [ ] Click a territory → EntityPanel appears top-right with name, color swatch, type, confidence
9. - [ ] Click empty ocean/land area → EntityPanel closes
10. - [ ] Drag slider rapidly left and right for 3 seconds → only 1 request fires per 150ms; no visual glitches; no stale data overlaid
11. - [ ] Navigate to the same year a second time (stop slider, move away, move back) → no network request (instantaneous update from cache; verify in browser DevTools Network tab)
12. - [ ] Loading spinner appears during initial load and disappears when data arrives
13. - [ ] Error message appears if API is stopped (`docker compose stop api`); resolves when API is restarted

- [ ] Step 4: Run the full test suite.

```bash
cd c:/History/apps/web && npm test
```

Expected output: all tests PASS, 0 failures.

- [ ] Step 5: Update root `README.md` — add frontend to the services table and document how to start it.

Open `README.md` and add to the services section:

```markdown
| Frontend | http://localhost:3000 | `cd apps/web && npm run dev` |
```

Also add a section if one does not exist:

```markdown
## Running the Frontend

```bash
cd apps/web
npm install   # first time only
npm run dev
```

Navigate to http://localhost:3000. The backend API must be running for territory data to load.
```

- [ ] Step 6: Commit all.

```bash
cd c:/History && git add apps/web README.md && git commit -m "feat: milestone 1 complete — interactive temporal map frontend"
```

---

## Task 13: Snapshot Preloading (Enhancement)

**Files:**
- Modify: `apps/web/components/map/useTerritoryLayer.ts`

> NOTE: The `preloadAdjacent` function was already included in Task 7's implementation of `useTerritoryLayer.ts`. This task confirms it is correct and tests it manually. No code changes are required unless the function was omitted.

- [ ] Step 1: Verify `preloadAdjacent` is present in `useTerritoryLayer.ts`. It should already contain:

```typescript
async function preloadAdjacent(year: number): Promise<void> {
  const snapped = snapToSnapshot(year)
  const idx = SNAPSHOT_YEARS.indexOf(snapped)
  const candidates = [
    SNAPSHOT_YEARS[idx - 1],
    SNAPSHOT_YEARS[idx + 1],
    SNAPSHOT_YEARS[idx - 2],
    SNAPSHOT_YEARS[idx + 2],
  ].filter((y): y is number => y !== undefined && !snapshotCache.has(y))

  for (const y of candidates) {
    try {
      const data = await fetchWorldState(y)
      snapshotCache.set(y, data)
    } catch {
      // Preload failures are intentionally silent
    }
  }
}
```

And in `fetchAndUpdate`, after `snapshotCache.set(yr, data)`:
```typescript
snapshotCache.set(yr, data)
mapRef.current?.updateTerritories(data)
preloadAdjacent(yr)   // fire-and-forget
```

- [ ] Step 2: If `preloadAdjacent` is missing, add it now following the code in Task 7 Step 1. Run TypeScript check.

```bash
cd c:/History/apps/web && npx tsc --noEmit
```

- [ ] Step 3: Manual verification of preload in browser.

1. Open DevTools → Network tab, filter by `world/state`
2. Navigate to `http://localhost:3000`, wait for initial load at year -264
3. Observe: after the first fetch completes, 2–4 background requests fire for adjacent snapshot years (-300, -250, -325, -225)
4. Drag the slider to -275 → should be an instant cache hit (no new network request)

- [ ] Step 4: Commit if any changes were made.

```bash
cd c:/History && git add apps/web/components/map/useTerritoryLayer.ts && git commit -m "feat: verify adjacent snapshot preloading in useTerritoryLayer"
```

---

## Task 14: Final Polish + Production Build Check

**Files:**
- No new source files. This task ensures the build is clean and all quality gates pass.

- [ ] Step 1: Run the full test suite and confirm 100% pass.

```bash
cd c:/History/apps/web && npm test
```

- [ ] Step 2: Run TypeScript strict check with no errors.

```bash
cd c:/History/apps/web && npx tsc --noEmit
```

- [ ] Step 3: Run ESLint.

```bash
cd c:/History/apps/web && npm run lint
```

Fix any warnings flagged as errors. Common issues:
- `react-hooks/exhaustive-deps` — ensure all hook deps are listed
- `@typescript-eslint/no-explicit-any` — replace `any` with specific types

- [ ] Step 4: Run a production build to catch any build-time errors (e.g., SSR issues, missing imports).

```bash
cd c:/History/apps/web && npm run build
```

Expected: build completes successfully. The `MapView` dynamic import with `ssr: false` prevents MapLibre canvas errors at build time.

- [ ] Step 5: Review the complete acceptance criteria one final time.

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Map renders fullscreen, no white border | verify |
| 2 | Initial year: 264 BCE | verify |
| 3 | Territory polygons colored by entity | verify |
| 4 | Slider drag updates map, no flicker | verify |
| 5 | Year label updates in sync with slider | verify |
| 6 | Hover → opacity increase | verify |
| 7 | Click territory → EntityPanel | verify |
| 8 | Click empty → EntityPanel closes | verify |
| 9 | Fast drag: no race conditions | verify |
| 10 | Cache hit: instant, no network | verify |
| 11 | Loading indicator during fetch | verify |
| 12 | Error banner if API unreachable | verify |
| 13 | Map never reinitializes on year change | verify (check mapRef is stable) |
| 14 | All unit tests pass | verify |
| 15 | TypeScript strict — zero errors | verify |

- [ ] Step 6: Final commit.

```bash
cd c:/History && git add -A && git commit -m "feat: milestone 1 final — production build clean, all acceptance criteria met"
```

---

## Architectural Notes for Implementers

### Why `onEntitySelectRef` in MapView

The click handler is registered inside `map.on('load', ...)` which runs once. If `onEntitySelect` were captured directly in the closure, it would become stale after re-renders. The ref pattern (`onEntitySelectRef`) ensures the latest version of the callback is always called without requiring the map to be recreated.

### Why `dynamic(..., { ssr: false })` only in MapContainer

MapView imports `maplibre-gl/dist/maplibre-gl.css` and uses `document` / `canvas`. These do not exist during Next.js server-side rendering. The `dynamic` import boundary in MapContainer is the correct and minimal SSR guard — MapView itself does not need to be modified.

### Year 0 skip — where it matters

The skip from -1 to 1 must be handled in exactly two places:
- `sliderToYear` / `yearToSlider` in `lib/year.ts` — maps the 0–999 slider range
- `SNAPSHOT_YEARS` in `lib/year.ts` — the static list jumps from -25 to 25

Everywhere else in the codebase, year values are already valid (negative BCE or positive CE). Do not add year-0 guards elsewhere.

### AbortController vs debounce — why both

Debounce (150ms) reduces how often fetches start. AbortController cancels fetches that are already in flight when a new year is selected while the previous fetch has not completed. The two work together: debounce prevents over-fetching during rapid slider movement; abort handles the case where a slow network response arrives after the user has moved on.

### Cache eviction strategy

The cache uses JavaScript `Map` which preserves insertion order. When `maxSize` is reached, the oldest-inserted key (first in iteration order) is evicted. This is FIFO, not true LRU (access order is not tracked). For 50 entries covering a domain of 40 snapshot years this is more than sufficient — the entire snapshot space fits in the cache with room to spare.
