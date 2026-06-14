'use client'

import { AAA_POLISH } from '@/lib/flags'

export function ViewportFrame() {
  if (!AAA_POLISH) return null
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 5,
        boxShadow:
          'inset 0 0 100px 30px rgba(0,0,0,0.85), inset 0 0 0 1px rgba(212,168,71,0.4)',
      }}
    >
      <span data-frame-corner style={corner('tl')} />
      <span data-frame-corner style={corner('tr')} />
      <span data-frame-corner style={corner('bl')} />
      <span data-frame-corner style={corner('br')} />
    </div>
  )
}

function corner(pos: 'tl' | 'tr' | 'bl' | 'br'): React.CSSProperties {
  const base: React.CSSProperties = {
    position: 'absolute',
    width: 28, height: 28,
    border: '1.5px solid var(--parchment-border-light)',
    filter: 'drop-shadow(0 0 6px rgba(212,168,71,0.4))',
    opacity: 0.85,
  }
  if (pos === 'tl') return { ...base, top: 10, left: 10, borderRight: 'none', borderBottom: 'none' }
  if (pos === 'tr') return { ...base, top: 10, right: 10, borderLeft: 'none', borderBottom: 'none' }
  if (pos === 'bl') return { ...base, bottom: 10, left: 10, borderRight: 'none', borderTop: 'none' }
  return { ...base, bottom: 10, right: 10, borderLeft: 'none', borderTop: 'none' }
}
