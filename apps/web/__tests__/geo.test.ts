import { describe, it, expect } from 'vitest'
import { bboxCenter, featureCentroid } from '@/lib/geo'
import type { EntityFeature } from '@/types'

describe('bboxCenter', () => {
  it('returns midpoint of bbox', () => {
    const [lng, lat] = bboxCenter([0, 0, 10, 20])
    expect(lng).toBe(5)
    expect(lat).toBe(10)
  })

  it('handles negative coordinates', () => {
    const [lng, lat] = bboxCenter([-20, -10, 0, 0])
    expect(lng).toBe(-10)
    expect(lat).toBe(-5)
  })
})

describe('featureCentroid', () => {
  const makeFeature = (coords: number[][][][]): EntityFeature => ({
    type: 'Feature',
    id: 'x',
    geometry: { type: 'MultiPolygon', coordinates: coords },
    properties: {
      entity_id: 'x',
      slug: 'x',
      name: 'X',
      type: 'state',
      color: '#fff',
      confidence: 'high',
      year_start: 0,
      year_end: 0,
      confidence_type: 'exact',
      source_name: '',
      importance: 1,
    },
  })

  it('returns center of single rectangular polygon', () => {
    const f = makeFeature([[[[0, 0], [10, 0], [10, 20], [0, 20], [0, 0]]]])
    const [lng, lat] = featureCentroid(f)
    expect(lng).toBe(5)
    expect(lat).toBe(10)
  })

  it('returns center of multi-polygon bbox union', () => {
    const f = makeFeature([
      [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
      [[[20, 20], [30, 20], [30, 30], [20, 30], [20, 20]]],
    ])
    const [lng, lat] = featureCentroid(f)
    expect(lng).toBe(15)
    expect(lat).toBe(15)
  })
})
