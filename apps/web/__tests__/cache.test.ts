// apps/web/__tests__/cache.test.ts
import { describe, it, expect } from 'vitest'
import { SnapshotCache } from '@/lib/cache'
import type { WorldStateResponse } from '@/types'

const makeData = (year: number): WorldStateResponse => ({
  type: 'FeatureCollection',
  year,
  snapshot_year: year,
  features: [],
})

describe('SnapshotCache', () => {
  it('returns undefined for missing key', () => {
    const c = new SnapshotCache()
    expect(c.get(-264)).toBeUndefined()
  })

  it('returns stored value', () => {
    const c = new SnapshotCache()
    c.set(-264, makeData(-264))
    expect(c.get(-264)?.year).toBe(-264)
  })

  it('has() returns false for missing key', () => {
    const c = new SnapshotCache()
    expect(c.has(-264)).toBe(false)
  })

  it('has() returns true after set', () => {
    const c = new SnapshotCache()
    c.set(100, makeData(100))
    expect(c.has(100)).toBe(true)
  })

  it('size() returns 0 for empty cache', () => {
    const c = new SnapshotCache()
    expect(c.size()).toBe(0)
  })

  it('size() increments with each set', () => {
    const c = new SnapshotCache()
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    expect(c.size()).toBe(2)
  })

  it('evicts oldest when maxSize reached', () => {
    const c = new SnapshotCache(3)
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    c.set(3, makeData(3))
    c.set(4, makeData(4))  // triggers eviction of key 1
    expect(c.size()).toBe(3)
    expect(c.has(1)).toBe(false)
    expect(c.has(4)).toBe(true)
  })

  it('evicts in insertion order (LRU)', () => {
    const c = new SnapshotCache(2)
    c.set(10, makeData(10))
    c.set(20, makeData(20))
    c.set(30, makeData(30))  // evicts 10
    expect(c.has(10)).toBe(false)
    expect(c.has(20)).toBe(true)
    expect(c.has(30)).toBe(true)
  })

  it('overwriting existing key does not grow beyond maxSize', () => {
    const c = new SnapshotCache(2)
    c.set(1, makeData(1))
    c.set(2, makeData(2))
    c.set(1, makeData(1))  // overwrite — should NOT evict either key
    expect(c.size()).toBe(2)
    expect(c.has(1)).toBe(true)
    expect(c.has(2)).toBe(true)
  })

  it('default maxSize is 50', () => {
    const c = new SnapshotCache()
    for (let i = 0; i < 50; i++) c.set(i, makeData(i))
    expect(c.size()).toBe(50)
    c.set(50, makeData(50))
    expect(c.size()).toBe(50)
    expect(c.has(0)).toBe(false)
  })
})
