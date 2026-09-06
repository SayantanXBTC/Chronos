// apps/web/vitest.setup.ts
import '@testing-library/jest-dom'

// Vitest's built-in jsdom environment (v4) doesn't wire up a working
// `window.localStorage`/`sessionStorage` (jsdom itself supports it fine when
// given a real origin — this is a gap in how vitest constructs its jsdom
// instance). Code under test uses the bare global, as it would in a real
// browser, so give it a small in-memory Storage-compatible polyfill.
class MemoryStorage implements Storage {
  private store = new Map<string, string>()
  get length() { return this.store.size }
  clear() { this.store.clear() }
  getItem(key: string) { return this.store.has(key) ? this.store.get(key)! : null }
  key(index: number) { return Array.from(this.store.keys())[index] ?? null }
  removeItem(key: string) { this.store.delete(key) }
  setItem(key: string, value: string) { this.store.set(key, String(value)) }
}

for (const name of ['localStorage', 'sessionStorage'] as const) {
  Object.defineProperty(globalThis, name, {
    value: new MemoryStorage(),
    writable: true,
    configurable: true,
  })
  Object.defineProperty(window, name, {
    value: globalThis[name],
    writable: true,
    configurable: true,
  })
}

// AAA polish components return null when this flag is false. Default to true for tests
// so flag-gated components render and can be asserted against. Individual tests can
// override via `vi.stubEnv` if they need the opposite.
process.env.NEXT_PUBLIC_AAA_POLISH = process.env.NEXT_PUBLIC_AAA_POLISH ?? 'true'
