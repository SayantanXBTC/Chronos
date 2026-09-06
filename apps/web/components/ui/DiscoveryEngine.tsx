'use client'

import { useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { useStoryStore } from '@/store/story'
import { computeDiscoveryPrompts } from '@/lib/discovery'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'
import { Touchable } from '@/components/ui/Touchable'
import { AAA_POLISH } from '@/lib/flags'
import { MOTION_HUD } from '@/lib/motion'

export function DiscoveryEngine() {
  const year = useTimelineStore((s) => s.year)
  const entities = useTimelineStore((s) => s.currentEntities)
  const selectedEntity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const setSelectionSource = useTimelineStore((s) => s.setSelectionSource)
  const activeStory = useStoryStore((s) => s.activeStory)

  const prompts = useMemo(
    () => computeDiscoveryPrompts(entities, year),
    [entities, year]
  )

  const handlePrompt = useCallback(
    (slug: string) => {
      const entity = entities.find((e) => e.properties.slug === slug)
      if (entity) {
        setSelectionSource('panel')
        setSelectedEntity(entity)
      }
    },
    [entities, setSelectedEntity, setSelectionSource]
  )

  if (selectedEntity || activeStory || prompts.length === 0) return null
  if (!AAA_POLISH) return null

  return (
    <div className="absolute bottom-56 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-1.5 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {prompts.map((prompt, i) => (
          <motion.div
            key={prompt.id}
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1 - i * 0.18, y: 0, scale: 1 - i * 0.015 }}
            exit={{ opacity: 0, y: -6, scale: 0.95 }}
            transition={{ ...MOTION_HUD, delay: i * 0.05 }}
            className="pointer-events-auto"
            style={{ minWidth: 240 }}
          >
            <OrnamentFrame density="mid">
              <Touchable
                onClick={() => handlePrompt(prompt.slug)}
                soundKey="click"
                className="w-full flex flex-col items-center"
                ariaLabel={prompt.cta}
              >
                <span style={{ fontFamily: 'var(--font-garamond)', fontStyle: 'italic', fontSize: 11, color: 'var(--parchment-ink-muted)' }}>
                  {prompt.label}
                </span>
                <span style={{ fontFamily: 'var(--font-cinzel)', fontSize: 11, letterSpacing: '0.1em', color: 'var(--parchment-drop)' }}>
                  {prompt.cta}
                </span>
              </Touchable>
            </OrnamentFrame>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
