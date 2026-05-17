// apps/web/types/index.ts
import type { Feature, MultiPolygon } from 'geojson'

export interface EntityProperties {
  entity_id: string
  slug: string
  name: string
  type: string
  color: string
  confidence: string
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
