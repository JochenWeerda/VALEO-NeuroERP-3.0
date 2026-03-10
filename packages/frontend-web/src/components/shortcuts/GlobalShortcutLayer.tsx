import { useCallback, useEffect, useMemo, useState } from 'react'
import { ShortcutHelpPanel, type ShortcutDefinition, type ShortcutDisplayMode } from './ShortcutHelpPanel'
import { GLOBAL_SHORTCUTS, handleGlobalShortcutKeyDown } from '@/lib/shortcuts/global-shortcuts'

export function GlobalShortcutLayer(): JSX.Element {
  const [displayMode, setDisplayMode] = useState<ShortcutDisplayMode>('always')

  useEffect(() => {
    const saved = localStorage.getItem('shortcut-help-display-mode')
    if (saved) {
      setDisplayMode(saved as ShortcutDisplayMode)
    }
  }, [])

  const cycleDisplayMode = useCallback((): void => {
    setDisplayMode((current) => {
      const modes: ShortcutDisplayMode[] = ['always', 'hover', 'hidden']
      const nextMode = modes[(modes.indexOf(current) + 1) % modes.length]
      localStorage.setItem('shortcut-help-display-mode', nextMode)

      if (nextMode === 'always' && typeof (window as any).__expandShortcutHelpPanel === 'function') {
        ;(window as any).__expandShortcutHelpPanel()
      }

      return nextMode
    })
  }, [])

  useEffect(() => {
    ;(window as any).__cycleShortcutDisplayMode = cycleDisplayMode
    ;(window as any).__getShortcutDisplayMode = () => displayMode

    return () => {
      delete (window as any).__cycleShortcutDisplayMode
      delete (window as any).__getShortcutDisplayMode
    }
  }, [cycleDisplayMode, displayMode])

  useEffect(() => {
    window.addEventListener('keydown', handleGlobalShortcutKeyDown)
    return () => {
      window.removeEventListener('keydown', handleGlobalShortcutKeyDown)
    }
  }, [])

  const shortcutDefinitions = useMemo<ShortcutDefinition[]>(() => {
    return GLOBAL_SHORTCUTS.map((shortcut) => ({
      key: shortcut.key,
      label: shortcut.label,
      description: shortcut.description,
      category: shortcut.category,
    }))
  }, [])

  return (
    <ShortcutHelpPanel
      shortcuts={shortcutDefinitions}
      displayMode={displayMode}
      onDisplayModeChange={setDisplayMode}
    />
  )
}
