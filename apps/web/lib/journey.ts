import { STORIES } from '@/data/stories'
import { ENTITY_META } from '@/data/entity-metadata'
import type { CivStory, StoryChapter } from '@/store/story'
import type { EntityDetail } from '@/types'

export function generateJourneyStory(entity: EntityDetail): CivStory {
  // Return hand-crafted story if one exists
  const existing = STORIES.find((s) => s.slug === entity.slug)
  if (existing) return existing

  const meta = ENTITY_META[entity.slug]
  const chapters: StoryChapter[] = []

  const mapCoords = meta && 'capital' in meta && (meta as { capital?: { name: string; lon: number; lat: number } }).capital
    ? [(meta as { capital: { name: string; lon: number; lat: number } }).capital.lon, (meta as { capital: { name: string; lon: number; lat: number } }).capital.lat] as [number, number]
    : undefined

  // Founding chapter
  chapters.push({
    year: entity.year_start,
    title: 'Founding',
    description: `${entity.name} was established in ${formatYear(entity.year_start)}.`,
    focusSlug: entity.slug,
    ...(mapCoords ? { mapCoords } : {}),
  })

  // Peak chapter (if meta peak_year exists, differs from year_start, and is before year_end)
  if (
    meta?.peak_year !== undefined &&
    meta.peak_year !== entity.year_start &&
    (entity.year_end === null || meta.peak_year < entity.year_end)
  ) {
    chapters.push({
      year: meta.peak_year,
      title: meta.peak_label ?? 'Height of Power',
      description: `${entity.name} reached the height of its power in ${formatYear(meta.peak_year)}.`,
      focusSlug: entity.slug,
      ...(mapCoords ? { mapCoords } : {}),
    })
  }

  // End chapter (if year_end is set and differs from year_start)
  if (entity.year_end !== null && entity.year_end !== entity.year_start) {
    chapters.push({
      year: entity.year_end,
      title: 'End of an Era',
      description: `${entity.name} came to an end in ${formatYear(entity.year_end)}.`,
      focusSlug: entity.slug,
      ...(mapCoords ? { mapCoords } : {}),
    })
  }

  return {
    slug: entity.slug,
    name: entity.name,
    color: entity.color,
    chapters,
  }
}

function formatYear(year: number): string {
  if (year < 0) return `${Math.abs(year)} BCE`
  return `${year} CE`
}
