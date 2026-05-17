// apps/web/components/ui/LoadingOverlay.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'

export function LoadingOverlay() {
  const isLoading = useTimelineStore((s) => s.isLoading)
  const error = useTimelineStore((s) => s.error)

  if (!isLoading && !error) return null

  return (
    <div
      className="absolute top-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      {isLoading && (
        <div className="bg-black/70 backdrop-blur-sm text-white/80 text-xs px-3 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
          <div
            className="w-3 h-3 border border-white/40 border-t-white rounded-full animate-spin"
            aria-hidden="true"
          />
          Loading...
        </div>
      )}
      {error && !isLoading && (
        <div className="bg-red-900/80 backdrop-blur-sm text-red-200 text-xs px-3 py-1.5 rounded-full shadow-lg">
          {error}
        </div>
      )}
    </div>
  )
}
