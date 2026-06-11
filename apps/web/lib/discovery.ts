import type { EntityFeature } from '@/types'

export interface DiscoveryPrompt {
  id: string
  label: string
  cta: string
  slug: string
}

export function computeDiscoveryPrompts(
  entities: EntityFeature[],
  currentYear: number,
): DiscoveryPrompt[] {
  if (entities.length === 0) return []

  const prompts: DiscoveryPrompt[] = []
  const usedSlugs = new Set<string>()

  // 1. dominant-now: highest importance
  const dominant = [...entities].sort(
    (a, b) => b.properties.importance - a.properties.importance,
  )[0]
  const { name: dominantName, slug: dominantSlug } = dominant.properties
  prompts.push({
    id: 'dominant-now',
    label: 'The dominant power of this era',
    cta: `Follow ${dominantName} →`,
    slug: dominantSlug,
  })
  usedSlugs.add(dominantSlug)

  // 2. longest-reign: greatest lifespan (not already used)
  const longestReign = [...entities]
    .filter((e) => !usedSlugs.has(e.properties.slug))
    .sort((a, b) => {
      const spanA = Math.abs((a.properties.year_end ?? currentYear) - a.properties.year_start)
      const spanB = Math.abs((b.properties.year_end ?? currentYear) - b.properties.year_start)
      return spanB - spanA
    })[0]

  if (longestReign) {
    const { name, slug, year_start, year_end } = longestReign.properties
    const span = Math.abs((year_end ?? currentYear) - year_start)
    prompts.push({
      id: 'longest-reign',
      label: `${span} years of unbroken rule`,
      cta: `Explore ${name} →`,
      slug,
    })
    usedSlugs.add(slug)
  }

  // 3. rising-power: most recent year_start still ≤ currentYear (not already used)
  const risingPower = [...entities]
    .filter((e) => !usedSlugs.has(e.properties.slug) && e.properties.year_start <= currentYear)
    .sort((a, b) => b.properties.year_start - a.properties.year_start)[0]

  if (risingPower) {
    const { name, slug } = risingPower.properties
    prompts.push({
      id: 'rising-power',
      label: 'A new power has emerged',
      cta: `Discover ${name} →`,
      slug,
    })
  }

  return prompts.slice(0, 3)
}
