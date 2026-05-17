// apps/web/lib/cache.ts
import type { WorldStateResponse } from '@/types'

export class SnapshotCache {
  private cache = new Map<number, WorldStateResponse>()
  private maxSize: number

  constructor(maxSize = 50) {
    this.maxSize = maxSize
  }

  get(year: number): WorldStateResponse | undefined {
    return this.cache.get(year)
  }

  set(year: number, data: WorldStateResponse): void {
    if (this.cache.has(year)) {
      // Delete first so re-insertion doesn't exceed maxSize
      this.cache.delete(year)
    } else if (this.cache.size >= this.maxSize) {
      // Evict oldest (first in insertion order)
      const firstKey = this.cache.keys().next().value as number
      this.cache.delete(firstKey)
    }
    this.cache.set(year, data)
  }

  has(year: number): boolean {
    return this.cache.has(year)
  }

  size(): number {
    return this.cache.size
  }
}

export const snapshotCache = new SnapshotCache()
