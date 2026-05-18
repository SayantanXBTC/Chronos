// apps/web/components/map/useTerritoryLayer.ts
import { useEffect, useRef, useCallback } from 'react'
import type { RefObject } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchWorldState } from '@/lib/api'
import { snapshotCache } from '@/lib/cache'
import { snapToSnapshot, SNAPSHOT_YEARS } from '@/lib/year'
import type { MapViewHandle } from './MapView'

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

export function useTerritoryLayer(mapRef: RefObject<MapViewHandle | null>): void {
  const year = useTimelineStore((s) => s.year)
  const viewport = useTimelineStore((s) => s.viewport)
  const setLoading = useTimelineStore((s) => s.setLoading)
  const setError = useTimelineStore((s) => s.setError)

  const abortRef = useRef<AbortController | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const fetchAndUpdate = useCallback(
    async (yr: number, vp: typeof viewport) => {
      // Viewport-aware cache: bypass cache when viewport changes (not world bbox)
      const isWorldBbox = vp.minX <= -180 && vp.minY <= -90 && vp.maxX >= 180 && vp.maxY >= 90
      const cached = isWorldBbox ? snapshotCache.get(yr) : null
      if (cached) {
        mapRef.current?.updateTerritories(cached)
        useTimelineStore.getState().setCurrentEntities(cached.features)
        return
      }

      abortRef.current?.abort()
      abortRef.current = new AbortController()

      setLoading(true)
      setError(null)

      const controller = abortRef.current
      try {
        const data = await fetchWorldState(yr, {
          signal: controller.signal,
          zoom: vp.zoom,
          minX: vp.minX,
          minY: vp.minY,
          maxX: vp.maxX,
          maxY: vp.maxY,
        })
        if (controller.signal.aborted) return
        if (isWorldBbox) snapshotCache.set(yr, data)
        mapRef.current?.updateTerritories(data)
        useTimelineStore.getState().setCurrentEntities(data.features)
        if (isWorldBbox) preloadAdjacent(yr)
      } catch (err) {
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
      fetchAndUpdate(year, viewport)
    }, 150)

    return () => clearTimeout(debounceRef.current)
  }, [year, viewport, fetchAndUpdate])
}
