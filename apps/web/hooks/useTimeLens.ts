'use client'

import { useEffect, useRef, useState } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { fetchWorldState } from '@/lib/api'
import type { MapViewHandle } from '@/components/map/MapView'

const LENS_OFFSET_YEARS = 50
const DEBOUNCE_MS = 100

export function useTimeLens(mapRef: React.RefObject<MapViewHandle | null>): {
  previewYear: number | null
} {
  const isActiveRef = useRef(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const [previewYear, setPreviewYear] = useState<number | null>(null)

  useEffect(() => {
    // Keep a ref to current year without subscribing to re-renders
    let currentYear = useTimelineStore.getState().year
    const unsub = useTimelineStore.subscribe((s) => { currentYear = s.year })

    function activate() {
      if (isActiveRef.current) return
      isActiveRef.current = true
      document.body.style.cursor = 'crosshair'
    }

    function deactivate() {
      if (!isActiveRef.current) return
      isActiveRef.current = false
      document.body.style.cursor = ''
      if (debounceRef.current) { clearTimeout(debounceRef.current); debounceRef.current = null }
      abortRef.current?.abort()
      abortRef.current = null
      mapRef.current?.hideTimeLens()
      setPreviewYear(null)
    }

    async function fetchPreview() {
      const preview = currentYear + LENS_OFFSET_YEARS
      abortRef.current?.abort()
      abortRef.current = new AbortController()
      try {
        const data = await fetchWorldState(preview, { signal: abortRef.current.signal })
        if (isActiveRef.current) {
          mapRef.current?.showTimeLens(data, preview)
          setPreviewYear(preview)
        }
      } catch {
        // fetch aborted — ignore
      }
    }

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Alt') { e.preventDefault(); activate() }
    }

    function onKeyUp(e: KeyboardEvent) {
      if (e.key === 'Alt') deactivate()
    }

    function onBlur() {
      deactivate()
    }

    function onMouseMove() {
      if (!isActiveRef.current) return
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(fetchPreview, DEBOUNCE_MS)
    }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    window.addEventListener('blur', onBlur)
    window.addEventListener('mousemove', onMouseMove)

    return () => {
      unsub()
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('blur', onBlur)
      window.removeEventListener('mousemove', onMouseMove)
      if (debounceRef.current) clearTimeout(debounceRef.current)
      abortRef.current?.abort()
      document.body.style.cursor = ''
    }
  }, [mapRef])

  return { previewYear }
}
