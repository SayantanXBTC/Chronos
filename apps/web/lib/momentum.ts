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
  selectedSlug: string | null,
): unknown[] {
  const risingThreshold = currentYear - RISING_THRESHOLD
  const decliningThreshold = currentYear + DECLINING_THRESHOLD

  return [
    'case',
    // Selected = always bright
    ['==', ['get', 'slug'], selectedSlug ?? '___'], 0.78,
    // Rising (born recently)
    ['>', ['get', 'year_start'], risingThreshold],
    BASE_OPACITY + RISING_BOOST,
    // Declining (ends soon)
    [
      'all',
      ['has', 'year_end'],
      ['!=', ['get', 'year_end'], null],
      ['<', ['coalesce', ['get', 'year_end'], 9999], decliningThreshold],
      ['>', ['coalesce', ['get', 'year_end'], 9999], currentYear],
    ],
    BASE_OPACITY - DECLINING_DIM,
    // Stable
    BASE_OPACITY,
  ]
}
