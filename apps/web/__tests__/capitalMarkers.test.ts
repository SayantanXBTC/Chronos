import { describe, it, expect } from 'vitest'
import { ENTITY_META } from '@/data/entity-metadata'

describe('capital city data', () => {
  it('roman-empire has capital coordinates', () => {
    const meta = ENTITY_META['roman-empire']
    expect(meta.capital).toBeDefined()
    expect(typeof meta.capital!.lon).toBe('number')
    expect(typeof meta.capital!.lat).toBe('number')
    expect(meta.capital!.name).toBe('Rome')
  })

  it('all capitals have lon/lat within valid range', () => {
    for (const [slug, meta] of Object.entries(ENTITY_META)) {
      if (meta.capital) {
        expect(meta.capital.lon, `${slug} lon`).toBeGreaterThanOrEqual(-180)
        expect(meta.capital.lon, `${slug} lon`).toBeLessThanOrEqual(180)
        expect(meta.capital.lat, `${slug} lat`).toBeGreaterThanOrEqual(-90)
        expect(meta.capital.lat, `${slug} lat`).toBeLessThanOrEqual(90)
      }
    }
  })

  it('at least 15 entities have capital data', () => {
    const withCapitals = Object.values(ENTITY_META).filter((m) => m.capital)
    expect(withCapitals.length).toBeGreaterThanOrEqual(15)
  })
})
