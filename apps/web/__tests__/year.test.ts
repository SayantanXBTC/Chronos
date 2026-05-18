// apps/web/__tests__/year.test.ts
import { describe, it, expect } from 'vitest'
import { yearToDisplay, sliderToYear, yearToSlider, snapToSnapshot, SNAPSHOT_YEARS } from '@/lib/year'

describe('SNAPSHOT_YEARS', () => {
  it('has 40 values', () => { expect(SNAPSHOT_YEARS).toHaveLength(40) })
  it('starts at -500', () => { expect(SNAPSHOT_YEARS[0]).toBe(-500) })
  it('ends at 500', () => { expect(SNAPSHOT_YEARS[39]).toBe(500) })
  it('excludes 0', () => { expect(SNAPSHOT_YEARS).not.toContain(0) })
  it('contains -475', () => { expect(SNAPSHOT_YEARS).toContain(-475) })
  it('contains 25', () => { expect(SNAPSHOT_YEARS).toContain(25) })
})

describe('yearToDisplay', () => {
  it('negative year is BCE', () => { expect(yearToDisplay(-264)).toBe('264 BCE') })
  it('positive year is CE', () => { expect(yearToDisplay(117)).toBe('117 CE') })
  it('throws on 0', () => { expect(() => yearToDisplay(0)).toThrow() })
  it('-1 is 1 BCE', () => { expect(yearToDisplay(-1)).toBe('1 BCE') })
  it('1 is 1 CE', () => { expect(yearToDisplay(1)).toBe('1 CE') })
  it('-500 is 500 BCE', () => { expect(yearToDisplay(-500)).toBe('500 BCE') })
  it('500 is 500 CE', () => { expect(yearToDisplay(500)).toBe('500 CE') })
})

// Slider range: 0–5025 → years -3000 to 2026 (skipping 0)
// Positions 0–2999: BCE years (-3000 to -1)
// Positions 3000–5025: CE years (1 to 2026)
describe('sliderToYear / yearToSlider roundtrip', () => {
  it('slider 0 → year -3000', () => { expect(sliderToYear(0)).toBe(-3000) })
  it('slider 2999 → year -1', () => { expect(sliderToYear(2999)).toBe(-1) })
  it('slider 3000 → year 1', () => { expect(sliderToYear(3000)).toBe(1) })
  it('slider 5025 → year 2026', () => { expect(sliderToYear(5025)).toBe(2026) })
  it('year -3000 roundtrips', () => { expect(sliderToYear(yearToSlider(-3000))).toBe(-3000) })
  it('year -1 roundtrips', () => { expect(sliderToYear(yearToSlider(-1))).toBe(-1) })
  it('year 1 roundtrips', () => { expect(sliderToYear(yearToSlider(1))).toBe(1) })
  it('year 2026 roundtrips', () => { expect(sliderToYear(yearToSlider(2026))).toBe(2026) })
  it('year -500 roundtrips', () => { expect(sliderToYear(yearToSlider(-500))).toBe(-500) })
  it('year 500 roundtrips', () => { expect(sliderToYear(yearToSlider(500))).toBe(500) })
  it('yearToSlider throws on 0', () => { expect(() => yearToSlider(0)).toThrow() })
  it('yearToSlider(-3000) = 0', () => { expect(yearToSlider(-3000)).toBe(0) })
  it('yearToSlider(2026) = 5025', () => { expect(yearToSlider(2026)).toBe(5025) })
})

describe('snapToSnapshot', () => {
  it('-264 snaps to -275', () => { expect(snapToSnapshot(-264)).toBe(-275) })
  it('-500 snaps to -500', () => { expect(snapToSnapshot(-500)).toBe(-500) })
  it('-275 snaps to itself', () => { expect(snapToSnapshot(-275)).toBe(-275) })
  it('100 snaps to 100', () => { expect(snapToSnapshot(100)).toBe(100) })
  it('110 snaps to 100', () => { expect(snapToSnapshot(110)).toBe(100) })
  it('1 snaps to -25 (largest snapshot <= 1)', () => {
    // -25 is the last negative snapshot; 25 is first positive. Largest snap <= 1 is -25.
    expect(snapToSnapshot(1)).toBe(-25)
  })
  it('25 snaps to itself', () => { expect(snapToSnapshot(25)).toBe(25) })
  // Years outside snapshot range clamp to nearest edge
  it('-3000 snaps to -500 (earliest snapshot)', () => { expect(snapToSnapshot(-3000)).toBe(-500) })
  it('2026 snaps to 500 (latest snapshot)', () => { expect(snapToSnapshot(2026)).toBe(500) })
})
