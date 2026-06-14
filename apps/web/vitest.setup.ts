// apps/web/vitest.setup.ts
import '@testing-library/jest-dom'

// AAA polish components return null when this flag is false. Default to true for tests
// so flag-gated components render and can be asserted against. Individual tests can
// override via `vi.stubEnv` if they need the opposite.
process.env.NEXT_PUBLIC_AAA_POLISH = process.env.NEXT_PUBLIC_AAA_POLISH ?? 'true'
