// apps/web/components/map/MapContainer.tsx
'use client'

import dynamic from 'next/dynamic'
import { useRef, useCallback } from 'react'
import { AnimatePresence } from 'motion/react'
import { useTimelineStore, type Viewport } from '@/store/timeline'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { LoadingOverlay } from '@/components/ui/LoadingOverlay'
import { AttributionFooter } from '@/components/ui/AttributionFooter'
import { SearchBar } from '@/components/ui/SearchBar'
import { MetricsOverlay } from '@/components/ui/MetricsOverlay'
import { TemporalOverlay } from '@/components/ui/TemporalOverlay'
import { EraAtmosphere } from '@/components/ui/EraAtmosphere'
import { AtmosphericOverlay } from '@/components/ui/AtmosphericOverlay'
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
  const year = useTimelineStore((s) => s.year)
  const handleViewportChange = useCallback((v: Viewport) => setViewport(v), [setViewport])

  useTerritoryLayer(mapRef)
  useRiversLayer(mapRef)
  usePlaceNamesLayer(mapRef)

  return (
    <div className="relative w-full h-full bg-zinc-900">
      <EraAtmosphere />
      <MapView
        ref={mapRef}
        onEntitySelect={setSelectedEntity}
        onViewportChange={handleViewportChange}
        selectedSlug={selectedSlug}
        year={year}
      />
      <AtmosphericOverlay />
      <LoadingOverlay />
      <SearchBar />
      <TemporalOverlay />
      <AnimatePresence>
        {selectedSlug && <EntityPanel key={selectedSlug} />}
      </AnimatePresence>
      <TimelineSlider />
      <AttributionFooter />
      <MetricsOverlay />
    </div>
  )
}
