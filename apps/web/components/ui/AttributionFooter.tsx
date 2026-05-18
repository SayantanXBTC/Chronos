// apps/web/components/ui/AttributionFooter.tsx
'use client'

import { useEffect, useState } from 'react'
import { fetchSources } from '@/lib/api'
import type { SourceItem } from '@/types'

export function AttributionFooter() {
  const [sources, setSources] = useState<SourceItem[]>([])

  useEffect(() => {
    fetchSources().then(setSources).catch(() => {})
  }, [])

  if (!sources.length) return null

  return (
    <div className="absolute bottom-0 left-0 px-3 py-1.5 pointer-events-none select-none">
      <p className="text-white/30 text-[10px] font-mono">
        Map data:{' '}
        {sources.map((s, i) => (
          <span key={s.id}>
            {i > 0 && ' · '}
            {s.url ? (
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="pointer-events-auto hover:text-white/60 transition-colors"
              >
                {s.name}
              </a>
            ) : (
              s.name
            )}
          </span>
        ))}
      </p>
    </div>
  )
}
