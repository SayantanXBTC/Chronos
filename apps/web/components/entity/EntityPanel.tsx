'use client'

import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { fetchEntityDetail } from '@/lib/api'
import { yearToDisplay } from '@/lib/year'
import { LineageTree } from './LineageTree'
import { ENTITY_META } from '@/data/entity-metadata'
import type { EntityDetail } from '@/types'
import { generateJourneyStory } from '@/lib/journey'
import { useStoryStore } from '@/store/story'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'
import { Touchable } from '@/components/ui/Touchable'
import { AAA_POLISH } from '@/lib/flags'
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
    if (!entity) {
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

  const contemporaries = currentEntities.filter(
    (f) => f.properties.slug !== entity.properties.slug
  )

  const yearStart = detail?.year_start ?? entity.properties.year_start
  const yearEnd = detail?.year_end ?? entity.properties.year_end

  if (!AAA_POLISH) {
    return (
      <motion.div
        className="absolute top-4 right-4 w-80 max-h-[calc(100vh-6rem)] overflow-y-auto bg-black/85 backdrop-blur-md text-white rounded-xl p-5 border border-white/10 shadow-2xl"
        role="complementary"
        aria-label={`Entity: ${name}`}
        initial={{ opacity: 0, x: 24 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 24 }}
        transition={{ duration: 0.22, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <button
          onClick={() => setSelectedEntity(null)}
          className="absolute top-3 right-4 text-white/40 hover:text-white text-xl leading-none transition-colors"
          aria-label="Close entity panel"
        >
          ×
        </button>
        <div className="flex items-center gap-3 mb-3 pr-6">
          <div
            className="w-4 h-4 rounded-sm flex-shrink-0 border border-white/20"
            style={{ backgroundColor: color }}
            aria-hidden="true"
          />
          <h2 className="font-bold text-lg leading-tight">{name}</h2>
        </div>
        <dl className="space-y-1 text-sm">
          <div className="flex gap-2">
            <dt className="text-white/40 w-16 flex-shrink-0">Type</dt>
            <dd className="text-white/80 capitalize">{type}</dd>
          </div>
          {yearStart !== undefined && (
            <div className="flex gap-2">
              <dt className="text-white/40 w-16 flex-shrink-0">Dates</dt>
              <dd className="text-white/80">
                {yearToDisplay(yearStart)} – {yearEnd !== null && yearEnd !== undefined ? yearToDisplay(yearEnd) : 'present'}
              </dd>
            </div>
          )}
          <div className="flex gap-2">
            <dt className="text-white/40 w-16 flex-shrink-0">Boundary</dt>
            <dd className="text-white/60 text-xs leading-relaxed">{confidenceLabel}</dd>
          </div>
          {source_name && (
            <div className="flex gap-2">
              <dt className="text-white/40 w-16 flex-shrink-0">Source</dt>
              <dd className="text-white/50 text-xs leading-relaxed">{source_name}</dd>
            </div>
          )}
        </dl>
        {detail && (
          <figure className="mt-3 pt-3 border-t border-white/10" aria-label="Civilization lifespan">
            <div className="text-white/30 text-xs mb-1.5">Civilization lifespan</div>
            <div className="relative h-2 bg-white/10 rounded-full overflow-visible">
              <div
                className="absolute top-0 h-full rounded-full"
                style={{
                  backgroundColor: color,
                  left: `${Math.max(0, Math.min(100, ((detail.year_start - TIMELINE_MIN) / TIMELINE_SPAN) * 100))}%`,
                  right: `${Math.max(0, Math.min(100, ((TIMELINE_MAX - (detail.year_end ?? TIMELINE_MAX)) / TIMELINE_SPAN) * 100))}%`,
                  opacity: 0.65,
                }}
              />
              <div
                className="absolute top-[-2px] w-0.5 h-3 bg-amber-400/80 rounded-full"
                style={{ left: `${Math.max(0, Math.min(100, ((year - TIMELINE_MIN) / TIMELINE_SPAN) * 100))}%` }}
                aria-hidden="true"
              />
            </div>
            <div className="flex justify-between text-white/20 text-[10px] mt-1 font-mono">
              <span>3000 BCE</span>
              <span>2026 CE</span>
            </div>
            {entityMeta?.peak_label && (
              <div className="mt-1.5 text-amber-300/50 text-[11px] flex items-center gap-1">
                <span className="text-amber-400/60">★</span>
                <span>{entityMeta.peak_label}</span>
              </div>
            )}
          </figure>
        )}
        {detail && (
          <LineageTree
            predecessors={detail.lineage.predecessors}
            successors={detail.lineage.successors}
          />
        )}
        {detail && !activeStory && (
          <button
            onClick={() => startStory(generateJourneyStory(detail))}
            className="w-full mt-3 mb-1 py-2 rounded-lg font-cinzel text-[11px] tracking-widest transition-colors"
            style={{
              background: `linear-gradient(135deg, ${color}22, ${color}11)`,
              border: `1px solid ${color}40`,
              color: `${color}cc`,
            }}
          >
            ▶ Begin Journey
          </button>
        )}
        {contemporaries.length > 0 && (
          <div className="mt-3 pt-3 border-t border-white/10">
            <h3 className="text-white/40 text-xs uppercase tracking-widest mb-2">
              Contemporaries in {yearToDisplay(year)}
            </h3>
            <div className="space-y-1">
              {contemporaries.slice(0, 8).map((f) => (
                <div key={f.properties.slug} className="flex items-center gap-2 text-sm">
                  <div
                    className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: f.properties.color }}
                    aria-hidden="true"
                  />
                  <span className="text-white/70 truncate">{f.properties.name}</span>
                </div>
              ))}
              {contemporaries.length > 8 && (
                <div className="text-white/30 text-xs">+{contemporaries.length - 8} more</div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    )
  }

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
