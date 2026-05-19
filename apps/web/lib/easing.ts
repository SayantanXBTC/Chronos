export const SLIDER_MIN = 0
export const SLIDER_MAX = 5025

export function clampSlider(value: number): number {
  return Math.max(SLIDER_MIN, Math.min(SLIDER_MAX, value))
}

/** Cubic ease-out: fast start, decelerates to rest */
export function easeOut(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

/** Decay a velocity over time. Returns remaining velocity after dt ms. */
export function decayVelocity(velocity: number, dt: number, friction = 0.94): number {
  return velocity * Math.pow(friction, dt / 16.67)
}
