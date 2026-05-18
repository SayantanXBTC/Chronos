// apps/web/components/timeline/TimelineSlider.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'
import { yearToDisplay, sliderToYear, yearToSlider } from '@/lib/year'

// Slider covers -3000 to 2026 CE (skipping 0): 3000 BCE positions + 2026 CE positions = 5026 steps
const SLIDER_MIN = 0
const SLIDER_MAX = 5025

export function TimelineSlider() {
  const year = useTimelineStore((s) => s.year)
  const setYear = useTimelineStore((s) => s.setYear)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setYear(sliderToYear(Number(e.target.value)))
  }

  return (
    <div className="absolute bottom-0 left-0 right-0 px-8 pb-8 pt-12 bg-gradient-to-t from-black/85 to-transparent pointer-events-none">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        <div className="text-center text-white text-3xl font-bold mb-4 tracking-widest drop-shadow-lg">
          {yearToDisplay(year)}
        </div>
        <input
          type="range"
          min={SLIDER_MIN}
          max={SLIDER_MAX}
          step={1}
          value={yearToSlider(year)}
          onChange={handleChange}
          aria-label="Timeline year"
          className="w-full h-1.5 cursor-pointer accent-amber-400 rounded-full"
        />
        <div className="flex justify-between text-white/50 text-xs mt-2 font-mono select-none">
          <span>3000 BCE</span>
          <span>1 BCE / 1 CE</span>
          <span>2026 CE</span>
        </div>
      </div>
    </div>
  )
}
