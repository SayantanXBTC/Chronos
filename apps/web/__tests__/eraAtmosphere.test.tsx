import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { getEraForYear, ERA_MAP_BACKGROUNDS, ERA_WATER_COLORS } from '@/lib/year'
import { EraAtmosphere } from '@/components/ui/EraAtmosphere'
import { useTimelineStore } from '@/store/timeline'

describe('getEraForYear', () => {
  it('returns ancient for year < -500', () => {
    expect(getEraForYear(-1000)).toBe('ancient')
    expect(getEraForYear(-3000)).toBe('ancient')
  })

  it('returns classical for -500 to 499', () => {
    expect(getEraForYear(-500)).toBe('classical')
    expect(getEraForYear(0)).toBe('classical')
    expect(getEraForYear(499)).toBe('classical')
  })

  it('returns medieval for 500 to 1499', () => {
    expect(getEraForYear(500)).toBe('medieval')
    expect(getEraForYear(1000)).toBe('medieval')
  })

  it('returns early-modern for 1500 to 1799', () => {
    expect(getEraForYear(1500)).toBe('early-modern')
    expect(getEraForYear(1750)).toBe('early-modern')
  })

  it('returns modern for >= 1800', () => {
    expect(getEraForYear(1800)).toBe('modern')
    expect(getEraForYear(2000)).toBe('modern')
  })

  it('ERA_MAP_BACKGROUNDS has entry for every era', () => {
    const eras = ['ancient', 'classical', 'medieval', 'early-modern', 'modern'] as const
    eras.forEach((era) => {
      expect(ERA_MAP_BACKGROUNDS[era]).toMatch(/^#[0-9a-fA-F]{6}$/)
    })
  })

  it('ERA_WATER_COLORS has entry for every era', () => {
    const eras = ['ancient', 'classical', 'medieval', 'early-modern', 'modern'] as const
    eras.forEach((era) => {
      expect(ERA_WATER_COLORS[era]).toMatch(/^#[0-9a-fA-F]{6}$/)
    })
  })
})

describe('EraAtmosphere component', () => {
  it('sets data-era attribute on documentElement', () => {
    useTimelineStore.setState({ year: -1000 })
    render(<EraAtmosphere />)
    expect(document.documentElement.getAttribute('data-era')).toBe('ancient')
  })

  it('updates data-era when year changes era', () => {
    useTimelineStore.setState({ year: 1000 })
    render(<EraAtmosphere />)
    expect(document.documentElement.getAttribute('data-era')).toBe('medieval')
  })
})
