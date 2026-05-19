import { describe, it, expect } from 'vitest'
import { clampSlider, easeOut } from '@/lib/easing'

describe('clampSlider', () => {
  it('clamps below 0 to 0', () => expect(clampSlider(-10)).toBe(0))
  it('clamps above 5025 to 5025', () => expect(clampSlider(6000)).toBe(5025))
  it('passes through middle value', () => expect(clampSlider(2000)).toBe(2000))
})

describe('easeOut', () => {
  it('returns 0 for t=0', () => expect(easeOut(0)).toBeCloseTo(0))
  it('returns 1 for t=1', () => expect(easeOut(1)).toBeCloseTo(1))
  it('decelerates (midpoint > 0.5)', () => expect(easeOut(0.5)).toBeGreaterThan(0.5))
})
