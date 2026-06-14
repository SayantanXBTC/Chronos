export type SoundKey = 'click' | 'open' | 'close' | 'hover' | 'error' | 'transition'

const SOUND_FILES: Record<SoundKey, string> = {
  click: '/audio/click.ogg',
  open: '/audio/open.ogg',
  close: '/audio/close.ogg',
  hover: '/audio/hover.ogg',
  error: '/audio/error.ogg',
  transition: '/audio/transition.ogg',
}

const STORAGE_KEY = 'chronos:audio-enabled'

let ctx: AudioContext | null = null
const buffers: Partial<Record<SoundKey, AudioBuffer>> = {}
let enabled = readInitial()

function readInitial(): boolean {
  if (typeof localStorage === 'undefined') return false
  return localStorage.getItem(STORAGE_KEY) === 'true'
}

function getCtx(): AudioContext | null {
  if (ctx) return ctx
  const Ctor: typeof AudioContext | undefined =
    typeof window !== 'undefined'
      ? (window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext)
      : undefined
  if (!Ctor) return null
  ctx = new Ctor()
  return ctx
}

async function loadBuffer(key: SoundKey): Promise<AudioBuffer | null> {
  const c = getCtx()
  if (!c) return null
  if (buffers[key]) return buffers[key]!
  try {
    const res = await fetch(SOUND_FILES[key])
    const arr = await res.arrayBuffer()
    const buf = await c.decodeAudioData(arr)
    buffers[key] = buf
    return buf
  } catch {
    return null
  }
}

export function getAudioEnabled(): boolean {
  return enabled
}

export function setAudioEnabled(v: boolean): void {
  enabled = v
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, String(v))
  }
}

export function playSound(key: SoundKey, volume = 0.5): void {
  if (!enabled) return
  if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return
  const c = getCtx()
  if (!c) return
  loadBuffer(key).then((buf) => {
    if (!buf || !ctx) return
    const src = ctx.createBufferSource()
    const gain = ctx.createGain()
    gain.gain.value = volume
    src.buffer = buf
    src.connect(gain).connect(ctx.destination)
    src.start(0)
  })
}

export function preloadSounds(): Promise<void> {
  return Promise.all(
    (Object.keys(SOUND_FILES) as SoundKey[]).map(loadBuffer)
  ).then(() => undefined)
}
