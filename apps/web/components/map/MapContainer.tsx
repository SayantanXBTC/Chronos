// apps/web/components/map/MapContainer.tsx
'use client'

import dynamic from 'next/dynamic'
import { useRef, useCallback } from 'react'
import { useTimelineStore, type Viewport } from '@/store/timeline'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { LoadingOverlay } from '@/components/ui/LoadingOverlay'
import { AttributionFooter } from '@/components/ui/AttributionFooter'
import { SearchBar } from '@/components/ui/SearchBar'
import { TemporalOverlay } from '@/components/ui/TemporalOverlay'
import { EraAtmosphere } from '@/components/ui/EraAtmosphere'
import { WhatElseExisted } from '@/components/ui/WhatElseExisted'
import { DiscoveryEngine } from '@/components/ui/DiscoveryEngine'
import { useTerritoryLayer } from './useTerritoryLayer'
import { useRiversLayer } from './useRiversLayer'
import { usePlaceNamesLayer } from './usePlaceNamesLayer'
import type { MapViewHandle } from './MapView'
import { useTimeLens } from '@/hooks/useTimeLens'
import { yearToDisplay } from '@/lib/year'
import { AnimatePresence, motion } from 'motion/react'

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
  const { previewYear } = useTimeLens(mapRef)

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
      <LoadingOverlay />
      <SearchBar />
      <TemporalOverlay />
      <EntityPanel />
      {/* What Else Existed — bottom-right signature overlay */}
      <div className="pointer-events-auto">
        <WhatElseExisted />
      </div>
      {/* Discovery Engine — center-bottom invitation cards */}
      <div className="pointer-events-auto">
        <DiscoveryEngine />
      </div>
      <TimelineSlider />
      <AttributionFooter />
      {/* Time lens year label — appears when Alt is held */}
      <AnimatePresence>
        {previewYear !== null && (
          <motion.div
            key="time-lens-label"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
            className="absolute top-4 left-1/2 -translate-x-1/2 z-30 pointer-events-none select-none"
          >
            <div
              className="px-3 py-1.5 rounded-lg backdrop-blur-md border font-cinzel text-[10px] tracking-widest"
              style={{
                background: 'rgba(16,10,4,0.88)',
                borderColor: 'rgba(190,148,68,0.35)',
                color: 'rgba(255,210,100,0.85)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.60)',
              }}
            >
              {(() => {
                try { return `⟳ +50 years · ${yearToDisplay(previewYear)}` }
                catch { return `⟳ +50 years · ${previewYear}` }
              })()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
