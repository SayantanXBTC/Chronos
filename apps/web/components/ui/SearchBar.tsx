'use client'

import { useState, useRef, useEffect } from 'react'
import { useTimelineStore } from '@/store/timeline'
import type { EntityFeature } from '@/types'

export function SearchBar() {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const currentEntities = useTimelineStore((s) => s.currentEntities)
  const setSelectedEntity = useTimelineStore((s) => s.setSelectedEntity)
  const containerRef = useRef<HTMLDivElement>(null)

  const trimmed = query.trim().toLowerCase()
  const results: EntityFeature[] = trimmed.length < 1
    ? []
    : currentEntities
        .filter((f) => f.properties.name.toLowerCase().includes(trimmed))
        .slice(0, 10)

  function select(entity: EntityFeature) {
    setSelectedEntity(entity)
    setQuery('')
    setOpen(false)
  }

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  return (
    <div ref={containerRef} className="absolute top-4 left-4 w-64 z-10">
      <input
        type="search"
        value={query}
        onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
        onFocus={() => setOpen(true)}
        placeholder="Search civilizations…"
        className="w-full bg-black/70 backdrop-blur-md text-white placeholder-white/30 rounded-lg px-3 py-2 text-sm border border-white/10 outline-none focus:border-amber-400/50 transition-colors"
        aria-label="Search civilizations"
        aria-expanded={open && results.length > 0}
        aria-haspopup="listbox"
        role="combobox"
        autoComplete="off"
      />
      {open && results.length > 0 && (
        <ul
          className="mt-1 bg-black/90 backdrop-blur-md rounded-lg border border-white/10 shadow-2xl overflow-hidden"
          role="listbox"
          aria-label="Search results"
        >
          {results.map((entity) => (
            <li key={entity.properties.slug}>
              <button
                onClick={() => select(entity)}
                className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/80 hover:bg-white/10 transition-colors text-left"
                role="option"
              >
                <div
                  className="w-3 h-3 rounded-sm flex-shrink-0"
                  style={{ backgroundColor: entity.properties.color }}
                  aria-hidden="true"
                />
                <span className="truncate">{entity.properties.name}</span>
                <span className="text-white/30 text-xs flex-shrink-0 capitalize ml-auto">
                  {entity.properties.type}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
