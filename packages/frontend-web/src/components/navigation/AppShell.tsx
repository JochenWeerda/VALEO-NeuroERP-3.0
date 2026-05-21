import { Suspense, lazy, type ReactNode, useCallback, useEffect, useMemo, useState, useSyncExternalStore } from 'react'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { useActionDispatch } from '@/features/ki-usability/context/ActionDispatchHooks'
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

function subscribeOnline(cb: () => void): () => void {
  window.addEventListener('online', cb)
  window.addEventListener('offline', cb)
  return () => {
    window.removeEventListener('online', cb)
    window.removeEventListener('offline', cb)
  }
}

export function AppShell({ children, enableCommandPalette = true }: AppShellProps): JSX.Element {
  const isOnline = useSyncExternalStore(subscribeOnline, () => navigator.onLine, () => true)
  const actionDispatch = useActionDispatch()
  const commandPaletteFeatureEnabled = useFeature('commandPalette')
  const commandPaletteAvailable = enableCommandPalette && commandPaletteFeatureEnabled
  const [commandOpen, setCommandOpen] = useState<boolean>(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false)
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
    const map = new Map<string, { id: string; path: string }>()
    for (const shortcut of ACTION_SHORTCUTS) {
      if (shortcut.shortcut) {
        map.set(shortcut.shortcut.toLowerCase(), { id: shortcut.id, path: shortcut.path })
      }
    }
    return map
  }, [])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent): void => {
      const shortcut = eventToShortcut(event)
      const shortcutAction = actionShortcutMap.get(shortcut)
      if (shortcutAction) {
        event.preventDefault()
        event.stopPropagation()
        void actionDispatch.dispatch(shortcutAction.id, { path: shortcutAction.path })
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
  }, [actionDispatch, actionShortcutMap, commandPaletteAvailable, handleToggleSidebar, handleToggleShortcuts])

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

      {/* Mobile Sidebar Overlay — bottom-sheet on small screens */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true" aria-label="Navigationsmenü">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50"
            onClick={handleMobileMenuClose}
            aria-hidden="true"
          />
          {/* Bottom sheet on mobile (< sm), side panel on tablet (sm-md) */}
          <div className="fixed inset-y-0 left-0 z-50 w-72 animate-in slide-in-from-left duration-300 sm:block hidden">
            <Suspense fallback={<div className="h-full w-full border-r bg-background" />}>
              <Sidebar collapsed={false} onToggle={handleMobileMenuClose} onNavigate={handleMobileMenuClose} />
            </Suspense>
          </div>
          <div className="fixed inset-x-0 bottom-0 z-50 max-h-[80vh] animate-in slide-in-from-bottom duration-300 sm:hidden overflow-y-auto rounded-t-2xl">
            <Suspense fallback={<div className="h-96 w-full rounded-t-2xl bg-background" />}>
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

        {!isOnline && (
          <div
            role="status"
            aria-live="polite"
            className="flex items-center justify-center gap-2 bg-orange-500 px-4 py-2 text-sm font-medium text-white"
          >
            <span aria-hidden="true">⚠</span>
            Keine Internetverbindung — Änderungen werden gespeichert, sobald die Verbindung wiederhergestellt ist.
          </div>
        )}

        <main
          className="flex-1 overflow-y-auto overflow-x-hidden"
          role="main"
          aria-label="Main content"
          data-testid="page-root"
        >
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

