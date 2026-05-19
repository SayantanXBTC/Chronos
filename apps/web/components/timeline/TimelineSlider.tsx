'use client'

import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { useTimelineStore } from '@/store/timeline'
import {
  yearToDisplay,
  sliderToYear,
  yearToSlider,
  ERA_MARKERS,
  snapToPrevSnapshot,
  snapToNextSnapshot,
  SNAPSHOT_YEARS,
} from '@/lib/year'
import { PlaybackControls } from './PlaybackControls'

const SLIDER_MIN = 0
const SLIDER_MAX = 5025

const YEAR_MIN = SNAPSHOT_YEARS[0]
const YEAR_MAX = SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]

function eraPercent(year: number): number {
  return ((yearToSlider(year) - SLIDER_MIN) / (SLIDER_MAX - SLIDER_MIN)) * 100
}

export function TimelineSlider() {
  const year = useTimelineStore((s) => s.year)
  const setYear = useTimelineStore((s) => s.setYear)
  const isPlaying = useTimelineStore((s) => s.isPlaying)
  const playSpeed = useTimelineStore((s) => s.playSpeed)
  const [editing, setEditing] = useState(false)
  const [editValue, setEditValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!isPlaying) return
    const msPerStep = Math.round(1000 / playSpeed)
    const id = setInterval(() => {
      const store = useTimelineStore.getState()
      const next = snapToNextSnapshot(store.year)
      if (next === store.year) {
        store.setPlaying(false)
        return
      }
      store.setYear(next)
    }, msPerStep)
    return () => clearInterval(id)
  }, [isPlaying, playSpeed])

  function handleSliderChange(e: React.ChangeEvent<HTMLInputElement>) {
    setYear(sliderToYear(Number(e.target.value)))
  }

  function handleSliderKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      setYear(snapToNextSnapshot(year))
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      setYear(snapToPrevSnapshot(year))
    }
  }

  function startEditing() {
    setEditValue(year < 0 ? `${Math.abs(year)} BCE` : String(year))
    setEditing(true)
  }

  useEffect(() => {
    if (editing && inputRef.current) inputRef.current.focus()
  }, [editing])

  function commitEdit() {
    const raw = parseInt(editValue, 10)
    if (!isNaN(raw)) {
      const signed = editValue.toLowerCase().includes('b') ? -raw : raw
      const clamped = Math.max(YEAR_MIN, Math.min(YEAR_MAX, signed === 0 ? 1 : signed))
      setYear(clamped)
    }
    setEditing(false)
  }

  function handleEditKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') commitEdit()
    if (e.key === 'Escape') setEditing(false)
  }

  return (
    <div className="absolute bottom-0 left-0 right-0 px-8 pb-6 pt-12 bg-gradient-to-t from-black/90 to-transparent pointer-events-none select-none">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        {/* Year display / edit */}
        <div className="text-center mb-3">
          {editing ? (
            <input
              ref={inputRef}
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={commitEdit}
              onKeyDown={handleEditKeyDown}
              className="bg-transparent border-b border-amber-400 text-white text-3xl font-bold text-center w-40 outline-none tracking-widest"
              aria-label="Enter year"
            />
          ) : (
            <AnimatePresence mode="wait">
              <motion.button
                key={yearToDisplay(year)}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.18, ease: 'easeOut' }}
                onClick={startEditing}
                className="text-white text-3xl font-bold tracking-widest drop-shadow-lg hover:text-amber-300 transition-colors"
                style={{ fontFamily: 'var(--font-cinzel), serif' }}
                aria-label={`Current year: ${yearToDisplay(year)}. Click to jump to year.`}
                title="Click to jump to year"
              >
                {yearToDisplay(year)}
              </motion.button>
            </AnimatePresence>
          )}
        </div>

        {/* Era markers row */}
        <div className="relative h-5 mb-1">
          {ERA_MARKERS.map((era) => (
            <button
              key={era.label}
              onClick={() => setYear(snapToNextSnapshot(era.year))}
              style={{ left: `${eraPercent(era.year)}%` }}
              className="absolute -translate-x-1/2 text-white/35 text-xs hover:text-amber-300 transition-colors leading-none"
              title={`Jump to ${era.label} era`}
            >
              {era.label}
            </button>
          ))}
        </div>

        {/* Playback controls */}
        <div className="flex justify-center mb-2">
          <PlaybackControls />
        </div>

        {/* Slider */}
        <div className="relative">
          <input
            type="range"
            min={SLIDER_MIN}
            max={SLIDER_MAX}
            step={1}
            value={yearToSlider(year)}
            onChange={handleSliderChange}
            onKeyDown={handleSliderKeyDown}
            aria-label="Timeline year"
            className="w-full h-1.5 cursor-pointer accent-amber-400 rounded-full"
          />
        </div>

        {/* Min/max labels */}
        <div className="flex justify-between text-white/40 text-xs mt-1.5 font-mono">
          <span>3000 BCE</span>
          <span>1 BCE / 1 CE</span>
          <span>2026 CE</span>
        </div>
      </div>
    </div>
  )
}
