// apps/web/components/map/usePlaceNamesLayer.ts
import { useEffect, useRef } from 'react'
import type { RefObject } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchPlaceNames } from '@/lib/api'
import type { MapViewHandle } from './MapView'

export function usePlaceNamesLayer(mapRef: RefObject<MapViewHandle | null>): void {
  const year = useTimelineStore((s) => s.year)
  const viewport = useTimelineStore((s) => s.viewport)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      abortRef.current?.abort()
      abortRef.current = new AbortController()

      fetchPlaceNames(year, {
        signal: abortRef.current.signal,
        zoom: viewport.zoom,
        minX: viewport.minX,
        minY: viewport.minY,
        maxX: viewport.maxX,
        maxY: viewport.maxY,
      })
        .then((data) => {
          mapRef.current?.updatePlaceNames(data)
        })
        .catch((err: Error) => {
          if (err.name !== 'AbortError') {
            // Place names are cosmetic — silent failure acceptable
          }
        })
    }, 150)

    return () => clearTimeout(debounceRef.current)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [year, viewport])
}
