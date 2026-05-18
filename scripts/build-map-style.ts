/**
 * Downloads the OpenFreeMap Liberty style and strips modern political overlays,
 * producing a clean historical base map saved to apps/web/public/map-style/historical.json.
 *
 * Run: npx tsx scripts/build-map-style.ts
 */

import { writeFileSync, mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUT_PATH = join(__dirname, '../apps/web/public/map-style/historical.json')
const STYLE_URL = 'https://tiles.openfreemap.org/styles/liberty'

// Layer id substrings that identify modern political overlays to remove.
// Physical geography (water, terrain, roads) is preserved for orientation.
const POLITICAL_PATTERNS = [
  'boundary',
  'border',
  'disputed',
  'country',
  'state',
  'province',
  'admin',
  'place',   // modern place name labels
  'city',
  'town',
  'village',
  'label',
]

function isPoliticalLayer(layer: { id: string; type: string }): boolean {
  const id = layer.id.toLowerCase()
  return POLITICAL_PATTERNS.some((p) => id.includes(p))
}

interface MaplibreLayer {
  id: string
  type: string
  source?: string
  [key: string]: unknown
}

interface MaplibreStyle {
  layers: MaplibreLayer[]
  sources: Record<string, unknown>
  [key: string]: unknown
}

async function main() {
  console.log(`Fetching style from ${STYLE_URL} …`)
  const res = await fetch(STYLE_URL)
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching style`)
  const style = (await res.json()) as MaplibreStyle

  const before = style.layers.length
  const kept = style.layers.filter((l) => !isPoliticalLayer(l))
  const after = kept.length
  console.log(`Stripped ${before - after} political layers (kept ${after}/${before})`)

  // Remove sources that are no longer referenced by any remaining layer.
  const usedSources = new Set(kept.map((l) => l.source).filter(Boolean))
  const prunedSources: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(style.sources)) {
    if (usedSources.has(k) || k === 'openmaptiles') {
      // always keep the base tile source even if no layers use it directly
      prunedSources[k] = v
    }
  }
  console.log(
    `Sources: kept ${Object.keys(prunedSources).length}/${Object.keys(style.sources).length}`
  )

  const result: MaplibreStyle = { ...style, layers: kept, sources: prunedSources }

  mkdirSync(dirname(OUT_PATH), { recursive: true })
  writeFileSync(OUT_PATH, JSON.stringify(result, null, 2))
  console.log(`Written to ${OUT_PATH}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
