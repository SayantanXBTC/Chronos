import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'

vi.mock('motion/react', async () => {
  const actual = await vi.importActual<typeof import('motion/react')>('motion/react')
  return { ...actual, useReducedMotion: vi.fn() }
})

import { useReducedMotion } from 'motion/react'
import { ParchmentDust } from '@/components/fx/ParchmentDust'

describe('ParchmentDust', () => {
  it('renders 12 circles by default', () => {
    vi.mocked(useReducedMotion).mockReturnValue(false)
    const { container } = render(<ParchmentDust />)
    expect(container.querySelectorAll('circle').length).toBe(12)
  })

  it('renders nothing when reduced motion preferred', () => {
    vi.mocked(useReducedMotion).mockReturnValue(true)
    const { container } = render(<ParchmentDust />)
    expect(container.querySelectorAll('circle').length).toBe(0)
  })
})
