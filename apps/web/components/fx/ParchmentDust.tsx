'use client'

import { useMemo } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { useSettingsStore } from '@/store/settings'

const COUNT = 12

interface Mote {
  r: number
  startX: number
  startY: number
  endX: number
  endY: number
  duration: number
  delay: number
  opacity: number
}

function seedMotes(): Mote[] {
  const motes: Mote[] = []
  let s = 1
  const rand = () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
  for (let i = 0; i < COUNT; i++) {
    motes.push({
      r: 1 + rand() * 2,
      startX: rand() * 100,
      startY: rand() * 100,
      endX: rand() * 100,
      endY: rand() * 100,
      duration: 30 + rand() * 30,
      delay: -rand() * 30,
      opacity: 0.04 + rand() * 0.04,
    })
  }
  return motes
}

export function ParchmentDust() {
  const systemReduced = useReducedMotion()
  const visualPolish = useSettingsStore((s) => s.visualPolish)
  const userReduced = useSettingsStore((s) => s.reducedMotion)
  const motes = useMemo(() => seedMotes(), [])

  if (!visualPolish || systemReduced || userReduced) return null

  return (
    <svg
      aria-hidden="true"
      width="100%" height="100%"
      viewBox="0 0 100 100" preserveAspectRatio="none"
      style={{
        position: 'fixed', inset: 0,
        pointerEvents: 'none', zIndex: 1,
      }}
    >
      {motes.map((m, i) => (
        <motion.circle
          key={i}
          r={m.r}
          fill="#d4a847"
          initial={{ cx: m.startX, cy: m.startY, opacity: m.opacity }}
          animate={{ cx: m.endX, cy: m.endY }}
          transition={{
            duration: m.duration,
            delay: m.delay,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'linear',
          }}
        />
      ))}
    </svg>
  )
}
