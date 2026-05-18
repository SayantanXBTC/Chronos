// apps/web/__tests__/timeline.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

beforeEach(() => {
  useTimelineStore.setState({
    year: -264,
    selectedEntity: null,
    isLoading: false,
    error: null,
  })
})

describe('useTimelineStore', () => {
  it('initial year is -264', () => {
    expect(useTimelineStore.getState().year).toBe(-264)
  })

  it('setYear updates year', () => {
    useTimelineStore.getState().setYear(100)
    expect(useTimelineStore.getState().year).toBe(100)
  })

  it('setYear to negative value works', () => {
    useTimelineStore.getState().setYear(-400)
    expect(useTimelineStore.getState().year).toBe(-400)
  })

  it('setLoading toggles isLoading to true', () => {
    useTimelineStore.getState().setLoading(true)
    expect(useTimelineStore.getState().isLoading).toBe(true)
  })

  it('setLoading toggles isLoading to false', () => {
    useTimelineStore.setState({ isLoading: true })
    useTimelineStore.getState().setLoading(false)
    expect(useTimelineStore.getState().isLoading).toBe(false)
  })

  it('setError sets error string', () => {
    useTimelineStore.getState().setError('Network error')
    expect(useTimelineStore.getState().error).toBe('Network error')
  })

  it('setError clears error with null', () => {
    useTimelineStore.setState({ error: 'some error' })
    useTimelineStore.getState().setError(null)
    expect(useTimelineStore.getState().error).toBeNull()
  })

  it('setSelectedEntity updates entity', () => {
    const fakeEntity: EntityFeature = {
      type: 'Feature',
      id: 'rome',
      geometry: { type: 'MultiPolygon', coordinates: [] },
      properties: {
        slug: 'roman-empire',
        name: 'Roman Empire',
        type: 'empire',
        color: '#C0392B',
        confidence: 'approximate',
        confidence_type: 'approximate',
        source_name: null,
        importance: 9,
        entity_id: 'abc-123',
      },
    }
    useTimelineStore.getState().setSelectedEntity(fakeEntity)
    expect(useTimelineStore.getState().selectedEntity?.id).toBe('rome')
    expect(useTimelineStore.getState().selectedEntity?.properties.name).toBe('Roman Empire')
  })

  it('setSelectedEntity clears with null', () => {
    const fakeEntity: EntityFeature = {
      type: 'Feature',
      id: 'rome',
      geometry: { type: 'MultiPolygon', coordinates: [] },
      properties: {
        slug: 'roman-empire',
        name: 'Roman Empire',
        type: 'empire',
        color: '#C0392B',
        confidence: 'approximate',
        confidence_type: 'approximate',
        source_name: null,
        importance: 9,
        entity_id: 'abc-123',
      },
    }
    useTimelineStore.setState({ selectedEntity: fakeEntity })
    useTimelineStore.getState().setSelectedEntity(null)
    expect(useTimelineStore.getState().selectedEntity).toBeNull()
  })
})
