import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, fireEvent } from '@testing-library/react'

vi.mock('@/lib/audio', () => ({
  getAudioEnabled: vi.fn(),
  setAudioEnabled: vi.fn(),
  playSound: vi.fn(),
}))

import { getAudioEnabled, setAudioEnabled } from '@/lib/audio'
import { AudioToggle } from '@/components/ui/AudioToggle'

describe('AudioToggle', () => {
  beforeEach(() => {
    vi.mocked(getAudioEnabled).mockReset()
    vi.mocked(setAudioEnabled).mockReset()
  })

  it('renders OFF icon when disabled', () => {
    vi.mocked(getAudioEnabled).mockReturnValue(false)
    const { container } = render(<AudioToggle />)
    expect(container.querySelector('[aria-pressed="false"]')).toBeTruthy()
  })

  it('renders ON icon when enabled', () => {
    vi.mocked(getAudioEnabled).mockReturnValue(true)
    const { container } = render(<AudioToggle />)
    expect(container.querySelector('[aria-pressed="true"]')).toBeTruthy()
  })

  it('toggles on click', () => {
    vi.mocked(getAudioEnabled).mockReturnValue(false)
    const { getByRole } = render(<AudioToggle />)
    fireEvent.click(getByRole('button'))
    expect(setAudioEnabled).toHaveBeenCalledWith(true)
  })
})
