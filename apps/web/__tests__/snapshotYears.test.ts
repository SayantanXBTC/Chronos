import { describe, it, expect } from 'vitest'
import { SNAPSHOT_YEARS, snapToSnapshot } from '@/lib/year'

describe('SNAPSHOT_YEARS', () => {
  it('starts at -3000', () => { expect(SNAPSHOT_YEARS[0]).toBe(-3000) })
  it('ends at 2026', () => { expect(SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]).toBe(2026) })
  it('contains no year 0', () => { expect(SNAPSHOT_YEARS).not.toContain(0) })
  it('is strictly ascending', () => {
    for (let i = 1; i < SNAPSHOT_YEARS.length; i++) {
      expect(SNAPSHOT_YEARS[i]).toBeGreaterThan(SNAPSHOT_YEARS[i - 1])
    }
  })
  it('has no duplicates', () => {
    expect(SNAPSHOT_YEARS.length).toBe(new Set(SNAPSHOT_YEARS).size)
  })
  it('has ~102 entries', () => {
    expect(SNAPSHOT_YEARS.length).toBeGreaterThanOrEqual(90)
    expect(SNAPSHOT_YEARS.length).toBeLessThanOrEqual(120)
  })
  it('has 250-year steps in ancient period', () => {
    expect(SNAPSHOT_YEARS).toContain(-3000)
    expect(SNAPSHOT_YEARS).toContain(-2750)
    expect(SNAPSHOT_YEARS).not.toContain(-2900)
  })
  it('has 25-year steps in classical period', () => {
    expect(SNAPSHOT_YEARS).toContain(-500)
    expect(SNAPSHOT_YEARS).toContain(-475)
    expect(SNAPSHOT_YEARS).toContain(475)
  })
  it('has 50-year steps in medieval period', () => {
    expect(SNAPSHOT_YEARS).toContain(550)
    expect(SNAPSHOT_YEARS).toContain(600)
    expect(SNAPSHOT_YEARS).not.toContain(525)
  })
  it('has 10-year steps in modern period', () => {
    expect(SNAPSHOT_YEARS).toContain(1910)
    expect(SNAPSHOT_YEARS).toContain(2020)
    expect(SNAPSHOT_YEARS).toContain(2026)
  })
})

describe('snapToSnapshot with expanded years', () => {
  it('snaps -3000 to itself', () => { expect(snapToSnapshot(-3000)).toBe(-3000) })
  it('snaps -2900 to nearest (-2750 or -3000)', () => {
    const result = snapToSnapshot(-2900)
    expect(result === -2750 || result === -3000).toBe(true)
  })
  it('snaps 2026 to itself', () => { expect(snapToSnapshot(2026)).toBe(2026) })
})
