import { describe, it, expect } from 'vitest'
import { generateJourneyStory } from '@/lib/journey'
import type { EntityDetail } from '@/types'

const ROME: EntityDetail = {
  slug: 'roman-empire',
  name: 'Roman Empire',
  type: 'empire',
  color: '#B22222',
  year_start: -27,
  year_end: 476,
  source_name: null,
  confidence_type: 'approximate',
  importance: 10,
  lineage: { predecessors: [], successors: [] },
}

const UNKNOWN: EntityDetail = {
  slug: 'unknown-entity',
  name: 'Unknown Kingdom',
  type: 'kingdom',
  color: '#888888',
  year_start: 500,
  year_end: 750,
  source_name: null,
  confidence_type: 'approximate',
  importance: 5,
  lineage: { predecessors: [], successors: [] },
}

describe('generateJourneyStory', () => {
  it('returns an existing STORY if one exists for the slug', () => {
    const story = generateJourneyStory(ROME)
    expect(story.slug).toBe('roman-empire')
    expect(story.chapters.length).toBeGreaterThan(3)
  })

  it('generates a 2-chapter story for entity without ENTITY_META peak', () => {
    const story = generateJourneyStory(UNKNOWN)
    expect(story.slug).toBe('unknown-entity')
    expect(story.name).toBe('Unknown Kingdom')
    expect(story.color).toBe('#888888')
    expect(story.chapters).toHaveLength(2)
    expect(story.chapters[0].year).toBe(500)
    expect(story.chapters[1].year).toBe(750)
  })

  it('generates founding and end chapter titles correctly', () => {
    const story = generateJourneyStory(UNKNOWN)
    expect(story.chapters[0].title).toBe('Founding')
    expect(story.chapters[story.chapters.length - 1].title).toBe('End of an Era')
  })

  it('chapter years are in ascending order', () => {
    const story = generateJourneyStory(ROME)
    const years = story.chapters.map((c) => c.year)
    for (let i = 1; i < years.length; i++) {
      expect(years[i]).toBeGreaterThanOrEqual(years[i - 1])
    }
  })

  it('every chapter has required fields', () => {
    const story = generateJourneyStory(UNKNOWN)
    for (const ch of story.chapters) {
      expect(ch.year).toBeDefined()
      expect(ch.title).toBeTruthy()
      expect(ch.description).toBeTruthy()
      expect(ch.focusSlug).toBe(UNKNOWN.slug)
    }
  })
})
