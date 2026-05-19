import { describe, it, expect } from 'vitest'
import { EVENTS } from '@/components/ui/TemporalOverlay'

describe('expanded EVENTS array', () => {
  it('has at least 55 entries', () => {
    expect(EVENTS.length).toBeGreaterThanOrEqual(55)
  })

  it('covers Bronze Age (-3000 to -1200)', () => {
    const early = EVENTS.filter((e) => e.year <= -1200)
    expect(early.length).toBeGreaterThanOrEqual(3)
  })

  it('covers post-1500 CE era', () => {
    const modern = EVENTS.filter((e) => e.year >= 1500)
    expect(modern.length).toBeGreaterThanOrEqual(8)
  })

  it('all entries have year and text', () => {
    for (const ev of EVENTS) {
      expect(typeof ev.year).toBe('number')
      expect(ev.text.length).toBeGreaterThan(10)
    }
  })
})
