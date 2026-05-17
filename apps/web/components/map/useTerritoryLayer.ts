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
  const setLoading = useTimelineStore((s) => s.setLoading)
  const setError = useTimelineStore((s) => s.setError)

  const abortRef = useRef<AbortController | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const fetchAndUpdate = useCallback(
    async (yr: number) => {
      const cached = snapshotCache.get(yr)
      if (cached) {
        mapRef.current?.updateTerritories(cached)
        return
      }

      abortRef.current?.abort()
      abortRef.current = new AbortController()

      setLoading(true)
      setError(null)

      try {
        const data = await fetchWorldState(yr, { signal: abortRef.current.signal })
        snapshotCache.set(yr, data)
        mapRef.current?.updateTerritories(data)
        preloadAdjacent(yr)
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
      fetchAndUpdate(year)
    }, 150)

    return () => clearTimeout(debounceRef.current)
  }, [year, fetchAndUpdate])
}
