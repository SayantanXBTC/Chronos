// apps/web/lib/year.ts

// Snapshot years the backend pre-computes (matches world_state.py SNAPSHOT_YEARS).
// Range is -500 to 500 CE in 25-year steps, skipping 0.
export const SNAPSHOT_YEARS: readonly number[] = [
  -500, -475, -450, -425, -400, -375, -350, -325, -300,
  -275, -250, -225, -200, -175, -150, -125, -100,  -75,
   -50,  -25,   25,   50,   75,  100,  125,  150,  175,
   200,  225,  250,  275,  300,  325,  350,  375,  400,
   425,  450,  475,  500,
]

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
