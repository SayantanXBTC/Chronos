// apps/web/lib/year.ts

// Snapshot years the backend pre-computes (matches world_state.py SNAPSHOT_YEARS).
// Adaptive density: -3000 to 2026 CE with variable intervals by era.
function buildSnapshotYears(): readonly number[] {
  const years: number[] = []
  for (let y = -3000; y <= -1000; y += 250) years.push(y)
  for (let y = -900; y <= -500; y += 100) years.push(y)
  for (let y = -475; y <= 500; y += 25) { if (y !== 0) years.push(y) }
  for (let y = 550; y <= 1500; y += 50) years.push(y)
  for (let y = 1525; y <= 1900; y += 25) years.push(y)
  for (let y = 1910; y <= 2020; y += 10) years.push(y)
  years.push(2026)
  return Object.freeze([...new Set(years)].sort((a, b) => a - b))
}

export const SNAPSHOT_YEARS: readonly number[] = buildSnapshotYears()

export function yearToDisplay(year: number): string {
  if (year === 0) throw new RangeError('Year 0 does not exist in this calendar system')
  return year < 0 ? `${Math.abs(year)} BCE` : `${year} CE`
}

// Slider range: 0 → 5025, mapping to years -3000 → 2026 (skipping 0).
// Positions 0–2999 map to BCE years -3000 to -1.
// Positions 3000–5025 map to CE years 1 to 2026.
export function sliderToYear(value: number): number {
  return value < 3000 ? value - 3000 : value - 2999
}

export function yearToSlider(year: number): number {
  if (year === 0) throw new RangeError('Year 0 does not exist in this calendar system')
  return year < 0 ? year + 3000 : year + 2999
}

export function snapToSnapshot(year: number): number {
  let result = SNAPSHOT_YEARS[0]
  for (const snap of SNAPSHOT_YEARS) {
    if (snap <= year) {
      result = snap
    } else {
      break
    }
  }
  return result
}

export interface EraMark {
  year: number
  label: string
}

export const ERA_MARKERS: EraMark[] = [
  { year: -3000, label: 'Ancient' },
  { year: -500,  label: 'Classical' },
  { year: 500,   label: 'Medieval' },
  { year: 1500,  label: 'Early Modern' },
  { year: 1800,  label: 'Modern' },
]

export function snapToPrevSnapshot(year: number): number {
  const idx = SNAPSHOT_YEARS.indexOf(year)
  if (idx < 0) {
    const below = [...SNAPSHOT_YEARS].reverse().find((y) => y < year)
    return below ?? SNAPSHOT_YEARS[0]
  }
  if (idx === 0) return SNAPSHOT_YEARS[0]
  return SNAPSHOT_YEARS[idx - 1]
}

export function snapToNextSnapshot(year: number): number {
  const idx = SNAPSHOT_YEARS.indexOf(year)
  if (idx < 0) {
    const above = SNAPSHOT_YEARS.find((y) => y > year)
    return above ?? SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]
  }
  if (idx >= SNAPSHOT_YEARS.length - 1) return SNAPSHOT_YEARS[SNAPSHOT_YEARS.length - 1]
  return SNAPSHOT_YEARS[idx + 1]
}

export type Era = 'ancient' | 'classical' | 'medieval' | 'early-modern' | 'modern'

export function getEraForYear(year: number): Era {
  if (year < -500) return 'ancient'
  if (year < 500)  return 'classical'
  if (year < 1500) return 'medieval'
  if (year < 1800) return 'early-modern'
  return 'modern'
}

export const ERA_MAP_BACKGROUNDS: Record<Era, string> = {
  'ancient':      '#d4b896',
  'classical':    '#cfc4a8',
  'medieval':     '#c4b898',
  'early-modern': '#c8c4b0',
  'modern':       '#c0c8cc',
}

export const ERA_WATER_COLORS: Record<Era, string> = {
  'ancient':      '#7a9ab8',
  'classical':    '#6e9ab5',
  'medieval':     '#6088a0',
  'early-modern': '#5d8fa8',
  'modern':       '#5890a8',
}

export const ERA_TRANSITION_DURATION = 800
