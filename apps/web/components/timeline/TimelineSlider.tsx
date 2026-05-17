// apps/web/components/timeline/TimelineSlider.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'
import { yearToDisplay, sliderToYear, yearToSlider } from '@/lib/year'

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
          min={0}
          max={999}
          step={1}
          value={yearToSlider(year)}
          onChange={handleChange}
          aria-label="Timeline year"
          className="w-full h-1.5 cursor-pointer accent-amber-400 rounded-full"
        />
        <div className="flex justify-between text-white/50 text-xs mt-2 font-mono select-none">
          <span>500 BCE</span>
          <span>1 BCE / 1 CE</span>
          <span>500 CE</span>
        </div>
      </div>
    </div>
  )
}
