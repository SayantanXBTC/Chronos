import { describe, it, expect } from 'vitest'
import { computeDiscoveryPrompts } from '@/lib/discovery'
import type { EntityFeature } from '@/types'

function makeEntity(slug: string, name: string, importance: number, yearStart: number, yearEnd: number | null, color = '#888'): EntityFeature {
  return {
    type: 'Feature',
    id: slug,
    geometry: { type: 'MultiPolygon', coordinates: [] },
    properties: {
      entity_id: slug,
      slug,
      name,
      type: 'empire',
      color,
      confidence: 'approximate',
      confidence_type: 'approximate',
      source_name: null,
      importance,
      year_start: yearStart,
      year_end: yearEnd,
    },
  }
}

const ROME = makeEntity('roman-empire', 'Roman Empire', 10, -27, 476, '#B22222')
const HAN = makeEntity('han-dynasty', 'Han Dynasty', 8, -206, 220, '#8B0000')
const CARTHAGE = makeEntity('carthage', 'Carthage', 6, -814, -146, '#DAA520')

describe('computeDiscoveryPrompts', () => {
  it('returns empty array for no entities', () => {
    expect(computeDiscoveryPrompts([], 0)).toEqual([])
  })

  it('returns at most 3 prompts', () => {
    expect(computeDiscoveryPrompts([ROME, HAN, CARTHAGE], 100).length).toBeLessThanOrEqual(3)
  })

  it('dominant-now prompt targets highest-importance entity', () => {
    const prompts = computeDiscoveryPrompts([ROME, HAN, CARTHAGE], 100)
    const dominant = prompts.find((p) => p.id === 'dominant-now')
    expect(dominant).toBeDefined()
    expect(dominant!.slug).toBe('roman-empire')
  })

  it('longest-reign prompt targets entity with greatest lifespan', () => {
    // Rome: 503 years. Han: 426. Carthage: 668.
    const prompts = computeDiscoveryPrompts([ROME, HAN, CARTHAGE], -200)
    const longest = prompts.find((p) => p.id === 'longest-reign')
    expect(longest).toBeDefined()
    expect(longest!.slug).toBe('carthage')
  })

  it('all prompts have required fields', () => {
    const prompts = computeDiscoveryPrompts([ROME, HAN], 0)
    for (const p of prompts) {
      expect(p.id).toBeTruthy()
      expect(p.label.length).toBeGreaterThan(0)
      expect(p.cta.length).toBeGreaterThan(0)
      expect(p.slug).toBeTruthy()
    }
  })

  it('no two prompts share the same slug', () => {
    const prompts = computeDiscoveryPrompts([ROME, HAN, CARTHAGE], -200)
    const slugs = prompts.map((p) => p.slug)
    expect(new Set(slugs).size).toBe(slugs.length)
  })
})
