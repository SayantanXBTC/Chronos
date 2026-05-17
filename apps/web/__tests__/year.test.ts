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

describe('sliderToYear / yearToSlider roundtrip', () => {
  it('slider 0 → year -500', () => { expect(sliderToYear(0)).toBe(-500) })
  it('slider 499 → year -1', () => { expect(sliderToYear(499)).toBe(-1) })
  it('slider 500 → year 1', () => { expect(sliderToYear(500)).toBe(1) })
  it('slider 999 → year 500', () => { expect(sliderToYear(999)).toBe(500) })
  it('year -500 roundtrips', () => { expect(sliderToYear(yearToSlider(-500))).toBe(-500) })
  it('year -1 roundtrips', () => { expect(sliderToYear(yearToSlider(-1))).toBe(-1) })
  it('year 1 roundtrips', () => { expect(sliderToYear(yearToSlider(1))).toBe(1) })
  it('year 500 roundtrips', () => { expect(sliderToYear(yearToSlider(500))).toBe(500) })
  it('yearToSlider throws on 0', () => { expect(() => yearToSlider(0)).toThrow() })
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
})
