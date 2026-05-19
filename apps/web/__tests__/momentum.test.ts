import { describe, it, expect } from 'vitest'
import { getMomentumOpacity } from '@/lib/momentum'

describe('getMomentumOpacity', () => {
  it('stable territory gets base opacity', () => {
    expect(getMomentumOpacity(-500, null, -264)).toBeCloseTo(0.40, 2)
  })

  it('rising territory (born < 150y ago) gets higher opacity', () => {
    // Born at -300, current year -264 → age = 36 years → rising
    expect(getMomentumOpacity(-300, null, -264)).toBeGreaterThan(0.40)
  })

  it('declining territory (ends within 100y) gets lower opacity', () => {
    // year_end = -200, current = -264 → 64 years until end → declining
    expect(getMomentumOpacity(-500, -200, -264)).toBeLessThan(0.40)
  })

  it('opacity stays within [0.15, 0.60]', () => {
    const cases: [number, number | null, number][] = [
      [-264, null, -264],   // just born
      [-3000, -2900, -2950], // deep past, near end
      [-100, null, 2000],    // very old
    ]
    cases.forEach(([ys, ye, y]) => {
      const op = getMomentumOpacity(ys, ye, y)
      expect(op).toBeGreaterThanOrEqual(0.15)
      expect(op).toBeLessThanOrEqual(0.60)
    })
  })
})
