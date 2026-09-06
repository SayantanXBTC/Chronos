'use client'

import { useState, useEffect } from 'react'
import { Touchable } from './Touchable'
import { AAA_POLISH } from '@/lib/flags'
import { getAudioEnabled, setAudioEnabled } from '@/lib/audio'

export function AudioToggle() {
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
    // Deliberately deferred: this component is server-rendered, and
    // getAudioEnabled() reads localStorage — using it as the initial state
    // would mismatch the server-rendered markup for anyone with audio
    // already enabled. Render the SSR-safe default first, sync after mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setEnabled(getAudioEnabled())
  }, [])

  if (!AAA_POLISH) return null

  function toggle() {
    const next = !enabled
    setAudioEnabled(next)
    setEnabled(next)
  }

  return (
    <div style={{ position: 'absolute', bottom: 56, right: 16, zIndex: 12 }}>
      <Touchable
        onClick={toggle}
        ariaLabel="Toggle UI sounds"
        soundKey="click"
        className="px-2 py-1 font-cinzel text-[10px] tracking-widest"
      >
        <span aria-pressed={enabled} role="switch" style={{ color: 'var(--parchment-ink)' }}>
          {enabled ? '◉ AUDIO' : '○ AUDIO'}
        </span>
      </Touchable>
    </div>
  )
}
