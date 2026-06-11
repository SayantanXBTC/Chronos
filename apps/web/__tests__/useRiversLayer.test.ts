// apps/web/__tests__/useRiversLayer.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useRiversLayer } from '@/components/map/useRiversLayer'
import type { MapViewHandle } from '@/components/map/MapView'
import type { RiversResponse } from '@/types'

const MOCK_RIVERS: RiversResponse = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: { type: 'LineString', coordinates: [[32.9, 22.0], [31.2, 30.1]] },
      properties: { name: 'Nile', name_alt: 'Neilos', importance: 10 },
    },
  ],
}

vi.mock('@/lib/api', () => ({
  fetchRivers: vi.fn(),
}))

import { fetchRivers } from '@/lib/api'

const mockFetchRivers = vi.mocked(fetchRivers)

function makeMapRef(updateRivers?: (data: RiversResponse) => void) {
  const handle: MapViewHandle = {
    updateTerritories: vi.fn() as MapViewHandle['updateTerritories'],
    updateRivers: updateRivers ?? (vi.fn() as MapViewHandle['updateRivers']),
    updatePlaceNames: vi.fn() as MapViewHandle['updatePlaceNames'],
    updateRoutes: vi.fn() as MapViewHandle['updateRoutes'],
    flyTo: vi.fn() as MapViewHandle['flyTo'],
    showTimeLens: vi.fn() as MapViewHandle['showTimeLens'],
    hideTimeLens: vi.fn() as MapViewHandle['hideTimeLens'],
  }
  return { current: handle }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockFetchRivers.mockResolvedValue(MOCK_RIVERS)
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useRiversLayer', () => {
  it('fetches rivers once on mount', async () => {
    const mapRef = makeMapRef()
    renderHook(() => useRiversLayer(mapRef))

    await waitFor(() => {
      expect(mockFetchRivers).toHaveBeenCalledTimes(1)
    })
  })

  it('calls updateRivers with fetched data', async () => {
    const updateRivers = vi.fn()
    const mapRef = makeMapRef(updateRivers)
    renderHook(() => useRiversLayer(mapRef))

    await waitFor(() => {
      expect(updateRivers).toHaveBeenCalledWith(MOCK_RIVERS)
    })
  })

  it('does not re-fetch when year changes (rivers are static)', async () => {
    const mapRef = makeMapRef()

    // Simulate by rendering the hook twice — rivers hook has no deps so won't re-fetch
    const { rerender } = renderHook(() => useRiversLayer(mapRef))
    await waitFor(() => expect(mockFetchRivers).toHaveBeenCalledTimes(1))

    rerender()
    await waitFor(() => expect(mockFetchRivers).toHaveBeenCalledTimes(1))
  })

  it('does not throw when fetch fails', async () => {
    mockFetchRivers.mockRejectedValue(new Error('Network error'))
    const mapRef = makeMapRef()

    // Should not throw
    expect(() => renderHook(() => useRiversLayer(mapRef))).not.toThrow()
    // Wait briefly to let the rejected promise settle
    await new Promise((r) => setTimeout(r, 50))
  })

  it('does not call updateRivers when mapRef is null', async () => {
    const nullRef = { current: null }
    renderHook(() => useRiversLayer(nullRef))

    await waitFor(() => expect(mockFetchRivers).toHaveBeenCalledTimes(1))
    // No error thrown — mapRef?.updateRivers guarded
  })
})
