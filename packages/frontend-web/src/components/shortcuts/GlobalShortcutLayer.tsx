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

      if (nextMode === 'always') {
        const w = window as Window & { __expandShortcutHelpPanel?: () => void }
        if (typeof w.__expandShortcutHelpPanel === 'function') {
          w.__expandShortcutHelpPanel()
        }
      }

      return nextMode
    })
  }, [])

  useEffect(() => {
    const w = window as Window & {
      __cycleShortcutDisplayMode?: typeof cycleDisplayMode
      __getShortcutDisplayMode?: () => ShortcutDisplayMode
    }
    w.__cycleShortcutDisplayMode = cycleDisplayMode
    w.__getShortcutDisplayMode = () => displayMode

    return () => {
      delete w.__cycleShortcutDisplayMode
      delete w.__getShortcutDisplayMode
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
