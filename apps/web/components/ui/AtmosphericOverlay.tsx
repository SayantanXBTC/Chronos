'use client'

import { useTimelineStore } from '@/store/timeline'
import { getEraForYear } from '@/lib/year'

// Per-era filter values: ancient = warmer/more desaturated, modern = neutral
const ERA_DESATURATION: Record<string, string> = {
  'ancient':      'saturate(0.78) sepia(0.12)',
  'classical':    'saturate(0.85) sepia(0.08)',
  'medieval':     'saturate(0.82) sepia(0.10)',
  'early-modern': 'saturate(0.92) sepia(0.04)',
  'modern':       'saturate(1.00)',
}

export function AtmosphericOverlay() {
  const year = useTimelineStore((s) => s.year)
  const era = getEraForYear(year)
  const filter = ERA_DESATURATION[era] ?? 'saturate(1.00)'

  return (
    <>
      {/* Film grain — SVG feTurbulence, very subtle */}
      <div
        data-testid="noise-overlay"
        className="absolute inset-0 pointer-events-none select-none z-10"
        aria-hidden="true"
        style={{ opacity: 0.035, mixBlendMode: 'overlay' }}
      >
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <filter id="grain">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.65"
              numOctaves="3"
              stitchTiles="stitch"
            />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter="url(#grain)" />
        </svg>
      </div>

      {/* Vignette — radial gradient darkening edges */}
      <div
        data-testid="vignette-overlay"
        className="absolute inset-0 pointer-events-none select-none z-10"
        aria-hidden="true"
        style={{
          background: 'radial-gradient(ellipse at 50% 50%, transparent 50%, rgba(0,0,0,0.35) 100%)',
        }}
      />

      {/* Era desaturation — CSS backdropFilter applied over map */}
      <div
        data-testid="desaturation-overlay"
        className={`absolute inset-0 pointer-events-none select-none z-10 era-${era}`}
        aria-hidden="true"
        style={{ backdropFilter: filter, WebkitBackdropFilter: filter }}
      />
    </>
  )
}
