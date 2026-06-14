'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { ENTITY_REGIONS, REGION_ORDER } from '@/data/entity-regions'
import { yearToDisplay } from '@/lib/year'
import type { EntityFeature } from '@/types'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'
import { Touchable } from '@/components/ui/Touchable'
import { AAA_POLISH } from '@/lib/flags'
import { MOTION_HUD } from '@/lib/motion'

export function WhatElseExisted() {
  const [open, setOpen] = useState(false)
  const entities = useTimelineStore((s) => s.currentEntities)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const setSelectionSource = useTimelineStore((s) => s.setSelectionSource)
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
    setSelectionSource('panel')
    setSelectedEntity(e)
  }

  if (entities.length === 0) return null
  if (!AAA_POLISH) return null

  let displayYear = ''
  try { displayYear = yearToDisplay(year) } catch { displayYear = String(year) }

  return (
    <div className="absolute bottom-28 right-4 z-10 flex flex-col items-end gap-2">
      <Touchable
        onClick={() => setOpen((v) => !v)}
        soundKey={open ? 'close' : 'open'}
        ariaLabel="What else existed at this time"
        className="flex items-center gap-2 px-3 py-1.5"
      >
        <span style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', color: 'var(--parchment-ink)' }}>
          ⊕ What else existed?
        </span>
      </Touchable>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.97 }}
            transition={MOTION_HUD}
            className="overflow-hidden w-56"
          >
            <OrnamentFrame density="mid">
              <div className="pb-1.5 mb-1" style={{ borderBottom: '1px solid var(--parchment-border)' }}>
                <div style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', color: 'var(--parchment-label)' }}>
                  World in {displayYear}
                </div>
                <div style={{ fontFamily: 'var(--font-garamond)', fontStyle: 'italic', fontSize: 11, color: 'var(--parchment-ink-muted)' }}>
                  {entities.length} civilization{entities.length !== 1 ? 's' : ''} coexist
                </div>
              </div>

              <div className="max-h-72 overflow-y-auto -mx-2">
                {grouped.map(({ region, items }) => (
                  <div key={region}>
                    <div className="px-2 py-1" style={{ fontFamily: 'var(--font-cinzel)', fontSize: 9, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--parchment-ink-muted)' }}>
                      {region}
                    </div>
                    {items.map((e) => (
                      <Touchable
                        key={e.properties.slug}
                        onClick={() => handleSelect(e)}
                        soundKey="click"
                        ripple={false}
                        ariaLabel={e.properties.name}
                        className="w-full flex items-center gap-2 px-2 py-1.5 text-left"
                      >
                        <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{ backgroundColor: e.properties.color }} />
                        <span className="truncate" style={{ fontFamily: 'var(--font-garamond)', fontSize: 12, color: 'var(--parchment-ink-soft)' }}>
                          {e.properties.name}
                        </span>
                      </Touchable>
                    ))}
                  </div>
                ))}
              </div>
            </OrnamentFrame>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
