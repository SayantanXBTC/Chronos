'use client'

import type { ReactNode } from 'react'

export type OrnamentDensity = 'full' | 'mid' | 'minimal'

interface OrnamentFrameProps {
  children: ReactNode
  density?: OrnamentDensity
  className?: string
}

export function OrnamentFrame({ children, density = 'full', className = '' }: OrnamentFrameProps) {
  const baseStyle: React.CSSProperties = {
    position: 'relative',
    background: 'var(--parchment-gradient)',
    color: 'var(--parchment-ink)',
    border: density === 'minimal' ? '1px solid var(--parchment-border)' : '2px solid var(--parchment-border)',
    outline: density === 'full' ? '1px solid var(--parchment-border-light)' : undefined,
    outlineOffset: density === 'full' ? '2px' : undefined,
    padding: density === 'full' ? '20px 22px' : density === 'mid' ? '14px 16px' : '8px 12px',
    boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
  }

  return (
    <div className={className} style={baseStyle}>
      {density === 'full' && (
        <>
          <span data-ornament="corner" aria-hidden="true" style={cornerSeal('tl')} />
          <span data-ornament="corner" aria-hidden="true" style={cornerSeal('tr')} />
          <span data-ornament="corner" aria-hidden="true" style={cornerSeal('bl')} />
          <span data-ornament="corner" aria-hidden="true" style={cornerSeal('br')} />
          <span data-ornament="fleuron" aria-hidden="true" style={fleuronStyle}>✦ · ✦ · ✦</span>
        </>
      )}
      {density === 'mid' && (
        <>
          <span data-ornament="bracket" aria-hidden="true" style={bracketStyle('tl')} />
          <span data-ornament="bracket" aria-hidden="true" style={bracketStyle('tr')} />
          <span data-ornament="bracket" aria-hidden="true" style={bracketStyle('bl')} />
          <span data-ornament="bracket" aria-hidden="true" style={bracketStyle('br')} />
        </>
      )}
      {children}
    </div>
  )
}

function cornerSeal(pos: 'tl' | 'tr' | 'bl' | 'br'): React.CSSProperties {
  const base: React.CSSProperties = {
    position: 'absolute',
    width: 14, height: 14,
    background: 'radial-gradient(circle, var(--parchment-border-light) 35%, transparent 60%)',
    pointerEvents: 'none',
  }
  if (pos === 'tl') return { ...base, top: -7, left: -7 }
  if (pos === 'tr') return { ...base, top: -7, right: -7 }
  if (pos === 'bl') return { ...base, bottom: -7, left: -7 }
  return { ...base, bottom: -7, right: -7 }
}

function bracketStyle(pos: 'tl' | 'tr' | 'bl' | 'br'): React.CSSProperties {
  const base: React.CSSProperties = {
    position: 'absolute',
    width: 18, height: 18,
    border: '1.5px solid var(--parchment-border)',
    pointerEvents: 'none',
  }
  if (pos === 'tl') return { ...base, top: 4, left: 4, borderRight: 'none', borderBottom: 'none' }
  if (pos === 'tr') return { ...base, top: 4, right: 4, borderLeft: 'none', borderBottom: 'none' }
  if (pos === 'bl') return { ...base, bottom: 4, left: 4, borderRight: 'none', borderTop: 'none' }
  return { ...base, bottom: 4, right: 4, borderLeft: 'none', borderTop: 'none' }
}

const fleuronStyle: React.CSSProperties = {
  position: 'absolute',
  top: 6,
  left: '50%',
  transform: 'translateX(-50%)',
  fontFamily: 'var(--font-cinzel)',
  fontSize: 10,
  letterSpacing: '0.4em',
  color: 'var(--parchment-border)',
  pointerEvents: 'none',
}
