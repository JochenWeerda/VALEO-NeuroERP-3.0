import { Suspense, lazy, type ReactNode, useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { useFeature } from '@/hooks/useFeature'

interface AppShellProps {
  children: ReactNode
  enableCommandPalette?: boolean
}

const CommandPalette = lazy(() =>
  import('./CommandPalette').then((module) => ({ default: module.CommandPalette })),
)

const Sidebar = lazy(() =>
  import('./Sidebar').then((module) => ({ default: module.Sidebar })),
)

const TopBar = lazy(() =>
  import('./TopBar').then((module) => ({ default: module.TopBar })),
)

export function AppShell({ children, enableCommandPalette = true }: AppShellProps): JSX.Element {
  const navigate = useNavigate()
  const commandPaletteFeatureEnabled = useFeature('commandPalette')
  const commandPaletteAvailable = enableCommandPalette && commandPaletteFeatureEnabled
  const [commandOpen, setCommandOpen] = useState<boolean>(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false)

  const handleToggleSidebar = useCallback((): void => {
    setSidebarCollapsed((collapsed) => !collapsed)
  }, [])

  const handleToggleShortcuts = useCallback((): void => {
    // Zyklische Schaltlogik: always → hover → hidden → always
    // Warte kurz, falls die Funktion noch nicht initialisiert ist
    const cycleMode = (): void => {
      if (typeof (window as any).__cycleShortcutDisplayMode === 'function') {
        (window as any).__cycleShortcutDisplayMode()
      } else {
        // Retry nach kurzer Verzögerung
        setTimeout(() => {
          if (typeof (window as any).__cycleShortcutDisplayMode === 'function') {
            (window as any).__cycleShortcutDisplayMode()
          } else {
            console.warn('ShortcutHelpPanel cycle function not found')
          }
        }, 100)
      }
    }
    cycleMode()
  }, [])

  const handleMobileMenuToggle = useCallback((): void => {
    setMobileMenuOpen((open) => !open)
  }, [])

  const handleMobileMenuClose = useCallback((): void => {
    setMobileMenuOpen(false)
  }, [])

  const handleCommandOpen = useCallback((): void => {
    if (commandPaletteAvailable) {
      setCommandOpen(true)
    }
  }, [commandPaletteAvailable])

  const handleCommandToggle = useCallback(
    (open: boolean): void => {
      if (!commandPaletteAvailable) {
        setCommandOpen(false)
        return
      }
      setCommandOpen(open)
    },
    [commandPaletteAvailable],
  )

  const actionShortcutMap = useMemo(() => {
    const map = new Map<string, string>()
    for (const shortcut of ACTION_SHORTCUTS) {
      if (shortcut.shortcut) {
        map.set(shortcut.shortcut.toLowerCase(), shortcut.path)
      }
    }
    return map
  }, [])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent): void => {
      const shortcut = eventToShortcut(event)
      const shortcutPath = actionShortcutMap.get(shortcut)
      if (shortcutPath) {
        event.preventDefault()
        event.stopPropagation()
        navigate(shortcutPath)
        return
      }

      // Strg+B: Sidebar ein-/ausklappen
      if (event.key.toLowerCase() === 'b' && (event.metaKey || event.ctrlKey) && !event.shiftKey && !event.altKey) {
        event.preventDefault()
        event.stopPropagation()
        handleToggleSidebar()
        return
      }

      // Strg+N: Shortcuts-Liste ein-/ausblenden
      if (event.key.toLowerCase() === 'n' && (event.metaKey || event.ctrlKey) && !event.shiftKey && !event.altKey) {
        event.preventDefault()
        event.stopPropagation()
        handleToggleShortcuts()
        return
      }

      // Strg+K: Command Palette (nur wenn verfügbar)
      if (commandPaletteAvailable && event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey) && !event.shiftKey && !event.altKey) {
        event.preventDefault()
        event.stopPropagation()
        setCommandOpen((open) => !open)
      }
    }

    // Verwende window mit capture phase für bessere Event-Capture
    window.addEventListener('keydown', handleKeyDown, true)
    return () => {
      window.removeEventListener('keydown', handleKeyDown, true)
    }
  }, [actionShortcutMap, commandPaletteAvailable, handleToggleSidebar, handleToggleShortcuts, navigate])

  const commandPaletteProps = useMemo(() => {
    if (!commandPaletteAvailable) {
      return null
    }
    return {
      open: commandOpen,
      onOpenChange: handleCommandToggle,
    }
  }, [commandOpen, commandPaletteAvailable, handleCommandToggle])

  return (
    <div
      className="flex h-screen overflow-hidden bg-background"
      data-mcp-component="app-shell"
      data-mcp-version="1.0.0"
    >
      {/* Desktop Sidebar */}
      <div className="hidden md:block">
        <Suspense fallback={<div className="h-screen w-16 border-r bg-background" />}>
          <Sidebar collapsed={sidebarCollapsed} onToggle={handleToggleSidebar} />
        </Suspense>
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50"
            onClick={handleMobileMenuClose}
            aria-hidden="true"
          />
          {/* Sidebar Panel */}
          <div className="fixed inset-y-0 left-0 z-50 w-72 animate-in slide-in-from-left duration-300">
            <Suspense fallback={<div className="h-full w-full border-r bg-background" />}>
              <Sidebar collapsed={false} onToggle={handleMobileMenuClose} onNavigate={handleMobileMenuClose} />
            </Suspense>
          </div>
        </div>
      )}

      <div className="flex flex-1 flex-col overflow-hidden">
        <Suspense fallback={<div className="h-14 border-b bg-background md:h-16" />}>
          <TopBar
            onCommandOpen={handleCommandOpen}
            commandPaletteEnabled={commandPaletteAvailable}
            onMobileMenuToggle={handleMobileMenuToggle}
            onSidebarToggle={handleToggleSidebar}
            onShortcutsToggle={handleToggleShortcuts}
          />
        </Suspense>

        <main className="flex-1 overflow-y-auto overflow-x-hidden" role="main" aria-label="Main content">
          {children}
        </main>
      </div>

      {commandPaletteProps ? (
        <Suspense fallback={null}>
          <CommandPalette {...commandPaletteProps} />
        </Suspense>
      ) : null}
    </div>
  )

  function eventToShortcut(event: KeyboardEvent): string {
    const parts: string[] = []
    if (event.ctrlKey || event.metaKey) parts.push('ctrl')
    if (event.altKey) parts.push('alt')
    if (event.shiftKey) parts.push('shift')
    parts.push(event.key.toLowerCase())
    return parts.join('+')
  }
}

