import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('audio system', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('disabled by default', async () => {
    const { getAudioEnabled } = await import('@/lib/audio')
    expect(getAudioEnabled()).toBe(false)
  })

  it('setAudioEnabled persists to localStorage', async () => {
    const { setAudioEnabled, getAudioEnabled } = await import('@/lib/audio')
    setAudioEnabled(true)
    expect(getAudioEnabled()).toBe(true)
    expect(localStorage.getItem('chronos:audio-enabled')).toBe('true')
  })

  it('reads localStorage on init', async () => {
    localStorage.setItem('chronos:audio-enabled', 'true')
    vi.resetModules()
    const { getAudioEnabled } = await import('@/lib/audio')
    expect(getAudioEnabled()).toBe(true)
  })

  it('playSound is no-op when disabled', async () => {
    const { playSound } = await import('@/lib/audio')
    expect(() => playSound('click')).not.toThrow()
  })

  it('playSound is no-op when AudioContext unavailable', async () => {
    const { setAudioEnabled, playSound } = await import('@/lib/audio')
    setAudioEnabled(true)
    // jsdom has no AudioContext — should silently no-op
    expect(() => playSound('click')).not.toThrow()
  })
})
