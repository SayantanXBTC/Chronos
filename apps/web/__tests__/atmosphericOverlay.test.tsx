import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AtmosphericOverlay } from '@/components/ui/AtmosphericOverlay'
import { useTimelineStore } from '@/store/timeline'

describe('AtmosphericOverlay', () => {
  beforeEach(() => {
    useTimelineStore.setState({ year: -264 })
  })

  it('renders noise overlay element', () => {
    render(<AtmosphericOverlay />)
    expect(screen.getByTestId('noise-overlay')).toBeDefined()
  })

  it('renders vignette overlay element', () => {
    render(<AtmosphericOverlay />)
    expect(screen.getByTestId('vignette-overlay')).toBeDefined()
  })

  it('applies ancient desaturation class for BCE year', () => {
    useTimelineStore.setState({ year: -1000 })
    render(<AtmosphericOverlay />)
    const container = screen.getByTestId('desaturation-overlay')
    expect(container.className).toContain('era-ancient')
  })

  it('applies modern class for CE year >= 1800', () => {
    useTimelineStore.setState({ year: 1900 })
    render(<AtmosphericOverlay />)
    const container = screen.getByTestId('desaturation-overlay')
    expect(container.className).toContain('era-modern')
  })
})
