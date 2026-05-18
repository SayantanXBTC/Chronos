// apps/web/__tests__/usePlaceNamesLayer.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { usePlaceNamesLayer } from '@/components/map/usePlaceNamesLayer'
import { useTimelineStore } from '@/store/timeline'
import type { MapViewHandle } from '@/components/map/MapView'
import type { PlaceNamesResponse } from '@/types'

const MOCK_PLACE_NAMES: PlaceNamesResponse = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [12.5, 41.9] },
      properties: { name: 'Rome', name_modern: 'Rome', type: 'city', importance: 10, label_priority: 10 },
    },
  ],
}

vi.mock('@/lib/api', () => ({
  fetchPlaceNames: vi.fn(),
}))

import { fetchPlaceNames } from '@/lib/api'

const mockFetchPlaceNames = vi.mocked(fetchPlaceNames)

function makeMapRef(updatePlaceNames?: (data: PlaceNamesResponse) => void) {
  const handle: MapViewHandle = {
    updateTerritories: vi.fn() as MapViewHandle['updateTerritories'],
    updateRivers: vi.fn() as MapViewHandle['updateRivers'],
    updatePlaceNames: updatePlaceNames ?? (vi.fn() as MapViewHandle['updatePlaceNames']),
  }
  return { current: handle }
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.useFakeTimers()
  mockFetchPlaceNames.mockResolvedValue(MOCK_PLACE_NAMES)
  // Reset store to a known year
  useTimelineStore.setState({ year: -264 })
})

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
})

describe('usePlaceNamesLayer', () => {
  it('fetches place names on mount after debounce', async () => {
    const mapRef = makeMapRef()
    renderHook(() => usePlaceNamesLayer(mapRef))

    vi.advanceTimersByTime(200) // past 150ms debounce
    await vi.runAllTimersAsync()

    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(1)
    expect(mockFetchPlaceNames).toHaveBeenCalledWith(-264, expect.objectContaining({ signal: expect.any(AbortSignal) }))
  })

  it('calls updatePlaceNames with fetched data', async () => {
    const updatePlaceNames = vi.fn()
    const mapRef = makeMapRef(updatePlaceNames)
    renderHook(() => usePlaceNamesLayer(mapRef))

    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()

    expect(updatePlaceNames).toHaveBeenCalledWith(MOCK_PLACE_NAMES)
  })

  it('debounces rapid year changes', async () => {
    const mapRef = makeMapRef()
    renderHook(() => usePlaceNamesLayer(mapRef))

    // Let initial mount debounce fire for -264
    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()
    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(1)

    // Reset mock to track subsequent calls
    mockFetchPlaceNames.mockClear()

    // Rapid year changes: two changes before debounce fires
    useTimelineStore.setState({ year: -300 })
    vi.advanceTimersByTime(50) // 50ms — debounce not yet fired
    expect(mockFetchPlaceNames).not.toHaveBeenCalled()

    useTimelineStore.setState({ year: -200 }) // clears previous timer
    vi.advanceTimersByTime(50) // 100ms total — still not fired
    expect(mockFetchPlaceNames).not.toHaveBeenCalled()

    // Let final debounce complete
    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()

    // Should only fire once for -200, not for intermediate -300
    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(1)
    expect(mockFetchPlaceNames).toHaveBeenCalledWith(-200, expect.anything())
  })

  it('re-fetches when year changes', async () => {
    const mapRef = makeMapRef()
    renderHook(() => usePlaceNamesLayer(mapRef))

    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()
    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(1)

    useTimelineStore.setState({ year: 100 })
    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()

    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(2)
    expect(mockFetchPlaceNames).toHaveBeenLastCalledWith(100, expect.anything())
  })

  it('does not throw when fetch fails', async () => {
    mockFetchPlaceNames.mockRejectedValue(new Error('Network error'))
    const mapRef = makeMapRef()

    expect(() => renderHook(() => usePlaceNamesLayer(mapRef))).not.toThrow()

    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()
    // No uncaught rejection
  })

  it('does not call updatePlaceNames when mapRef is null', async () => {
    const nullRef = { current: null }
    renderHook(() => usePlaceNamesLayer(nullRef))

    vi.advanceTimersByTime(200)
    await vi.runAllTimersAsync()

    expect(mockFetchPlaceNames).toHaveBeenCalledTimes(1)
    // No error — optional chaining in hook guards this
  })
})
