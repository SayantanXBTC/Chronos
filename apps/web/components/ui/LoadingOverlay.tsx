'use client'

import { useTimelineStore } from '@/store/timeline'

const PILL = "absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/75 backdrop-blur-md text-white text-sm px-4 py-2 rounded-full border border-white/10 shadow-lg"

export function LoadingOverlay() {
  const isLoading = useTimelineStore((s) => s.isLoading)
  const error = useTimelineStore((s) => s.error)

  if (error) {
    return (
      <div className={PILL} role="status" aria-live="assertive">
        <span className="w-2 h-2 rounded-full bg-red-400" aria-hidden="true" />
        <span className="text-red-300">{error}</span>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className={PILL} role="status" aria-live="polite">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" aria-hidden="true" />
        <span>Loading…</span>
      </div>
    )
  }

  return null
}
