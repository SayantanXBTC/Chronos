import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TemporalOverlay } from '@/components/ui/TemporalOverlay'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

vi.mock('@/store/timeline', async () => {
  const actual = await vi.importActual('@/store/timeline')
  return actual
})

const mockEntity = (slug: string, name: string, importance: number): EntityFeature => ({
  type: 'Feature',
  id: slug,
  geometry: { type: 'MultiPolygon', coordinates: [] },
  properties: {
    entity_id: `id-${slug}`, slug, name, type: 'empire',
    color: '#c00', confidence: 'approximate', confidence_type: 'approximate',
    source_name: null, importance, year_start: -100, year_end: null,
  },
})

beforeEach(() => {
  useTimelineStore.setState({ year: -27, currentEntities: [] })
})

describe('TemporalOverlay', () => {
  it('renders without crash at far year', () => {
    useTimelineStore.setState({ year: -2999, currentEntities: [] })
    const { container } = render(<TemporalOverlay />)
    expect(container).toBeDefined()
  })

  it('shows event text near year -27', () => {
    useTimelineStore.setState({ year: -27, currentEntities: [] })
    render(<TemporalOverlay />)
    expect(screen.getByText(/Roman Republic becomes the Roman Empire/i)).toBeDefined()
  })

  it('shows world powers from currentEntities', () => {
    useTimelineStore.setState({
      year: 100,
      currentEntities: [
        mockEntity('roman-empire', 'Roman Empire', 9),
        mockEntity('han-dynasty', 'Han Dynasty', 8),
      ],
    })
    render(<TemporalOverlay />)
    expect(screen.getByText('Roman Empire')).toBeDefined()
    expect(screen.getByText('Han Dynasty')).toBeDefined()
  })

  it('shows max 3 world powers', () => {
    useTimelineStore.setState({
      year: 100,
      currentEntities: [
        mockEntity('a', 'Alpha', 9),
        mockEntity('b', 'Beta', 8),
        mockEntity('c', 'Gamma', 7),
        mockEntity('d', 'Delta', 6),
      ],
    })
    render(<TemporalOverlay />)
    expect(screen.queryByText('Delta')).toBeNull()
  })
})
