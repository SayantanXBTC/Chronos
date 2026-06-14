import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'

describe('OrnamentFrame', () => {
  it('renders children', () => {
    const { getByText } = render(<OrnamentFrame>Hello</OrnamentFrame>)
    expect(getByText('Hello')).toBeTruthy()
  })

  it('full density renders 4 corner seals + top fleuron', () => {
    const { container } = render(<OrnamentFrame density="full">x</OrnamentFrame>)
    expect(container.querySelectorAll('[data-ornament="corner"]').length).toBe(4)
    expect(container.querySelector('[data-ornament="fleuron"]')).toBeTruthy()
  })

  it('mid density renders 4 corner brackets, no fleuron', () => {
    const { container } = render(<OrnamentFrame density="mid">x</OrnamentFrame>)
    expect(container.querySelectorAll('[data-ornament="bracket"]').length).toBe(4)
    expect(container.querySelector('[data-ornament="fleuron"]')).toBeNull()
  })

  it('minimal density renders no decorative spans', () => {
    const { container } = render(<OrnamentFrame density="minimal">x</OrnamentFrame>)
    expect(container.querySelectorAll('[data-ornament]').length).toBe(0)
  })

  it('decorative spans are aria-hidden', () => {
    const { container } = render(<OrnamentFrame density="full">x</OrnamentFrame>)
    const decorations = container.querySelectorAll('[data-ornament]')
    decorations.forEach((el) => {
      expect(el.getAttribute('aria-hidden')).toBe('true')
    })
  })
})
