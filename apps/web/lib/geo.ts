import type { EntityFeature } from '@/types'

export type BBox = [number, number, number, number]

export function bboxCenter(bbox: BBox): [number, number] {
  const [minX, minY, maxX, maxY] = bbox
  return [(minX + maxX) / 2, (minY + maxY) / 2]
}

export function featureCentroid(f: EntityFeature): [number, number] {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const polygon of f.geometry.coordinates) {
    for (const ring of polygon) {
      for (const [x, y] of ring) {
        if (x < minX) minX = x
        if (y < minY) minY = y
        if (x > maxX) maxX = x
        if (y > maxY) maxY = y
      }
    }
  }
  return bboxCenter([minX, minY, maxX, maxY])
}
