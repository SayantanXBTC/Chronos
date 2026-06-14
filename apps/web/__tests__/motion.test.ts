import { describe, it, expect } from 'vitest'
import {
  MOTION_HUD,
  MOTION_THEATRICAL,
  MOTION_INSTANT,
  FLY_TO_DURATION_MS,
  UNFURL_DURATION_MS,
  RIPPLE_DURATION_MS,
} from '@/lib/motion'

describe('motion presets', () => {
  it('MOTION_HUD is a stiff/damped spring', () => {
    expect(MOTION_HUD.type).toBe('spring')
    expect(MOTION_HUD.stiffness).toBe(400)
    expect(MOTION_HUD.damping).toBe(30)
  })

  it('MOTION_THEATRICAL is softer with overshoot', () => {
    expect(MOTION_THEATRICAL.type).toBe('spring')
    expect(MOTION_THEATRICAL.stiffness).toBe(140)
    expect(MOTION_THEATRICAL.damping).toBe(22)
  })

  it('MOTION_INSTANT has zero duration', () => {
    expect(MOTION_INSTANT.duration).toBe(0)
  })

  it('duration constants match spec', () => {
    expect(FLY_TO_DURATION_MS).toBe(900)
    expect(UNFURL_DURATION_MS).toBe(450)
    expect(RIPPLE_DURATION_MS).toBe(250)
  })
})
