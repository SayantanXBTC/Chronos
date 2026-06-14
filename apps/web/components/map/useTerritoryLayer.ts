import { useEffect, useRef, useCallback } from 'react'
import type { RefObject } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchWorldState } from '@/lib/api'
import { snapshotCache } from '@/lib/cache'
import { snapToSnapshot, SNAPSHOT_YEARS } from '@/lib/year'
import type { MapViewHandle } from './MapView'
import { AAA_POLISH } from '@/lib/flags'

async function preloadAdjacent(year: number): Promise<void> {
  const snapped = snapToSnapshot(year)
  const idx = SNAPSHOT_YEARS.indexOf(snapped)
  const candidates = [
    SNAPSHOT_YEARS[idx - 1],
    SNAPSHOT_YEARS[idx + 1],
    SNAPSHOT_YEARS[idx - 2],
    SNAPSHOT_YEARS[idx + 2],
    SNAPSHOT_YEARS[idx - 3],
    SNAPSHOT_YEARS[idx + 3],
    SNAPSHOT_YEARS[idx - 4],
    SNAPSHOT_YEARS[idx + 4],
    SNAPSHOT_YEARS[idx - 5],
    SNAPSHOT_YEARS[idx + 5],
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
  // Delay the loading indicator to avoid flashes for cached/fast loads
  const loadingTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const fetchAndUpdate = useCallback(
    async (yr: number, vp: typeof viewport) => {
      const isWorldBbox = vp.minX <= -180 && vp.minY <= -90 && vp.maxX >= 180 && vp.maxY >= 90
      const cached = isWorldBbox ? snapshotCache.get(yr) : null
      if (cached) {
        mapRef.current?.updateTerritories(cached)
        useTimelineStore.getState().setCurrentEntities(cached.features)
        return
      }

      abortRef.current?.abort()
      abortRef.current = new AbortController()

      // Only show loading indicator after 500ms — hidden for fast/cached loads
      clearTimeout(loadingTimerRef.current)
      loadingTimerRef.current = setTimeout(() => setLoading(true), 500)

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
        clearTimeout(loadingTimerRef.current)
        setLoading(false)
      }
    },
    [mapRef, setLoading, setError]
  )

  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchAndUpdate(year, viewport)
    }, 50)  // Reduced from 150ms to 50ms for snappier response

    return () => {
      clearTimeout(debounceRef.current)
      clearTimeout(loadingTimerRef.current)
      abortRef.current?.abort()
    }
  }, [year, viewport, fetchAndUpdate])

  const selectedSlug = useTimelineStore((s) => s.selectedEntity?.properties.slug ?? null)
  useEffect(() => {
    if (!AAA_POLISH || !selectedSlug) return
    let raf = 0
    const start = performance.now()
    const tick = (t: number) => {
      const elapsed = t - start
      const opacity = 0.78 + 0.07 * Math.sin(elapsed / 600)
      mapRef.current?.setShimmerOpacity(selectedSlug, opacity)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [mapRef, selectedSlug])
}
