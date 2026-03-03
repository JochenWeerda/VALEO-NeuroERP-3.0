import { type ReactNode, useCallback, useEffect, useMemo, useState } from 'react'
import { CommandPalette } from './CommandPalette'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useFeature } from '@/hooks/useFeature'

interface AppShellProps {
  children: ReactNode
  enableCommandPalette?: boolean
}

export const appShellMCP = createMCPMetadata('AppShell', 'navigation', {
  accessibility: {
    role: 'application',
    ariaLabel: 'VALEO NeuroERP Main Application',
    focusable: false,
    keyboardShortcuts: ['Ctrl+K', 'Ctrl+B', '/'],
  },
  intent: {
    purpose: 'Main application navigation and layout',
    userActions: ['navigate', 'search', 'command'],
    businessDomain: 'core',
  },
  mcpHints: {
    autoFillable: false,
    explainable: true,
    testable: true,
    contextAware: true,
  },
})

export function AppShell({ children, enableCommandPalette = true }: AppShellProps): JSX.Element {
  const commandPaletteFeatureEnabled = useFeature('commandPalette')
  const commandPaletteAvailable = enableCommandPalette && commandPaletteFeatureEnabled
  const [commandOpen, setCommandOpen] = useState<boolean>(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false)

  const handleToggleSidebar = useCallback((): void => {
    setSidebarCollapsed((collapsed) => !collapsed)
  }, [])

  const handleToggleShortcuts = useCallback((): void => {
    // Zyklische Schaltlogik: always â†’ hover â†’ hidden â†’ always
    // Warte kurz, falls die Funktion noch nicht initialisiert ist
    const cycleMode = (): void => {
      if (typeof (window as any).__cycleShortcutDisplayMode === 'function') {
        (window as any).__cycleShortcutDisplayMode()
      } else {
        // Retry nach kurzer VerzÃ¶gerung
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

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent): void => {
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

      // Strg+K: Command Palette (nur wenn verfÃ¼gbar)
      if (commandPaletteAvailable && event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey) && !event.shiftKey && !event.altKey) {
        event.preventDefault()
        event.stopPropagation()
        setCommandOpen((open) => !open)
      }
    }

    // Verwende window mit capture phase fÃ¼r bessere Event-Capture
    window.addEventListener('keydown', handleKeyDown, true)
    return () => {
      window.removeEventListener('keydown', handleKeyDown, true)
    }
  }, [commandPaletteAvailable, handleToggleSidebar, handleToggleShortcuts])

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
        <Sidebar collapsed={sidebarCollapsed} onToggle={handleToggleSidebar} />
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
            <Sidebar collapsed={false} onToggle={handleMobileMenuClose} onNavigate={handleMobileMenuClose} />
          </div>
        </div>
      )}

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar
          onCommandOpen={handleCommandOpen}
          commandPaletteEnabled={commandPaletteAvailable}
          onMobileMenuToggle={handleMobileMenuToggle}
          onSidebarToggle={handleToggleSidebar}
          onShortcutsToggle={handleToggleShortcuts}
        />

        <main className="flex-1 overflow-y-auto overflow-x-hidden" role="main" aria-label="Main content">
          {children}
        </main>
      </div>

      {commandPaletteProps ? <CommandPalette {...commandPaletteProps} /> : null}
    </div>
  )
}
