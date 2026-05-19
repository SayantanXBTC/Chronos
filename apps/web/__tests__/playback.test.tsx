import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlaybackControls } from '@/components/timeline/PlaybackControls'
import { useTimelineStore } from '@/store/timeline'

describe('PlaybackControls', () => {
  beforeEach(() => {
    useTimelineStore.setState({ isPlaying: false, playSpeed: 1 })
    vi.clearAllMocks()
  })

  it('shows play button when not playing', () => {
    render(<PlaybackControls />)
    expect(screen.getByLabelText('Play timeline')).toBeDefined()
  })

  it('shows pause button when playing', () => {
    useTimelineStore.setState({ isPlaying: true })
    render(<PlaybackControls />)
    expect(screen.getByLabelText('Pause playback')).toBeDefined()
  })

  it('toggles play on click', async () => {
    const user = userEvent.setup()
    render(<PlaybackControls />)
    await user.click(screen.getByLabelText('Play timeline'))
    expect(useTimelineStore.getState().isPlaying).toBe(true)
  })

  it('toggles pause on click when playing', async () => {
    useTimelineStore.setState({ isPlaying: true })
    const user = userEvent.setup()
    render(<PlaybackControls />)
    await user.click(screen.getByLabelText('Pause playback'))
    expect(useTimelineStore.getState().isPlaying).toBe(false)
  })

  it('speed buttons exist for all speeds', () => {
    render(<PlaybackControls />)
    expect(screen.getByText('½×')).toBeDefined()
    expect(screen.getByText('1×')).toBeDefined()
    expect(screen.getByText('2×')).toBeDefined()
    expect(screen.getByText('5×')).toBeDefined()
  })

  it('sets play speed on click', async () => {
    const user = userEvent.setup()
    render(<PlaybackControls />)
    await user.click(screen.getByText('2×'))
    expect(useTimelineStore.getState().playSpeed).toBe(2)
  })

  it('active speed button has aria-pressed=true', () => {
    useTimelineStore.setState({ playSpeed: 2 })
    render(<PlaybackControls />)
    const btn = screen.getByText('2×').closest('button')
    expect(btn?.getAttribute('aria-pressed')).toBe('true')
  })

  it('inactive speed button has aria-pressed=false', () => {
    useTimelineStore.setState({ playSpeed: 1 })
    render(<PlaybackControls />)
    const btn = screen.getByText('2×').closest('button')
    expect(btn?.getAttribute('aria-pressed')).toBe('false')
  })
})
