'use client'

import { useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import { useStoryStore } from '@/store/story'
import { computeDiscoveryPrompts } from '@/lib/discovery'

export function DiscoveryEngine() {
  const year = useTimelineStore((s) => s.year)
  const entities = useTimelineStore((s) => s.currentEntities)
  const selectedEntity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const activeStory = useStoryStore((s) => s.activeStory)

  const prompts = useMemo(
    () => computeDiscoveryPrompts(entities, year),
    [entities, year]
  )

  const handlePrompt = useCallback(
    (slug: string) => {
      const entity = entities.find((e) => e.properties.slug === slug)
      if (entity) setSelectedEntity(entity)
    },
    [entities, setSelectedEntity]
  )

  // Hide when entity selected, story running, or no prompts
  if (selectedEntity || activeStory || prompts.length === 0) return null

  return (
    <div className="absolute bottom-28 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-1.5 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {prompts.map((prompt, i) => (
          <motion.button
            key={prompt.id}
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1 - i * 0.2, y: 0, scale: 1 - i * 0.015 }}
            exit={{ opacity: 0, y: -6, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 380, damping: 28, delay: i * 0.05 }}
            onClick={() => handlePrompt(prompt.slug)}
            className="pointer-events-auto flex flex-col items-center px-4 py-2 rounded-xl backdrop-blur-md border transition-all"
            style={{
              background: 'rgba(16,10,4,0.82)',
              borderColor: 'rgba(190,148,68,0.18)',
              boxShadow: '0 8px 28px rgba(0,0,0,0.60)',
              minWidth: '240px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'rgba(190,148,68,0.40)'
              e.currentTarget.style.background = 'rgba(30,18,6,0.90)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(190,148,68,0.18)'
              e.currentTarget.style.background = 'rgba(16,10,4,0.82)'
            }}
          >
            <span
              className="font-im-fell italic text-[11px] mb-0.5"
              style={{ color: 'var(--scroll-text-dim)' }}
            >
              {prompt.label}
            </span>
            <span
              className="font-cinzel text-[11px] tracking-wide"
              style={{ color: 'rgba(255,210,100,0.85)' }}
            >
              {prompt.cta}
            </span>
          </motion.button>
        ))}
      </AnimatePresence>
    </div>
  )
}
