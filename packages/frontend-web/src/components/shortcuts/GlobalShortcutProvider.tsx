/**
 * Global Shortcut Provider
 * Stellt globale Shortcuts für alle Eingabemasken bereit
 */

import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { ShortcutHelpPanel, type ShortcutDefinition, type ShortcutDisplayMode } from './ShortcutHelpPanel'
import { GLOBAL_SHORTCUTS, handleGlobalShortcutKeyDown } from '@/lib/shortcuts/global-shortcuts'

type GlobalShortcutProviderProps = {
  children: ReactNode
}

export function GlobalShortcutProvider({ children }: GlobalShortcutProviderProps): JSX.Element {
  const [displayMode, setDisplayMode] = useState<ShortcutDisplayMode>('always')

  // Lade gespeicherte Präferenz
  useEffect(() => {
    const saved = localStorage.getItem('shortcut-help-display-mode')
    if (saved) {
      setDisplayMode(saved as ShortcutDisplayMode)
    }
  }, [])

  // Zyklische Schaltlogik: always → hover → hidden → always
  const cycleDisplayMode = useCallback((): void => {
    setDisplayMode((current) => {
      const modes: ShortcutDisplayMode[] = ['always', 'hover', 'hidden']
      const currentIndex = modes.indexOf(current)
      const nextIndex = (currentIndex + 1) % modes.length
      const nextMode = modes[nextIndex]
      
      // Speichere in localStorage
      localStorage.setItem('shortcut-help-display-mode', nextMode)
      
      // Wenn auf 'always' gesetzt wird, Panel auch expandieren
      if (nextMode === 'always' && typeof (window as any).__expandShortcutHelpPanel === 'function') {
        ;(window as any).__expandShortcutHelpPanel()
      }
      
      return nextMode
    })
  }, [])

  // Exportiere Funktion für externen Zugriff (z.B. von AppShell)
  useEffect(() => {
    ;(window as any).__cycleShortcutDisplayMode = cycleDisplayMode
    ;(window as any).__getShortcutDisplayMode = () => displayMode
    
    return () => {
      delete (window as any).__cycleShortcutDisplayMode
      delete (window as any).__getShortcutDisplayMode
    }
  }, [cycleDisplayMode, displayMode])

  // Registriere globale Keyboard-Listener
  useEffect(() => {
    window.addEventListener('keydown', handleGlobalShortcutKeyDown)
    return () => {
      window.removeEventListener('keydown', handleGlobalShortcutKeyDown)
    }
  }, [])

  // Konvertiere GLOBAL_SHORTCUTS zu ShortcutDefinition[]
  const shortcutDefinitions: ShortcutDefinition[] = GLOBAL_SHORTCUTS.map((s) => ({
    key: s.key,
    label: s.label,
    description: s.description,
    category: s.category,
  }))

  return (
    <>
      {children}
      <ShortcutHelpPanel
        shortcuts={shortcutDefinitions}
        displayMode={displayMode}
        onDisplayModeChange={setDisplayMode}
      />
    </>
  )
}

