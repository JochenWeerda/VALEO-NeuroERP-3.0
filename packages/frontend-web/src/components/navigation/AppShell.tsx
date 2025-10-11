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
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false)

  const handleToggleSidebar = useCallback((): void => {
    setSidebarCollapsed((collapsed) => !collapsed)
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
    if (!commandPaletteAvailable) {
      setCommandOpen(false)
      return
    }

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        setCommandOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [commandPaletteAvailable])

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
      <Sidebar collapsed={sidebarCollapsed} onToggle={handleToggleSidebar} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar
          onCommandOpen={handleCommandOpen}
          commandPaletteEnabled={commandPaletteAvailable}
        />

        <main className="flex-1 overflow-y-auto overflow-x-hidden" role="main" aria-label="Main content">
          {children}
        </main>
      </div>

      {commandPaletteProps ? <CommandPalette {...commandPaletteProps} /> : null}
    </div>
  )
}
