import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ViewportFrame } from '@/components/map/ViewportFrame'

describe('ViewportFrame', () => {
  it('renders 4 corner brackets', () => {
    const { container } = render(<ViewportFrame />)
    expect(container.querySelectorAll('[data-frame-corner]').length).toBe(4)
  })

  it('overlay element has pointer-events none', () => {
    const { container } = render(<ViewportFrame />)
    const overlay = container.firstElementChild as HTMLElement
    expect(overlay.style.pointerEvents).toBe('none')
  })
})
