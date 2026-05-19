'use client'

import { useEffect, useState } from 'react'
import { FPSCounter } from '@/lib/metrics'

export function MetricsOverlay() {
  const [visible, setVisible] = useState(false)
  const [fps, setFps] = useState(0)

  useEffect(() => {
    const counter = new FPSCounter()

    const handleKey = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === 'M') {
        setVisible((v) => {
          if (!v) counter.start(setFps)
          else counter.stop()
          return !v
        })
      }
    }

    window.addEventListener('keydown', handleKey)
    return () => {
      window.removeEventListener('keydown', handleKey)
      counter.stop()
    }
  }, [])

  if (!visible) return null

  return (
    <div className="absolute top-16 left-4 bg-black/80 text-green-400 font-mono text-xs px-3 py-2 rounded pointer-events-none z-50 border border-green-400/20">
      <div>{fps} FPS</div>
      <div className="text-white/40 text-[10px] mt-0.5">Shift+M to hide</div>
    </div>
  )
}
