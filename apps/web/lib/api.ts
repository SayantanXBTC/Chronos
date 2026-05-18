// apps/web/lib/api.ts
import type { WorldStateResponse, PlaceNamesResponse, RiversResponse, SourceItem, EntityDetail } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface ViewportOptions {
  minX?: number
  minY?: number
  maxX?: number
  maxY?: number
  zoom?: number
}

interface FetchOptions extends ViewportOptions {
  signal?: AbortSignal
}

export async function fetchWorldState(
  year: number,
  options?: FetchOptions
): Promise<WorldStateResponse> {
  const params = new URLSearchParams({
    year: String(year),
    zoom: String(options?.zoom ?? 4),
    min_x: String(options?.minX ?? -180),
    min_y: String(options?.minY ?? -90),
    max_x: String(options?.maxX ?? 180),
    max_y: String(options?.maxY ?? 90),
  })
  const res = await fetch(`${API_BASE}/api/v1/world/state?${params}`, {
    signal: options?.signal,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json() as Promise<WorldStateResponse>
}

export async function fetchSnapshots(): Promise<number[]> {
  const res = await fetch(`${API_BASE}/api/v1/world/snapshots`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  const data = await res.json()
  return (data as { snapshots: number[] }).snapshots
}

export async function fetchPlaceNames(
  year: number,
  options?: FetchOptions
): Promise<PlaceNamesResponse> {
  const params = new URLSearchParams({
    year: String(year),
    zoom: String(options?.zoom ?? 4),
    min_x: String(options?.minX ?? -180),
    min_y: String(options?.minY ?? -90),
    max_x: String(options?.maxX ?? 180),
    max_y: String(options?.maxY ?? 90),
  })
  const res = await fetch(`${API_BASE}/api/v1/place-names?${params}`, {
    signal: options?.signal,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json() as Promise<PlaceNamesResponse>
}

export async function fetchRivers(): Promise<RiversResponse> {
  const res = await fetch(`${API_BASE}/api/v1/rivers`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json() as Promise<RiversResponse>
}

export async function fetchSources(): Promise<SourceItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/sources`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json() as Promise<SourceItem[]>
}

export async function fetchEntityDetail(slug: string): Promise<EntityDetail | null> {
  const resp = await fetch(`${API_BASE}/api/v1/entities/${slug}`)
  if (resp.status === 404) return null
  if (!resp.ok) throw new Error(`fetchEntityDetail: ${resp.status}`)
  return resp.json() as Promise<EntityDetail>
}
