'use client'

import { useState, useRef, type ReactNode, type MouseEvent } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { MOTION_HUD, RIPPLE_DURATION_MS } from '@/lib/motion'
import { playSound, type SoundKey } from '@/lib/audio'

interface TouchableProps {
  children: ReactNode
  onClick?: () => void
  className?: string
  disabled?: boolean
  ripple?: boolean
  soundKey?: SoundKey
  ariaLabel?: string
}

interface Ripple {
  id: number
  x: number
  y: number
}

export function Touchable({
  children,
  onClick,
  className = '',
  disabled = false,
  ripple = true,
  soundKey = 'click',
  ariaLabel,
}: TouchableProps) {
  const [ripples, setRipples] = useState<Ripple[]>([])
  const nextId = useRef(0)

  function handleClick(e: MouseEvent<HTMLButtonElement>) {
    if (disabled) return
    playSound(soundKey)
    if (ripple) {
      const rect = e.currentTarget.getBoundingClientRect()
      const id = nextId.current++
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      setRipples((prev) => [...prev, { id, x, y }])
      setTimeout(() => {
        setRipples((prev) => prev.filter((r) => r.id !== id))
      }, RIPPLE_DURATION_MS + 50)
    }
    onClick?.()
  }

  return (
    <motion.button
      type="button"
      aria-label={ariaLabel}
      disabled={disabled}
      className={className}
      style={{ position: 'relative', overflow: 'hidden' }}
      whileHover={disabled ? undefined : { scale: 1.02 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      transition={MOTION_HUD}
      onClick={handleClick}
    >
      {children}
      <AnimatePresence>
        {ripples.map((r) => (
          <motion.span
            key={r.id}
            data-ripple
            initial={{ scale: 0, opacity: 0.4 }}
            animate={{ scale: 4, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: RIPPLE_DURATION_MS / 1000 }}
            style={{
              position: 'absolute',
              left: r.x,
              top: r.y,
              width: 24,
              height: 24,
              marginLeft: -12,
              marginTop: -12,
              borderRadius: '50%',
              background: 'rgba(139,26,10,0.55)',
              pointerEvents: 'none',
            }}
          />
        ))}
      </AnimatePresence>
    </motion.button>
  )
}
