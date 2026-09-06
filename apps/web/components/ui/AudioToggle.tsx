'use client'

import { useEffect } from 'react'
import { Touchable } from './Touchable'
import { useSettingsStore } from '@/store/settings'
import { getAudioEnabled } from '@/lib/audio'

export function AudioToggle() {
  const visualPolish = useSettingsStore((s) => s.visualPolish)
  const enabled = useSettingsStore((s) => s.soundEnabled)
  const setSoundEnabled = useSettingsStore((s) => s.setSoundEnabled)

  useEffect(() => {
    // Deliberately deferred: this component is server-rendered, and
    // getAudioEnabled() reads localStorage — using it as the initial state
    // would mismatch the server-rendered markup for anyone with audio
    // already enabled. Render the SSR-safe default first, sync after mount.
    useSettingsStore.setState({ soundEnabled: getAudioEnabled() })
  }, [])

  if (!visualPolish) return null

  return (
    <div style={{ position: 'absolute', bottom: 56, right: 16, zIndex: 12 }}>
      <Touchable
        onClick={() => setSoundEnabled(!enabled)}
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
