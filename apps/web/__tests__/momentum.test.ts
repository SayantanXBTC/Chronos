import { describe, it, expect } from 'vitest'
import { getMomentumOpacity, buildMomentumOpacityExpression } from '@/lib/momentum'

describe('getMomentumOpacity', () => {
  it('stable territory gets base opacity', () => {
    expect(getMomentumOpacity(-500, null, -264)).toBeCloseTo(0.28, 2)
  })

  it('rising territory (born < 150y ago) gets higher opacity', () => {
    // Born at -300, current year -264 → age = 36 years → rising
    expect(getMomentumOpacity(-300, null, -264)).toBeGreaterThan(0.28)
  })

  it('declining territory (ends within 100y) gets lower opacity', () => {
    // year_end = -200, current = -264 → 64 years until end → declining
    expect(getMomentumOpacity(-500, -200, -264)).toBeLessThan(0.28)
  })

  it('opacity stays within [0.12, 0.50]', () => {
    const cases: [number, number | null, number][] = [
      [-264, null, -264],   // just born
      [-3000, -2900, -2950], // deep past, near end
      [-100, null, 2000],    // very old
    ]
    cases.forEach(([ys, ye, y]) => {
      const op = getMomentumOpacity(ys, ye, y)
      expect(op).toBeGreaterThanOrEqual(0.12)
      expect(op).toBeLessThanOrEqual(0.50)
    })
  })
})

describe('lowered base opacity for layered visual system', () => {
  it('BASE_OPACITY in expression is 0.28 for softer fill', () => {
    const expr = buildMomentumOpacityExpression(100) as unknown[]
    // The stable (default) fallback is the last element
    const stable = expr[expr.length - 1] as number
    expect(stable).toBe(0.28)
  })
})
