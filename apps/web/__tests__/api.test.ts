// apps/web/__tests__/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchWorldState, fetchSnapshots } from '@/lib/api'

const mockResponse = (data: unknown, ok = true) =>
  Promise.resolve({
    ok,
    status: ok ? 200 : 500,
    json: () => Promise.resolve(data),
  } as Response)

beforeEach(() => { vi.restoreAllMocks() })

describe('fetchWorldState', () => {
  it('calls correct URL with year param', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] })
    )
    await fetchWorldState(-264)
    expect(spy).toHaveBeenCalledWith(
      expect.stringContaining('year=-264'),
      expect.anything()
    )
  })

  it('includes required query params', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] })
    )
    await fetchWorldState(-264)
    const url = spy.mock.calls[0][0] as string
    expect(url).toContain('zoom=4')
    expect(url).toContain('min_x=-180')
    expect(url).toContain('max_x=180')
  })

  it('throws on non-ok response', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse({}, false))
    await expect(fetchWorldState(-264)).rejects.toThrow('API error')
  })

  it('passes AbortSignal when provided', async () => {
    const spy = vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ type: 'FeatureCollection', year: 100, snapshot_year: 100, features: [] })
    )
    const controller = new AbortController()
    await fetchWorldState(100, { signal: controller.signal })
    const init = spy.mock.calls[0][1] as RequestInit
    expect(init.signal).toBe(controller.signal)
  })

  it('returns parsed WorldStateResponse', async () => {
    const payload = { type: 'FeatureCollection', year: -264, snapshot_year: -275, features: [] }
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse(payload))
    const result = await fetchWorldState(-264)
    expect(result.year).toBe(-264)
    expect(result.type).toBe('FeatureCollection')
  })
})

describe('fetchSnapshots', () => {
  it('returns snapshots array', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(
      mockResponse({ snapshots: [-500, -475] })
    )
    const result = await fetchSnapshots()
    expect(result).toEqual([-500, -475])
  })

  it('throws on non-ok response', async () => {
    vi.spyOn(global, 'fetch').mockReturnValue(mockResponse({}, false))
    await expect(fetchSnapshots()).rejects.toThrow('API error')
  })
})
