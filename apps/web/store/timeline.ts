// apps/web/store/timeline.ts
import { create } from 'zustand'
import type { EntityFeature } from '@/types'

export interface Viewport {
  minX: number
  minY: number
  maxX: number
  maxY: number
  zoom: number
}

const DEFAULT_VIEWPORT: Viewport = {
  minX: -180, minY: -90, maxX: 180, maxY: 90, zoom: 4,
}

interface TimelineState {
  year: number
  selectedEntity: EntityFeature | null
  currentEntities: EntityFeature[]
  isLoading: boolean
  error: string | null
  viewport: Viewport
  isPlaying: boolean
  playSpeed: number
  setYear: (year: number) => void
  setSelectedEntity: (entity: EntityFeature | null) => void
  setCurrentEntities: (entities: EntityFeature[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setViewport: (viewport: Viewport) => void
  setPlaying: (playing: boolean) => void
  setPlaySpeed: (speed: number) => void
}

export const useTimelineStore = create<TimelineState>((set) => ({
  year: -264,
  selectedEntity: null,
  currentEntities: [],
  isLoading: false,
  error: null,
  viewport: DEFAULT_VIEWPORT,
  isPlaying: false,
  playSpeed: 1,
  setYear: (year) => set({ year }),
  setSelectedEntity: (selectedEntity) => set({ selectedEntity }),
  setCurrentEntities: (currentEntities) => set({ currentEntities }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setViewport: (viewport) => set({ viewport }),
  setPlaying: (isPlaying) => set({ isPlaying }),
  setPlaySpeed: (playSpeed) => set({ playSpeed }),
}))
