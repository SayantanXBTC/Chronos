import { describe, it, expect, afterEach, vi } from 'vitest'

describe('AAA_POLISH flag', () => {
  const orig = process.env.NEXT_PUBLIC_AAA_POLISH

  afterEach(() => {
    process.env.NEXT_PUBLIC_AAA_POLISH = orig
    vi.resetModules()
  })

  it('is true when env var is "true"', async () => {
    process.env.NEXT_PUBLIC_AAA_POLISH = 'true'
    vi.resetModules()
    const { AAA_POLISH } = await import('@/lib/flags')
    expect(AAA_POLISH).toBe(true)
  })

  it('is false when env var is "false"', async () => {
    process.env.NEXT_PUBLIC_AAA_POLISH = 'false'
    vi.resetModules()
    const { AAA_POLISH } = await import('@/lib/flags')
    expect(AAA_POLISH).toBe(false)
  })

  it('is true when env var unset (polish is the default experience)', async () => {
    delete process.env.NEXT_PUBLIC_AAA_POLISH
    vi.resetModules()
    const { AAA_POLISH } = await import('@/lib/flags')
    expect(AAA_POLISH).toBe(true)
  })
})
