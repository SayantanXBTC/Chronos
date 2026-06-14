import type { Transition } from 'motion/react'

export const MOTION_HUD: Transition = {
  type: 'spring',
  stiffness: 400,
  damping: 30,
  mass: 0.6,
}

export const MOTION_THEATRICAL: Transition = {
  type: 'spring',
  stiffness: 140,
  damping: 22,
  mass: 1,
}

export const MOTION_INSTANT: Transition = { duration: 0 }

export const FLY_TO_DURATION_MS = 900
export const UNFURL_DURATION_MS = 450
export const RIPPLE_DURATION_MS = 250
