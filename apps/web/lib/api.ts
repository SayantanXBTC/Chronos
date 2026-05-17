// apps/web/lib/api.ts
import type { WorldStateResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function fetchWorldState(
  year: number,
  options?: { signal?: AbortSignal }
): Promise<WorldStateResponse> {
  const params = new URLSearchParams({
    year: String(year),
    zoom: '4',
    min_x: '-180',
    min_y: '-90',
    max_x: '180',
    max_y: '90',
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
