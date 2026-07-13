/**
 * KeyboardShortcutBar — Zeigt aktive Keyboard-Shortcuts als Footer-Leiste an
 *
 * Gap 023: Keyboard-first Kernmasken
 * Erscheint am unteren Rand des Screens, sichtbar sobald kein Touch-Gerät erkannt.
 * Zeigt maximal 6 Shortcuts (häufigste Aktionen).
 *
 * Verwendung:
 *   <KeyboardShortcutBar shortcuts={buildCoreMaskShortcuts({ onSave, onCancel })} />
 */

import React from 'react'
import { cn } from '@/lib/utils'
import { Keyboard } from 'lucide-react'
import { KeyboardShortcut, formatShortcutLabel } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/components/touch/TouchFieldLayout'

interface KeyboardShortcutBarProps {
  shortcuts: KeyboardShortcut[]
  /** Maximale Anzahl angezeigter Shortcuts (default: 6) */
  maxVisible?: number
  className?: string
}

export function KeyboardShortcutBar({
  shortcuts,
  maxVisible = 6,
  className,
}: KeyboardShortcutBarProps): JSX.Element | null {
  const isTouch = useTouchDevice()

  // Auf Touch-Geräten nicht anzeigen
  if (isTouch) return null

  const visible = shortcuts.filter((s) => !s.disabled).slice(0, maxVisible)
  if (visible.length === 0) return null

  return (
    <div
      role="status"
      aria-label="Keyboard Shortcuts"
      className={cn(
        'flex items-center gap-1 border-t border-slate-200 bg-slate-50 px-4 py-2',
        'text-xs text-slate-500',
        className,
      )}
    >
      <Keyboard className="mr-2 h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden />
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {visible.map((sc) => (
          <span key={`${sc.key}-${sc.ctrl}-${sc.alt}`} className="flex items-center gap-1">
            <kbd className="inline-flex items-center rounded border border-slate-300 bg-white px-1.5 py-0.5 font-mono text-xs text-slate-600 shadow-sm">
              {formatShortcutLabel(sc)}
            </kbd>
            <span>{sc.label}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
