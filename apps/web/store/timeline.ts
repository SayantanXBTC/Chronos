// apps/web/store/timeline.ts
import { create } from 'zustand'
import type { EntityFeature } from '@/types'

interface TimelineState {
  year: number
  selectedEntity: EntityFeature | null
  isLoading: boolean
  error: string | null
  setYear: (year: number) => void
  setSelectedEntity: (entity: EntityFeature | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useTimelineStore = create<TimelineState>((set) => ({
  year: -264,
  selectedEntity: null,
  isLoading: false,
  error: null,
  setYear: (year) => set({ year }),
  setSelectedEntity: (selectedEntity) => set({ selectedEntity }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}))
