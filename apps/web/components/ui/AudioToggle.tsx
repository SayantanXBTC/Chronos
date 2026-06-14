'use client'

import { useState, useEffect } from 'react'
import { Touchable } from './Touchable'
import { AAA_POLISH } from '@/lib/flags'
import { getAudioEnabled, setAudioEnabled } from '@/lib/audio'

export function AudioToggle() {
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
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
