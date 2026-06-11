'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { ENTITY_REGIONS, REGION_ORDER } from '@/data/entity-regions'
import { yearToDisplay } from '@/lib/year'
import type { EntityFeature } from '@/types'

export function WhatElseExisted() {
  const [open, setOpen] = useState(false)
  const entities = useTimelineStore((s) => s.currentEntities)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const year = useTimelineStore((s) => s.year)

  const grouped = useMemo(() => {
    const groups: Record<string, EntityFeature[]> = {}
    for (const e of entities) {
      const region = ENTITY_REGIONS[e.properties.slug] ?? 'Other'
      if (!groups[region]) groups[region] = []
      groups[region].push(e)
    }
    const ordered = REGION_ORDER
      .filter((r) => groups[r]?.length)
      .map((r) => ({ region: r, items: groups[r] }))
    const other = groups['Other']
    if (other?.length) ordered.push({ region: 'Other', items: other })
    return ordered
  }, [entities])

  function handleSelect(e: EntityFeature) {
    setSelectedEntity(e)
  }

  if (entities.length === 0) return null

  let displayYear = ''
  try { displayYear = yearToDisplay(year) } catch { displayYear = String(year) }

  return (
    <div className="absolute bottom-28 right-4 z-10 flex flex-col items-end gap-2">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg backdrop-blur-md border transition-all font-cinzel text-[10px] tracking-widest"
        style={{
          background: open ? 'rgba(190,148,68,0.18)' : 'rgba(16,10,4,0.82)',
          borderColor: open ? 'rgba(190,148,68,0.40)' : 'rgba(190,148,68,0.18)',
          color: open ? 'rgba(255,210,100,0.90)' : 'var(--scroll-label)',
        }}
        aria-label="What else existed at this time"
      >
        <span style={{ opacity: 0.70 }}>⊕</span>
        <span>What else existed?</span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 420, damping: 30 }}
            className="scroll-panel rounded-xl border overflow-hidden w-56"
            style={{
              backdropFilter: 'blur(24px)',
              WebkitBackdropFilter: 'blur(24px)',
              boxShadow: '0 16px 48px rgba(0,0,0,0.75)',
            }}
          >
            <div className="px-3 pt-2.5 pb-1.5 scroll-divider border-b">
              <div className="font-cinzel text-[10px] tracking-widest" style={{ color: 'var(--scroll-label)' }}>
                World in {displayYear}
              </div>
              <div className="font-im-fell italic text-[11px] mt-0.5" style={{ color: 'var(--scroll-text-faint)' }}>
                {entities.length} civilization{entities.length !== 1 ? 's' : ''} coexist
              </div>
            </div>

            <div className="max-h-72 overflow-y-auto">
              {grouped.map(({ region, items }) => (
                <div key={region}>
                  <div
                    className="px-3 py-1 font-cinzel text-[9px] tracking-widest uppercase"
                    style={{ color: 'var(--scroll-text-faint)' }}
                  >
                    {region}
                  </div>
                  {items.map((e) => (
                    <button
                      key={e.properties.slug}
                      onClick={() => handleSelect(e)}
                      className="w-full flex items-center gap-2 px-3 py-1.5 transition-colors text-left scroll-divider border-b"
                      onMouseEnter={(el) => (el.currentTarget.style.background = 'rgba(190,148,68,0.07)')}
                      onMouseLeave={(el) => (el.currentTarget.style.background = 'transparent')}
                    >
                      <div
                        className="w-2 h-2 rounded-sm flex-shrink-0"
                        style={{ backgroundColor: e.properties.color }}
                      />
                      <span
                        className="font-im-fell text-[12px] leading-none truncate"
                        style={{ color: 'var(--scroll-text)' }}
                      >
                        {e.properties.name}
                      </span>
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
