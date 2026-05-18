import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EntityPanel } from '@/components/entity/EntityPanel'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature, EntityDetail } from '@/types'

vi.mock('@/lib/api', () => ({
  fetchEntityDetail: vi.fn(),
}))

const mockEntity: EntityFeature = {
  type: 'Feature',
  id: 'roman-empire',
  geometry: { type: 'MultiPolygon', coordinates: [] },
  properties: {
    entity_id: 'uuid-aaa',
    slug: 'roman-empire',
    name: 'Roman Empire',
    type: 'empire',
    color: '#c0392b',
    confidence: 'approximate',
    confidence_type: 'approximate',
    source_name: 'Manual trace',
    importance: 9,
    year_start: -27,
    year_end: 476,
  },
}

const mockDetail: EntityDetail = {
  slug: 'roman-empire',
  name: 'Roman Empire',
  type: 'empire',
  color: '#c0392b',
  year_start: -27,
  year_end: 476,
  source_name: 'Manual trace',
  confidence_type: 'approximate',
  importance: 9,
  lineage: {
    predecessors: [
      { slug: 'roman-republic', name: 'Roman Republic', relationship_type: 'evolved_into', year: -27, notes: null },
    ],
    successors: [
      { slug: 'western-roman-empire', name: 'Western Roman Empire', relationship_type: 'split_from', year: 285, notes: null },
    ],
  },
}

describe('EntityPanel', () => {
  beforeEach(() => {
    useTimelineStore.setState({
      selectedEntity: null,
      currentEntities: [],
      year: 100,
    })
    vi.clearAllMocks()
  })

  it('renders nothing when no entity selected', () => {
    const { container } = render(<EntityPanel />)
    expect(container.firstChild).toBeNull()
  })

  it('shows entity name', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    expect(screen.getByText('Roman Empire')).toBeDefined()
  })

  it('shows dates once detail loads', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText(/27 BCE/)).toBeDefined())
    expect(screen.getByText(/476 CE/)).toBeDefined()
  })

  it('shows predecessor in lineage', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Roman Republic')).toBeDefined())
  })

  it('shows successor in lineage', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Western Roman Empire')).toBeDefined())
  })

  it('shows contemporaries from currentEntities', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    const contemporary: EntityFeature = {
      ...mockEntity,
      id: 'han-dynasty',
      properties: { ...mockEntity.properties, slug: 'han-dynasty', name: 'Han Dynasty', entity_id: 'uuid-bbb' },
    }
    useTimelineStore.setState({
      selectedEntity: mockEntity,
      currentEntities: [mockEntity, contemporary],
    })
    render(<EntityPanel />)
    await waitFor(() => expect(screen.getByText('Han Dynasty')).toBeDefined())
  })

  it('close button deselects entity', async () => {
    const { fetchEntityDetail } = await import('@/lib/api')
    vi.mocked(fetchEntityDetail).mockResolvedValue(mockDetail)
    useTimelineStore.setState({ selectedEntity: mockEntity })
    const user = userEvent.setup()
    render(<EntityPanel />)
    await user.click(screen.getByLabelText('Close entity panel'))
    expect(useTimelineStore.getState().selectedEntity).toBeNull()
  })
})
