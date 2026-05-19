'use client'

import { useMemo } from 'react'
import { useShallow } from 'zustand/react/shallow'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

interface TimelineEvent { year: number; text: string }

const EVENTS: TimelineEvent[] = [
  { year: -3000, text: 'Bronze Age civilizations emerge in Mesopotamia and Egypt' },
  { year: -2500, text: 'Old Kingdom Egypt — pyramids being built' },
  { year: -1200, text: 'Late Bronze Age collapse — palace economies fall' },
  { year: -800,  text: 'Greek colonization spreads across Mediterranean' },
  { year: -500,  text: 'Classical age: Athens, Achaemenid Persia, and Confucian China' },
  { year: -323,  text: 'Death of Alexander — Hellenistic kingdoms formed' },
  { year: -221,  text: 'Qin unifies China for the first time' },
  { year: -27,   text: 'Roman Republic becomes the Roman Empire under Augustus' },
  { year: 100,   text: 'Roman Empire at peak extent under Trajan' },
  { year: 220,   text: 'Han dynasty falls — Three Kingdoms period in China' },
  { year: 285,   text: 'Roman Empire splits into Western and Eastern halves' },
  { year: 330,   text: 'Constantinople founded — Eastern Rome dominates' },
  { year: 400,   text: 'Gupta Empire golden age — classical Hindu culture flourishes' },
  { year: 476,   text: 'Western Roman Empire falls' },
  { year: 618,   text: 'Tang Dynasty founded — China enters golden age' },
  { year: 622,   text: 'Islamic civilization begins from the Arabian Peninsula' },
  { year: 750,   text: 'Abbasid Caliphate — Islamic Golden Age of science and culture' },
  { year: 800,   text: 'Charlemagne crowned Emperor of the Franks' },
  { year: 1000,  text: 'Silk Road trade at peak — goods flow East to West' },
  { year: 1206,  text: 'Genghis Khan unites Mongols — largest land empire forming' },
  { year: 1258,  text: 'Mongols sack Baghdad — Abbasid Caliphate ends' },
  { year: 1300,  text: 'Mali Empire at peak — Mansa Musa controls gold trade' },
  { year: 1368,  text: 'Ming Dynasty founded — Great Wall rebuilt' },
  { year: 1453,  text: 'Ottoman Turks take Constantinople — Byzantine Empire ends' },
  { year: 1492,  text: 'Columbus reaches Americas — age of exploration begins' },
  { year: 1526,  text: 'Mughal Empire founded in northern India' },
  { year: 1600,  text: 'European powers compete for global trade routes' },
  { year: 1750,  text: 'Industrial Revolution beginning in Britain' },
  { year: 1800,  text: 'Napoleonic wars reshape European order' },
  { year: 1850,  text: 'Age of imperialism — European empires at maximum extent' },
]

function nearestEvent(year: number): TimelineEvent | null {
  if (EVENTS.length === 0) return null
  return EVENTS.reduce((best, ev) =>
    Math.abs(ev.year - year) < Math.abs(best.year - year) ? ev : best
  )
}

function topEntities(entities: EntityFeature[]): EntityFeature[] {
  return [...entities]
    .sort((a, b) => (b.properties.importance ?? 5) - (a.properties.importance ?? 5))
    .slice(0, 3)
}

export function TemporalOverlay() {
  const year = useTimelineStore((s) => s.year)
  const currentEntities = useTimelineStore(useShallow((s) => s.currentEntities))

  const event = useMemo(() => nearestEvent(year), [year])
  const top = useMemo(() => topEntities(currentEntities), [currentEntities])

  const nearEnough = event !== null && Math.abs(event.year - year) <= 150

  if (!nearEnough && top.length === 0) return null

  return (
    <div className="absolute bottom-32 left-4 max-w-xs pointer-events-none select-none z-10">
      {event !== null && Math.abs(event.year - year) <= 150 && (
        <div className="mb-2 bg-black/60 backdrop-blur-sm text-white/70 text-xs px-3 py-2 rounded-lg border border-white/10 leading-relaxed">
          {event.text}
        </div>
      )}
      {top.length > 0 && (
        <div className="bg-black/50 backdrop-blur-sm text-white/60 text-xs px-3 py-2 rounded-lg border border-white/10">
          <div className="text-white/25 uppercase tracking-widest text-[10px] mb-1.5">World powers</div>
          {top.map((f) => (
            <div key={f.properties.slug} className="flex items-center gap-2 py-0.5">
              <div
                className="w-2 h-2 rounded-sm flex-shrink-0"
                style={{ backgroundColor: f.properties.color }}
                aria-hidden="true"
              />
              <span className="truncate">{f.properties.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
