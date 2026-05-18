// apps/web/components/map/useRiversLayer.ts
import { useEffect } from 'react'
import type { RefObject } from 'react'
import { fetchRivers } from '@/lib/api'
import type { MapViewHandle } from './MapView'

export function useRiversLayer(mapRef: RefObject<MapViewHandle | null>): void {
  useEffect(() => {
    fetchRivers()
      .then((data) => {
        mapRef.current?.updateRivers(data)
      })
      .catch(() => {
        // Rivers are cosmetic — silent failure acceptable
      })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
