import { describe, it, expect } from 'vitest'
import { SNAPSHOT_YEARS } from '@/lib/year'

describe('expanded preload', () => {
  it('preload candidates include ±5 neighbors', () => {
    const idx = SNAPSHOT_YEARS.indexOf(-250)
    expect(idx).toBeGreaterThan(4)
    const candidates = [
      SNAPSHOT_YEARS[idx - 1],
      SNAPSHOT_YEARS[idx + 1],
      SNAPSHOT_YEARS[idx - 2],
      SNAPSHOT_YEARS[idx + 2],
      SNAPSHOT_YEARS[idx - 3],
      SNAPSHOT_YEARS[idx + 3],
      SNAPSHOT_YEARS[idx - 4],
      SNAPSHOT_YEARS[idx + 4],
      SNAPSHOT_YEARS[idx - 5],
      SNAPSHOT_YEARS[idx + 5],
    ].filter((y): y is number => y !== undefined)
    expect(candidates.length).toBe(10)
  })
})
