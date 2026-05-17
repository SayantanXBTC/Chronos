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

  useTerritoryLayer(mapRef)

  return (
    <div className="relative w-full h-full bg-zinc-900">
      <MapView ref={mapRef} onEntitySelect={setSelectedEntity} />
      <LoadingOverlay />
      <EntityPanel />
      <TimelineSlider />
    </div>
  )
}
