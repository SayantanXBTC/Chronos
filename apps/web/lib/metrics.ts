export class LatencyTracker {
  private t0: number | null = null
  last = 0
  readonly label: string

  constructor(label: string) {
    this.label = label
  }

  start(): void {
    this.t0 = performance.now()
  }

  end(): number {
    if (this.t0 === null) return 0
    this.last = performance.now() - this.t0
    this.t0 = null
    return this.last
  }
}

export class FPSCounter {
  private frames: number[] = []
  private rafId: number | null = null
  fps = 0

  start(onUpdate?: (fps: number) => void): void {
    const tick = (now: number) => {
      if (this.rafId === null) return  // stop() was called; bail out
      this.frames.push(now)
      const cutoff = now - 1000
      while (this.frames.length > 0 && this.frames[0] < cutoff) {
        this.frames.shift()
      }
      this.fps = this.frames.length
      onUpdate?.(this.fps)
      this.rafId = requestAnimationFrame(tick)
    }
    this.rafId = requestAnimationFrame(tick)
  }

  stop(): void {
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
    this.frames = []
    this.fps = 0
  }
}

export const timelineLatency = new LatencyTracker('timeline')
export const panelLatency = new LatencyTracker('panel')
