'use client'

import { useMemo } from 'react'
import { useShallow } from 'zustand/react/shallow'
import { motion, AnimatePresence } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

export interface TimelineEvent { year: number; text: string }

export const EVENTS: TimelineEvent[] = [
  { year: -3000, text: 'Bronze Age civilizations emerge in Mesopotamia and Egypt' },
  { year: -2800, text: 'Early Dynastic Period in Sumer — city-states compete for power' },
  { year: -2500, text: 'Old Kingdom Egypt — pyramids of Giza under construction' },
  { year: -2300, text: 'Akkadian Empire — first multi-ethnic empire in history' },
  { year: -2000, text: 'Middle Kingdom Egypt flourishes; Minoan civilization on Crete' },
  { year: -1800, text: 'Code of Hammurabi established in Babylon' },
  { year: -1600, text: 'Hittite Empire rises; New Kingdom Egypt begins' },
  { year: -1400, text: 'Mycenaean Greece and Late Bronze Age palace economy peak' },
  { year: -1200, text: 'Late Bronze Age collapse — palace economies fall across the Mediterranean' },
  { year: -1000, text: 'Iron Age spreads; Phoenician trade networks expand across sea' },
  { year: -900,  text: 'Neo-Assyrian Empire dominates Near East with military power' },
  { year: -800,  text: 'Greek city-states emerge; colonization spreads across Mediterranean' },
  { year: -750,  text: 'Homer composes the Iliad and Odyssey; Rome traditionally founded' },
  { year: -600,  text: 'Lydian coinage invented; Zoroastrianism spreads in Persia' },
  { year: -550,  text: 'Cyrus the Great founds Achaemenid Persia — first world empire' },
  { year: -500,  text: 'Classical age: Athens, Achaemenid Persia, and Confucian China simultaneously' },
  { year: -480,  text: 'Greco-Persian Wars — Battle of Thermopylae and Salamis' },
  { year: -450,  text: 'Athenian democracy at its height; Parthenon under construction' },
  { year: -400,  text: 'Warring States period in China; Plato founds the Academy in Athens' },
  { year: -356,  text: 'Alexander the Great born; Philip II transforms Macedon' },
  { year: -323,  text: 'Death of Alexander — Hellenistic kingdoms divide his empire' },
  { year: -300,  text: 'Maurya Empire unites India; Ptolemaic Egypt at cultural height' },
  { year: -264,  text: 'First Punic War — Rome and Carthage clash for Mediterranean supremacy' },
  { year: -221,  text: 'Qin Shi Huang unifies China for the first time' },
  { year: -200,  text: 'Han Dynasty consolidates China; Silk Road begins to form' },
  { year: -146,  text: 'Rome destroys Carthage and Corinth — dominates Mediterranean' },
  { year: -60,   text: 'Julius Caesar, Pompey, and Crassus form First Triumvirate' },
  { year: -27,   text: 'Roman Republic becomes the Roman Empire under Augustus' },
  { year: 100,   text: 'Roman Empire at peak extent under Trajan — from Scotland to Mesopotamia' },
  { year: 200,   text: 'Kushan Empire peaks; Buddhism spreads across Central Asia' },
  { year: 220,   text: 'Han dynasty falls — Three Kingdoms period fractures China' },
  { year: 285,   text: 'Roman Empire splits into Western and Eastern administrative halves' },
  { year: 313,   text: 'Constantine legalizes Christianity — Roman Empire transforms' },
  { year: 330,   text: 'Constantinople founded as new capital of Eastern Rome' },
  { year: 370,   text: 'Huns push westward — migrations destabilize Western Rome' },
  { year: 400,   text: 'Gupta Empire golden age — mathematics, astronomy, classical Sanskrit' },
  { year: 476,   text: 'Western Roman Empire falls — medieval period begins in Europe' },
  { year: 500,   text: 'Axum Empire controls Red Sea trade; Maya cities flourish in Mesoamerica' },
  { year: 550,   text: 'Justinian I reconquers much of the old Western Empire temporarily' },
  { year: 618,   text: 'Tang Dynasty founded — China enters its golden age' },
  { year: 622,   text: 'Hijra of Muhammad — Islamic civilization begins its expansion' },
  { year: 711,   text: 'Islamic forces cross into Iberia; Tang China reaches Central Asia' },
  { year: 750,   text: 'Abbasid Caliphate — Islamic Golden Age of science and philosophy' },
  { year: 800,   text: 'Charlemagne crowned Emperor — Carolingian Renaissance in Europe' },
  { year: 850,   text: 'Viking Age at its height — Norsemen reach from Russia to Normandy' },
  { year: 960,   text: 'Song Dynasty begins — gunpowder, printing press, paper money in China' },
  { year: 1000,  text: 'Silk Road trade at peak — goods and ideas flow from China to Rome' },
  { year: 1066,  text: 'Norman Conquest of England; Seljuk Turks defeat Byzantines at Manzikert' },
  { year: 1099,  text: 'First Crusade captures Jerusalem; crusader states established' },
  { year: 1200,  text: 'High Medieval period — Gothic cathedrals, universities, feudal kingdoms' },
  { year: 1206,  text: 'Genghis Khan unites Mongols — the largest land empire begins forming' },
  { year: 1258,  text: 'Mongols sack Baghdad — Abbasid Caliphate ends, 500 years of Islamic rule' },
  { year: 1300,  text: 'Mali Empire at peak — Mansa Musa controls half the world\'s gold' },
  { year: 1347,  text: 'Black Death reaches Europe — one third of the population dies' },
  { year: 1368,  text: 'Ming Dynasty founded — Great Wall rebuilt, Zheng He voyages begin' },
  { year: 1400,  text: 'Renaissance flourishes in Italy; Ottoman expansion accelerates' },
  { year: 1453,  text: 'Ottomans take Constantinople — Byzantine Empire ends after 1100 years' },
  { year: 1492,  text: 'Columbus reaches Americas — beginning of the Columbian Exchange' },
  { year: 1526,  text: 'Mughal Empire founded at Panipat — India enters Mughal era' },
  { year: 1550,  text: 'Spanish Empire controls Americas; Portuguese establish Asian trade routes' },
  { year: 1600,  text: 'European powers compete for global trade — Dutch, English, French VOC' },
  { year: 1648,  text: 'Peace of Westphalia — modern nation-state system established in Europe' },
  { year: 1700,  text: 'Qing Dynasty at height; Mughal Empire begins to fragment' },
  { year: 1750,  text: 'Industrial Revolution beginning in Britain — coal, iron, steam' },
  { year: 1776,  text: 'American independence; Enlightenment reshapes political philosophy' },
  { year: 1800,  text: 'Napoleonic wars reshape European order and spread revolutionary ideas' },
  { year: 1850,  text: 'Age of imperialism — European empires reach maximum territorial extent' },
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
      <AnimatePresence mode="wait">
        {event !== null && Math.abs(event.year - year) <= 150 && (
          <motion.div
            key={event.year}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.25 }}
            className="mb-2 bg-black/60 backdrop-blur-sm text-white/70 text-xs px-3 py-2 rounded-lg border border-white/10 leading-relaxed"
          >
            {event.text}
          </motion.div>
        )}
      </AnimatePresence>
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
