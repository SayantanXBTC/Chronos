const BASE_OPACITY = 0.28      // was 0.40 — lower fill, terrain shows through
const RISING_BOOST = 0.10      // was 0.12
const DECLINING_DIM = 0.08     // was 0.10
const RISING_THRESHOLD = 150
const DECLINING_THRESHOLD = 100

export function getMomentumOpacity(
  yearStart: number,
  yearEnd: number | null,
  currentYear: number,
): number {
  const age = currentYear - yearStart
  const isRising = age >= 0 && age < RISING_THRESHOLD
  const isDeclining = yearEnd !== null && yearEnd - currentYear < DECLINING_THRESHOLD && yearEnd > currentYear

  let opacity = BASE_OPACITY
  if (isRising) opacity += RISING_BOOST
  if (isDeclining) opacity -= DECLINING_DIM
  return Math.max(0.12, Math.min(0.50, opacity))
}

export function buildMomentumOpacityExpression(
  currentYear: number,
): unknown[] {
  const risingThreshold = currentYear - RISING_THRESHOLD
  const decliningThreshold = currentYear + DECLINING_THRESHOLD

  return [
    'case',
    ['boolean', ['feature-state', 'hover'], false], 0.52,
    ['>', ['get', 'year_start'], risingThreshold], BASE_OPACITY + RISING_BOOST,
    [
      'all',
      ['==', ['typeof', ['get', 'year_end']], 'number'],
      ['<', ['get', 'year_end'], decliningThreshold],
      ['>', ['get', 'year_end'], currentYear],
    ], BASE_OPACITY - DECLINING_DIM,
    BASE_OPACITY,
  ]
}
