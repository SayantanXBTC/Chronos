'use client'

import { useTimelineStore } from '@/store/timeline'

const SPEEDS = [
  { label: '½×', value: 0.5 },
  { label: '1×', value: 1 },
  { label: '2×', value: 2 },
  { label: '5×', value: 5 },
]

export function PlaybackControls() {
  const isPlaying = useTimelineStore((s) => s.isPlaying)
  const playSpeed = useTimelineStore((s) => s.playSpeed)
  const setPlaying = useTimelineStore((s) => s.setPlaying)
  const setPlaySpeed = useTimelineStore((s) => s.setPlaySpeed)

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setPlaying(!isPlaying)}
        aria-label={isPlaying ? 'Pause playback' : 'Play timeline'}
        className="w-8 h-8 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
      >
        {isPlaying ? '⏸' : '▶'}
      </button>
      <div className="flex gap-1" role="radiogroup" aria-label="Playback speed">
        {SPEEDS.map(({ label, value }) => (
          <button
            key={value}
            onClick={() => setPlaySpeed(value)}
            role="radio"
            aria-checked={playSpeed === value}
            className={`text-xs px-1.5 py-0.5 rounded transition-colors ${
              playSpeed === value
                ? 'bg-amber-400/80 text-black'
                : 'text-white/50 hover:text-white/80'
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
