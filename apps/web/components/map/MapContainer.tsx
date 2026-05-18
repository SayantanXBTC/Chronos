// apps/web/components/map/MapContainer.tsx
'use client'

import dynamic from 'next/dynamic'
import { useRef, useCallback } from 'react'
import { useTimelineStore, type Viewport } from '@/store/timeline'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { LoadingOverlay } from '@/components/ui/LoadingOverlay'
import { AttributionFooter } from '@/components/ui/AttributionFooter'
import { useTerritoryLayer } from './useTerritoryLayer'
import { useRiversLayer } from './useRiversLayer'
import { usePlaceNamesLayer } from './usePlaceNamesLayer'
import type { MapViewHandle } from './MapView'

// SSR must be disabled: MapLibre uses browser canvas APIs not available in Node.
const MapView = dynamic(() => import('./MapView'), { ssr: false })

export function MapContainer() {
  const mapRef = useRef<MapViewHandle | null>(null)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const setViewport = useTimelineStore((s) => s.setViewport)
  const selectedSlug = useTimelineStore((s) => s.selectedEntity?.properties.slug ?? null)
  const handleViewportChange = useCallback((v: Viewport) => setViewport(v), [setViewport])

  useTerritoryLayer(mapRef)
  useRiversLayer(mapRef)
  usePlaceNamesLayer(mapRef)

  return (
    <div className="relative w-full h-full bg-zinc-900">
      <MapView
        ref={mapRef}
        onEntitySelect={setSelectedEntity}
        onViewportChange={handleViewportChange}
        selectedSlug={selectedSlug}
      />
      <LoadingOverlay />
      <EntityPanel />
      <TimelineSlider />
      <AttributionFooter />
    </div>
  )
}
