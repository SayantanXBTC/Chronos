import { describe, it, expect } from 'vitest'

describe('library imports', () => {
  it('motion resolves', async () => {
    const m = await import('motion/react')
    expect(typeof m.motion).not.toBe('undefined')
  })

  it('@use-gesture/react resolves', async () => {
    const g = await import('@use-gesture/react')
    expect(typeof g.useDrag).toBe('function')
  })
})
