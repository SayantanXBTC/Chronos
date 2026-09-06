'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useSettingsStore } from '@/store/settings'
import { OrnamentFrame } from '@/components/ui/OrnamentFrame'
import { Touchable } from '@/components/ui/Touchable'
import { MOTION_HUD } from '@/lib/motion'

function ToggleRow({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (next: boolean) => void
}) {
  return (
    <Touchable
      onClick={() => onChange(!checked)}
      soundKey="click"
      ripple={false}
      ariaLabel={label}
      className="w-full flex items-center justify-between gap-3 px-2 py-1.5"
    >
      <span style={{ fontFamily: 'var(--font-garamond)', fontSize: 13, color: 'var(--parchment-ink-soft)' }}>
        {label}
      </span>
      <span
        role="switch"
        aria-checked={checked}
        style={{
          width: 30,
          height: 16,
          borderRadius: 999,
          flexShrink: 0,
          position: 'relative',
          background: checked ? 'var(--parchment-drop)' : 'rgba(58,36,16,0.25)',
          transition: 'background 0.15s ease',
        }}
      >
        <span
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: 2,
            left: checked ? 16 : 2,
            width: 12,
            height: 12,
            borderRadius: '50%',
            background: 'var(--parchment-gradient, #f0e6d2)',
            boxShadow: '0 1px 2px rgba(0,0,0,0.4)',
            transition: 'left 0.15s ease',
          }}
        />
      </span>
    </Touchable>
  )
}

export function SettingsPanel() {
  const [open, setOpen] = useState(false)
  const visualPolish = useSettingsStore((s) => s.visualPolish)
  const setVisualPolish = useSettingsStore((s) => s.setVisualPolish)
  const reducedMotion = useSettingsStore((s) => s.reducedMotion)
  const setReducedMotion = useSettingsStore((s) => s.setReducedMotion)
  const soundEnabled = useSettingsStore((s) => s.soundEnabled)
  const setSoundEnabled = useSettingsStore((s) => s.setSoundEnabled)

  return (
    <div className="absolute top-4 right-4 z-20 flex flex-col items-end gap-2">
      <Touchable
        onClick={() => setOpen((v) => !v)}
        soundKey={open ? 'close' : 'open'}
        ariaLabel="Settings"
        className="w-9 h-9 flex items-center justify-center rounded-full"
      >
        <span style={{ fontSize: 16, color: 'var(--parchment-ink)' }} aria-hidden="true">⚙</span>
      </Touchable>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.97 }}
            transition={MOTION_HUD}
            className="w-64"
          >
            <OrnamentFrame density="mid">
              <div className="pb-1.5 mb-1" style={{ borderBottom: '1px solid var(--parchment-border)' }}>
                <div style={{ fontFamily: 'var(--font-cinzel)', fontSize: 10, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--parchment-label)' }}>
                  Settings
                </div>
              </div>
              <ToggleRow label="Sound effects" checked={soundEnabled} onChange={setSoundEnabled} />
              <ToggleRow label="Visual polish" checked={visualPolish} onChange={setVisualPolish} />
              <ToggleRow label="Reduce motion" checked={reducedMotion} onChange={setReducedMotion} />
            </OrnamentFrame>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
