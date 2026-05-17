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
  const pendingDataRef = useRef<WorldStateResponse | null>(null)
  // Ref mirror: keeps onEntitySelect fresh inside the one-time map.on('load') closure
  const onEntitySelectRef = useRef(onEntitySelect)
  useEffect(() => { onEntitySelectRef.current = onEntitySelect }, [onEntitySelect])

  useImperativeHandle(ref, () => ({
    updateTerritories(data: WorldStateResponse) {
      const source = mapRef.current?.getSource('territories') as GeoJSONSource | undefined
      if (source) {
        source.setData(data as unknown as GeoJSON.GeoJSON)
        pendingDataRef.current = null
      } else {
        pendingDataRef.current = data
      }
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
      map.addSource('territories', {
        type: 'geojson',
        data: (pendingDataRef.current as unknown as GeoJSON.GeoJSON) ?? EMPTY_FC,
        generateId: true,
      })
      pendingDataRef.current = null

      map.addLayer({
        id: 'territories-fill',
        type: 'fill',
        source: 'territories',
        paint: {
          'fill-color': ['coalesce', ['get', 'color'], '#888888'],
          'fill-opacity': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            0.65,
            0.4,
          ],
        },
      })

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
  }, [])

  return <div ref={containerRef} className="w-full h-full" />
})

MapView.displayName = 'MapView'
export default MapView
