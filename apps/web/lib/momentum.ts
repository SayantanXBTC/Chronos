const BASE_OPACITY = 0.40
const RISING_BOOST = 0.12
const DECLINING_DIM = 0.10
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
  return Math.max(0.15, Math.min(0.60, opacity))
}

export function buildMomentumOpacityExpression(
  currentYear: number,
): unknown[] {
  const risingThreshold = currentYear - RISING_THRESHOLD
  const decliningThreshold = currentYear + DECLINING_THRESHOLD

  // Hover-aware outer wrapper + momentum inner expression
  return [
    'case',
    // Hover = always bright (feature-state)
    ['boolean', ['feature-state', 'hover'], false], 0.65,
    // Rising (born recently)
    ['>', ['get', 'year_start'], risingThreshold], BASE_OPACITY + RISING_BOOST,
    // Declining (year_end is a number AND ends within threshold AND after currentYear)
    [
      'all',
      ['==', ['typeof', ['get', 'year_end']], 'number'],
      ['<', ['get', 'year_end'], decliningThreshold],
      ['>', ['get', 'year_end'], currentYear],
    ], BASE_OPACITY - DECLINING_DIM,
    // Stable
    BASE_OPACITY,
  ]
}
