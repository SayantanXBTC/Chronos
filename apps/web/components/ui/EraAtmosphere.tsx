'use client'

import { useEffect } from 'react'
import { useTimelineStore } from '@/store/timeline'
import { getEraForYear } from '@/lib/year'

export function EraAtmosphere() {
  const year = useTimelineStore((s) => s.year)

  useEffect(() => {
    const era = getEraForYear(year)
    document.documentElement.setAttribute('data-era', era)
  }, [year])

  return null
}
