import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, fireEvent, act } from '@testing-library/react'
import { Touchable } from '@/components/ui/Touchable'

vi.mock('@/lib/audio', () => ({
  playSound: vi.fn(),
}))

import { playSound } from '@/lib/audio'

describe('Touchable', () => {
  beforeEach(() => {
    vi.mocked(playSound).mockClear()
  })

  it('renders children', () => {
    const { getByText } = render(<Touchable onClick={() => {}}>Hi</Touchable>)
    expect(getByText('Hi')).toBeTruthy()
  })

  it('fires onClick handler', () => {
    const fn = vi.fn()
    const { getByRole } = render(<Touchable onClick={fn}>x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(fn).toHaveBeenCalledOnce()
  })

  it('calls playSound("click") on click', () => {
    const { getByRole } = render(<Touchable onClick={() => {}}>x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(playSound).toHaveBeenCalledWith('click')
  })

  it('respects custom soundKey', () => {
    const { getByRole } = render(<Touchable onClick={() => {}} soundKey="open">x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(playSound).toHaveBeenCalledWith('open')
  })

  it('spawns ripple element on click and removes it', async () => {
    const { getByRole, container } = render(<Touchable onClick={() => {}}>x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(container.querySelector('[data-ripple]')).toBeTruthy()
    await act(async () => {
      await new Promise((r) => setTimeout(r, 400))
    })
    expect(container.querySelector('[data-ripple]')).toBeNull()
  })

  it('ripple disabled when ripple=false', () => {
    const { getByRole, container } = render(<Touchable onClick={() => {}} ripple={false}>x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(container.querySelector('[data-ripple]')).toBeNull()
  })

  it('disabled blocks click + audio', () => {
    const fn = vi.fn()
    const { getByRole } = render(<Touchable onClick={fn} disabled>x</Touchable>)
    fireEvent.click(getByRole('button'))
    expect(fn).not.toHaveBeenCalled()
    expect(playSound).not.toHaveBeenCalled()
  })
})
