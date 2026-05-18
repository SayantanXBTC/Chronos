'use client'

import type { LineageEntry } from '@/types'
import { yearToDisplay } from '@/lib/year'

const RELATIONSHIP_LABELS: Record<string, string> = {
  evolved_into: 'evolved into',
  successor: 'succeeded by',
  continuation: 'continued as',
  split_from: 'split into',
  merged_into: 'merged into',
}

interface LineageTreeProps {
  predecessors: LineageEntry[]
  successors: LineageEntry[]
}

export function LineageTree({ predecessors, successors }: LineageTreeProps) {
  if (predecessors.length === 0 && successors.length === 0) return null

  return (
    <div className="mt-3 pt-3 border-t border-white/10">
      <h3 className="text-white/40 text-xs uppercase tracking-widest mb-2">Lineage</h3>
      {predecessors.length > 0 && (
        <div className="mb-2">
          <div className="text-white/30 text-xs mb-1">Preceded by</div>
          {predecessors.map((entry) => (
            <div key={entry.slug} className="flex items-baseline gap-2 text-sm py-0.5">
              <span className="text-amber-300/80 font-medium truncate">{entry.name}</span>
              <span className="text-white/30 text-xs flex-shrink-0">
                {RELATIONSHIP_LABELS[entry.relationship_type] ?? entry.relationship_type}
              </span>
              <span className="text-white/30 text-xs flex-shrink-0">{yearToDisplay(entry.year)}</span>
            </div>
          ))}
        </div>
      )}
      {successors.length > 0 && (
        <div>
          <div className="text-white/30 text-xs mb-1">Succeeded by</div>
          {successors.map((entry) => (
            <div key={entry.slug} className="flex items-baseline gap-2 text-sm py-0.5">
              <span className="text-amber-300/80 font-medium truncate">{entry.name}</span>
              <span className="text-white/30 text-xs flex-shrink-0">
                {RELATIONSHIP_LABELS[entry.relationship_type] ?? entry.relationship_type}
              </span>
              <span className="text-white/30 text-xs flex-shrink-0">{yearToDisplay(entry.year)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
