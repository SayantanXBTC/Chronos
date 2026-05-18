// apps/web/types/index.ts
import type { Feature, MultiPolygon, LineString, Point } from 'geojson'

export interface EntityProperties {
  entity_id: string
  slug: string
  name: string
  type: string
  color: string
  confidence: string
  confidence_type: string
  source_name: string | null
  importance: number
}

export type EntityFeature = Feature<MultiPolygon, EntityProperties>

export interface WorldStateResponse {
  type: 'FeatureCollection'
  year: number
  snapshot_year: number
  features: EntityFeature[]
}

export interface SnapshotsResponse {
  snapshots: number[]
}

export interface PlaceNameProperties {
  name: string
  name_modern: string | null
  type: string
  importance: number
  label_priority: number
}

export type PlaceNameFeature = Feature<Point, PlaceNameProperties>

export interface PlaceNamesResponse {
  type: 'FeatureCollection'
  features: PlaceNameFeature[]
}

export interface RiverProperties {
  name: string
  name_alt: string | null
  importance: number
}

export type RiverFeature = Feature<LineString, RiverProperties>

export interface RiversResponse {
  type: 'FeatureCollection'
  features: RiverFeature[]
}

export interface SourceItem {
  id: string
  name: string
  url: string | null
  license: string | null
}
