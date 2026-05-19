import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { LatencyTracker } from '@/lib/metrics'

describe('LatencyTracker', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('records a measurement', () => {
    const tracker = new LatencyTracker('test')
    tracker.start()
    vi.advanceTimersByTime(42)
    const ms = tracker.end()
    expect(ms).toBeCloseTo(42, 0)
  })

  it('returns 0 if end called without start', () => {
    const tracker = new LatencyTracker('test')
    expect(tracker.end()).toBe(0)
  })

  it('stores last measurement', () => {
    const tracker = new LatencyTracker('test')
    tracker.start()
    vi.advanceTimersByTime(100)
    tracker.end()
    expect(tracker.last).toBeCloseTo(100, 0)
  })
})
