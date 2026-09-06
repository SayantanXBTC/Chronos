// apps/web/store/story.ts
import { create } from 'zustand'

export interface StoryChapter {
  year: number
  title: string
  description: string
  focusSlug: string
}

export interface CivStory {
  slug: string
  name: string
  color: string
  chapters: StoryChapter[]
}

interface StoryState {
  activeStory: CivStory | null
  startStory: (story: CivStory) => void
  endStory: () => void
}

export const useStoryStore = create<StoryState>((set) => ({
  activeStory: null,
  startStory: (story) => set({ activeStory: story }),
  endStory: () => set({ activeStory: null }),
}))
