import { describe, it, expect, beforeEach } from 'vitest'
import { useTimelineStore } from '@/store/timeline'

describe('timeline store - aaa fields', () => {
  beforeEach(() => {
    useTimelineStore.setState({
      _pendingFlyTo: null,
      _selectionSource: null,
    })
  })

  it('starts with null _pendingFlyTo', () => {
    expect(useTimelineStore.getState()._pendingFlyTo).toBeNull()
  })

  it('starts with null _selectionSource', () => {
    expect(useTimelineStore.getState()._selectionSource).toBeNull()
  })

  it('setPendingFlyTo sets value', () => {
    const target = { center: [10, 20] as [number, number], zoom: 5 }
    useTimelineStore.getState().setPendingFlyTo(target)
    expect(useTimelineStore.getState()._pendingFlyTo).toEqual(target)
  })

  it('setSelectionSource sets value', () => {
    useTimelineStore.getState().setSelectionSource('map')
    expect(useTimelineStore.getState()._selectionSource).toBe('map')
  })
})
