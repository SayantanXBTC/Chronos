import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TimelineSlider } from '@/components/timeline/TimelineSlider'
import { useTimelineStore } from '@/store/timeline'
import { ERA_MARKERS, snapToPrevSnapshot, snapToNextSnapshot } from '@/lib/year'

beforeEach(() => {
  useTimelineStore.setState({ year: -264 })
})

describe('ERA_MARKERS', () => {
  it('contains Ancient, Classical, Medieval, Early Modern, Modern', () => {
    const labels = ERA_MARKERS.map((e) => e.label)
    expect(labels).toContain('Ancient')
    expect(labels).toContain('Classical')
    expect(labels).toContain('Medieval')
    expect(labels).toContain('Early Modern')
    expect(labels).toContain('Modern')
  })

  it('each marker has year and label', () => {
    ERA_MARKERS.forEach((m) => {
      expect(typeof m.year).toBe('number')
      expect(typeof m.label).toBe('string')
    })
  })
})

describe('snapToPrevSnapshot', () => {
  it('moves to previous snapshot year', () => {
    // -500 is in SNAPSHOT_YEARS; previous should be -600
    const prev = snapToPrevSnapshot(-500)
    expect(prev).toBe(-600)
  })

  it('handles non-snapshot year by finding nearest lower', () => {
    // -264 is NOT in SNAPSHOT_YEARS; nearest lower snapshot is -275
    const prev = snapToPrevSnapshot(-264)
    expect(prev).toBeLessThan(-264)
    expect(prev).toBeGreaterThan(-3000)  // should NOT jump to minimum
  })

  it('does not go below minimum snapshot', () => {
    const prev = snapToPrevSnapshot(-3000)
    expect(prev).toBe(-3000)
  })
})

describe('snapToNextSnapshot', () => {
  it('moves to next snapshot year', () => {
    const next = snapToNextSnapshot(-264)
    expect(next).toBeGreaterThan(-264)
  })

  it('does not exceed maximum snapshot', () => {
    const next = snapToNextSnapshot(2026)
    expect(next).toBe(2026)
  })
})

describe('TimelineSlider keyboard navigation', () => {
  it('ArrowRight advances year', () => {
    render(<TimelineSlider />)
    const slider = screen.getByRole('slider', { name: /timeline year/i })
    fireEvent.keyDown(slider, { key: 'ArrowRight' })
    expect(useTimelineStore.getState().year).toBeGreaterThan(-264)
  })

  it('ArrowLeft retreats year', () => {
    render(<TimelineSlider />)
    const slider = screen.getByRole('slider', { name: /timeline year/i })
    fireEvent.keyDown(slider, { key: 'ArrowLeft' })
    expect(useTimelineStore.getState().year).toBeLessThan(-264)
  })

  it('renders era labels', () => {
    render(<TimelineSlider />)
    expect(screen.getByText('Classical')).toBeDefined()
    expect(screen.getByText('Medieval')).toBeDefined()
  })
})
