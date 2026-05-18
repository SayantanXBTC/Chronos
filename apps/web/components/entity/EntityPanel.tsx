// apps/web/components/entity/EntityPanel.tsx
'use client'

import { useTimelineStore } from '@/store/timeline'

const CONFIDENCE_LABELS: Record<string, string> = {
  exact: 'Exact boundary',
  approximate: 'Approximate boundary',
  inferred: 'Inferred boundary',
  disputed: 'Disputed boundary',
}

export function EntityPanel() {
  const entity = useTimelineStore((s) => s.selectedEntity)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)

  if (!entity) return null

  const { name, type, color, confidence_type, source_name } = entity.properties
  const confidenceLabel = CONFIDENCE_LABELS[confidence_type] ?? confidence_type

  return (
    <div
      className="absolute top-4 right-4 w-72 bg-black/80 backdrop-blur-md text-white rounded-xl p-5 border border-white/10 shadow-2xl"
      role="complementary"
      aria-label={`Entity: ${name}`}
    >
      <button
        onClick={() => setSelectedEntity(null)}
        className="absolute top-3 right-4 text-white/40 hover:text-white text-xl leading-none transition-colors"
        aria-label="Close entity panel"
      >
        ×
      </button>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-5 h-5 rounded flex-shrink-0 border border-white/20"
          style={{ backgroundColor: color }}
          aria-hidden="true"
        />
        <h2 className="font-bold text-lg leading-tight pr-4">{name}</h2>
      </div>
      <dl className="space-y-1 text-sm">
        <div className="flex gap-2">
          <dt className="text-white/50 w-20 flex-shrink-0">Type</dt>
          <dd className="text-white/80 capitalize">{type}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="text-white/50 w-20 flex-shrink-0">Boundary</dt>
          <dd className="text-white/80">{confidenceLabel}</dd>
        </div>
        {source_name && (
          <div className="flex gap-2">
            <dt className="text-white/50 w-20 flex-shrink-0">Source</dt>
            <dd className="text-white/60 text-xs leading-relaxed">{source_name}</dd>
          </div>
        )}
      </dl>
    </div>
  )
}
