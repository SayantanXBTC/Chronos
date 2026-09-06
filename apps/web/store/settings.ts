// apps/web/store/settings.ts
import { create } from 'zustand'
import { AAA_POLISH_DEFAULT } from '@/lib/flags'
import { setAudioEnabled } from '@/lib/audio'

const STORAGE_KEY = 'chronos:settings'

interface StoredSettings {
  visualPolish?: boolean
  reducedMotion?: boolean
}

function readStored(): StoredSettings {
  if (typeof localStorage === 'undefined') return {}
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function writeStored(partial: StoredSettings): void {
  if (typeof localStorage === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...readStored(), ...partial }))
  } catch {
    // ignore write failures (private browsing, quota, etc.)
  }
}

interface SettingsState {
  visualPolish: boolean
  reducedMotion: boolean
  // Deliberately NOT seeded from localStorage at module scope (unlike
  // visualPolish/reducedMotion) — this store is shared between server and
  // client, and reading the audio-enabled flag here would mismatch
  // server-rendered markup. Starts false; AudioToggle syncs the real value
  // after mount, same SSR-safe pattern it already used before this store
  // existed.
  soundEnabled: boolean
  setVisualPolish: (value: boolean) => void
  setReducedMotion: (value: boolean) => void
  setSoundEnabled: (value: boolean) => void
}

const stored = readStored()

export const useSettingsStore = create<SettingsState>((set) => ({
  visualPolish: stored.visualPolish ?? AAA_POLISH_DEFAULT,
  reducedMotion: stored.reducedMotion ?? false,
  soundEnabled: false,
  setVisualPolish: (visualPolish) => {
    writeStored({ visualPolish })
    set({ visualPolish })
  },
  setReducedMotion: (reducedMotion) => {
    writeStored({ reducedMotion })
    set({ reducedMotion })
  },
  setSoundEnabled: (soundEnabled) => {
    setAudioEnabled(soundEnabled)
    set({ soundEnabled })
  },
}))
