'use client'

import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { fetchEntityDetail } from '@/lib/api'
import { yearToDisplay } from '@/lib/year'
import { LineageTree } from './LineageTree'
import { ENTITY_META } from '@/data/entity-metadata'
import { ENTITY_FACTS } from '@/data/rulers'
import type { EntityDetail } from '@/types'
import { generateJourneyStory } from '@/lib/journey'
import { useStoryStore } from '@/store/story'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'
import { Touchable } from '@/components/ui/Touchable'
import { MOTION_THEATRICAL, MOTION_HUD } from '@/lib/motion'

const CONFIDENCE_LABELS: Record<string, string> = {
  exact: 'Exact boundary',
  approximate: 'Approximate boundary',
  inferred: 'Inferred boundary',
  disputed: 'Disputed boundary',
}

const TIMELINE_MIN = -3000
const TIMELINE_MAX = 2026
const TIMELINE_SPAN = TIMELINE_MAX - TIMELINE_MIN

export function EntityPanel() {
  const entity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const currentEntities = useTimelineStore((s) => s.currentEntities)
  const year = useTimelineStore((s) => s.year)
  const [detail, setDetail] = useState<EntityDetail | null>(null)
  const startStory = useStoryStore((s) => s.startStory)
  const activeStory = useStoryStore((s) => s.activeStory)

  useEffect(() => {
    // Synchronizes `detail` with an external system (the API) keyed on
    // `entity`; the synchronous setDetail(null) calls clear stale data from
    // the previous entity before the new fetch resolves, avoiding a flash of
    // the wrong civilization's details while loading.
    if (!entity) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setDetail(null)
      return
    }
    setDetail(null)
    fetchEntityDetail(entity.properties.slug).then(setDetail).catch(() => {})
  }, [entity])

  if (!entity) return null

  const { name, type, color, confidence_type, source_name } = entity.properties
  const confidenceLabel = CONFIDENCE_LABELS[confidence_type] ?? confidence_type
  const entityMeta = ENTITY_META[entity.properties.slug] ?? null
  const entityFacts = ENTITY_FACTS[entity.properties.slug] ?? null

  const contemporaries = currentEntities.filter(
    (f) => f.properties.slug !== entity.properties.slug
  )

  const yearStart = detail?.year_start ?? entity.properties.year_start
  const yearEnd = detail?.year_end ?? entity.properties.year_end

  return (
    <motion.div
      className="absolute top-4 right-4 w-80 max-h-[calc(100vh-6rem)] overflow-y-auto"
      style={{ transformOrigin: 'top', zIndex: 11 }}
      role="complementary"
      aria-label={`Entity: ${name}`}
      initial={{ scaleY: 0, opacity: 0 }}
      animate={{ scaleY: 1, opacity: 1 }}
      exit={{ scaleY: 0, opacity: 0 }}
      transition={MOTION_THEATRICAL}
    >
      <OrnamentFrame density="full" className="text-[14px]">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ ...MOTION_HUD, delay: 0.08 }}
        >
          <Touchable
            onClick={() => setSelectedEntity(null)}
            soundKey="close"
            ripple={false}
            ariaLabel="Close entity panel"
            className="absolute top-3 right-4 text-[20px] leading-none"
          >
            <span style={{ color: 'var(--parchment-ink-muted)' }}>×</span>
          </Touchable>

          <div className="flex items-center gap-3 mb-3 pr-6">
            <div className="w-4 h-4 rounded-sm flex-shrink-0 border" style={{ backgroundColor: color, borderColor: 'var(--parchment-border)' }} aria-hidden="true" />
            <h2 className="leading-tight" style={{ fontFamily: 'var(--font-cinzel)', fontWeight: 700, fontSize: 20, letterSpacing: '0.04em', color: 'var(--parchment-ink)' }}>{name}</h2>
          </div>

          <dl className="space-y-1" style={{ fontFamily: 'var(--font-garamond)', fontSize: 14, color: 'var(--parchment-ink-soft)' }}>
            <div className="flex gap-2">
              <dt className="w-16 flex-shrink-0" style={{ color: 'var(--parchment-label)', fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase' }}>Type</dt>
              <dd className="capitalize">{type}</dd>
            </div>
            {yearStart !== undefined && (
              <div className="flex gap-2">
                <dt className="w-16 flex-shrink-0" style={{ color: 'var(--parchment-label)', fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase' }}>Dates</dt>
                <dd>{yearToDisplay(yearStart)} – {yearEnd !== null && yearEnd !== undefined ? yearToDisplay(yearEnd) : 'present'}</dd>
              </div>
            )}
            <div className="flex gap-2">
              <dt className="w-16 flex-shrink-0" style={{ color: 'var(--parchment-label)', fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase' }}>Boundary</dt>
              <dd className="text-xs leading-relaxed" style={{ color: 'var(--parchment-ink-muted)' }}>{confidenceLabel}</dd>
            </div>
            {source_name && (
              <div className="flex gap-2">
                <dt className="w-16 flex-shrink-0" style={{ color: 'var(--parchment-label)', fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase' }}>Source</dt>
                <dd className="text-xs leading-relaxed" style={{ color: 'var(--parchment-ink-muted)' }}>{source_name}</dd>
              </div>
            )}
          </dl>

          {detail && (
            <figure className="mt-3 pt-3" style={{ borderTop: '1px solid var(--parchment-border)' }} aria-label="Civilization lifespan">
              <div className="text-xs mb-1.5" style={{ color: 'var(--parchment-label)', fontFamily: 'var(--font-cinzel)', letterSpacing: '0.2em', textTransform: 'uppercase' }}>Lifespan</div>
              <div className="relative h-2 rounded-full overflow-visible" style={{ background: 'rgba(58,36,16,0.18)' }}>
                <div className="absolute top-0 h-full rounded-full" style={{
                  backgroundColor: color,
                  left: `${Math.max(0, Math.min(100, ((detail.year_start - TIMELINE_MIN) / TIMELINE_SPAN) * 100))}%`,
                  right: `${Math.max(0, Math.min(100, ((TIMELINE_MAX - (detail.year_end ?? TIMELINE_MAX)) / TIMELINE_SPAN) * 100))}%`,
                  opacity: 0.8,
                }} />
                <div className="absolute top-[-2px] w-0.5 h-3 rounded-full" style={{ background: 'var(--parchment-drop)', left: `${Math.max(0, Math.min(100, ((year - TIMELINE_MIN) / TIMELINE_SPAN) * 100))}%` }} aria-hidden="true" />
              </div>
              <div className="flex justify-between text-[10px] mt-1" style={{ color: 'var(--parchment-ink-muted)', fontFamily: 'var(--font-cinzel)' }}>
                <span>3000 BCE</span>
                <span>2026 CE</span>
              </div>
              {entityMeta?.peak_label && (
                <div className="mt-1.5 text-[11px] flex items-center gap-1" style={{ color: 'var(--parchment-drop)' }}>
                  <span>★</span>
                  <span>{entityMeta.peak_label}</span>
                </div>
              )}
            </figure>
          )}

          {entityFacts && (
            <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--parchment-border)', fontFamily: 'var(--font-garamond)' }}>
              {entityFacts.rulers.length > 0 && (
                <>
                  <h3 style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--parchment-label)' }} className="mb-2">
                    Notable Rulers
                  </h3>
                  <ul className="space-y-1 mb-3">
                    {entityFacts.rulers.map((r) => (
                      <li key={r.name} className="flex justify-between gap-2 text-sm" style={{ color: 'var(--parchment-ink-soft)' }}>
                        <span className="truncate">{r.title} {r.name}</span>
                        <span className="text-xs flex-shrink-0" style={{ color: 'var(--parchment-ink-muted)' }}>{r.years}</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
              <h3 style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--parchment-label)' }} className="mb-2">
                Facts
              </h3>
              <ul className="space-y-1.5">
                {entityFacts.facts.map((fact, i) => (
                  <li key={i} className="text-xs leading-relaxed flex gap-1.5" style={{ color: 'var(--parchment-ink-muted)' }}>
                    <span aria-hidden="true">•</span>
                    <span>{fact}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {detail && (
            <LineageTree predecessors={detail.lineage.predecessors} successors={detail.lineage.successors} />
          )}

          {detail && !activeStory && (
            <Touchable
              onClick={() => startStory(generateJourneyStory(detail))}
              soundKey="open"
              className="w-full mt-3 mb-1 py-2 rounded-lg"
              ariaLabel="Begin Journey"
            >
              <span style={{ fontFamily: 'var(--font-cinzel)', fontSize: 11, letterSpacing: '0.25em', color: 'var(--parchment-drop)' }}>
                ▶ BEGIN JOURNEY
              </span>
            </Touchable>
          )}

          {contemporaries.length > 0 && (
            <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--parchment-border)' }}>
              <h3 style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--parchment-label)' }} className="mb-2">
                Contemporaries in {yearToDisplay(year)}
              </h3>
              <div className="space-y-1">
                {contemporaries.slice(0, 8).map((f) => (
                  <div key={f.properties.slug} className="flex items-center gap-2 text-sm">
                    <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: f.properties.color }} aria-hidden="true" />
                    <span className="truncate" style={{ color: 'var(--parchment-ink-soft)' }}>{f.properties.name}</span>
                  </div>
                ))}
                {contemporaries.length > 8 && (
                  <div className="text-xs" style={{ color: 'var(--parchment-ink-muted)' }}>+{contemporaries.length - 8} more</div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </OrnamentFrame>
    </motion.div>
  )
}
