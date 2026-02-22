import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { NotificationCenter } from '@/components/ui/notification-center'
import { Command as CommandIcon, HelpCircle, Keyboard, LogOut, Menu, Moon, PanelLeft, Search, Settings, Sparkles, Sun, User } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

interface TopBarProps {
  onCommandOpen?: () => void
  commandPaletteEnabled?: boolean
  onMobileMenuToggle?: () => void
  onSidebarToggle?: () => void
  onShortcutsToggle?: () => void
}

export const topBarMCP = createMCPMetadata('TopBar', 'navigation', {
  accessibility: {
    role: 'banner',
    ariaLabel: 'Top navigation bar',
    keyboardShortcuts: ['Ctrl+K', '/'],
  },
  intent: {
    purpose: 'Global search and user actions',
    userActions: ['search', 'open-command-palette', 'user-menu'],
    businessDomain: 'core',
  },
  mcpHints: {
    explainable: true,
    contextAware: true,
  },
})

// Komponente für Shortcuts-Toggle-Button mit dynamischem Tooltip
function ShortcutsToggleButton({ onToggle }: { onToggle: () => void }): JSX.Element {
  const [displayMode, setDisplayMode] = useState<'always' | 'hover' | 'hidden'>('always')
  const [tooltip, setTooltip] = useState('Shortcuts-Liste (Strg+N)')

  useEffect(() => {
    // Lade aktuellen Modus
    const updateMode = (): void => {
      if (typeof (window as any).__getShortcutDisplayMode === 'function') {
        const mode = (window as any).__getShortcutDisplayMode() || 'always'
        setDisplayMode(mode)
        
        // Setze Tooltip basierend auf Modus
        const tooltips = {
          always: 'Shortcuts-Liste: Immer anzeigen (Strg+N)',
          hover: 'Shortcuts-Liste: Bei Hover anzeigen (Strg+N)',
          hidden: 'Shortcuts-Liste: Ausgeblendet (Strg+N)',
        }
        setTooltip(tooltips[mode as keyof typeof tooltips] || 'Shortcuts-Liste (Strg+N)')
      }
    }

    // Initial load
    updateMode()

    // Poll für Änderungen (alle 500ms)
    const interval = setInterval(updateMode, 500)

    return () => clearInterval(interval)
  }, [])

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onToggle}
      className="hidden md:inline-flex"
      title={tooltip}
      aria-label="Shortcuts-Liste"
    >
      <Keyboard className={cn(
        'h-5 w-5',
        displayMode === 'hidden' && 'opacity-50',
        displayMode === 'hover' && 'opacity-75'
      )} />
      <span className="sr-only">Shortcuts</span>
    </Button>
  )
}

export function TopBar({ 
  onCommandOpen, 
  commandPaletteEnabled = true, 
  onMobileMenuToggle,
  onSidebarToggle,
  onShortcutsToggle,
}: TopBarProps): JSX.Element {
  const { isDark, toggleTheme } = useTheme()
  const user = {
    name: 'Test Admin',
    email: 'test-admin@valeo.local',
  }

  const handleSearchClick = (): void => {
    if (!commandPaletteEnabled) {
      return
    }
    onCommandOpen?.()
  }

  return (
    <header
      className="flex h-14 md:h-16 items-center gap-2 md:gap-4 border-b bg-background px-3 md:px-6"
      role="banner"
      data-mcp-component="top-bar"
    >
      {/* Mobile Hamburger */}
      {onMobileMenuToggle && (
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMobileMenuToggle}
          aria-label="Menü öffnen"
        >
          <Menu className="h-5 w-5" />
        </Button>
      )}

      <div className="flex-1 max-w-md">
        <Button
          variant="outline"
          className="w-full justify-start text-muted-foreground"
          onClick={handleSearchClick}
          disabled={!commandPaletteEnabled}
        >
          <Search className="mr-2 h-4 w-4" />
          <span>Suche... (Ctrl+K)</span>
          <kbd className="ml-auto hidden rounded bg-muted px-2 py-0.5 text-xs lg:inline">
            <CommandIcon className="h-3 w-3" />
            K
          </kbd>
        </Button>
      </div>

      <Button
        variant="ghost"
        size="icon"
        title="Ask VALEO - AI-Hilfe (Phase 3)"
        className="hidden sm:inline-flex"
        data-mcp-action="ask-valeo"
        data-mcp-intent="ai-assistance"
      >
        <Sparkles className="h-5 w-5 text-primary" />
        <span className="sr-only">AI-Hilfe</span>
      </Button>

      {/* Sidebar Toggle (Strg+B) */}
      {onSidebarToggle && (
        <Button
          variant="ghost"
          size="icon"
          onClick={onSidebarToggle}
          className="hidden md:inline-flex"
          title="Seitenleiste ein-/ausklappen (Strg+B)"
          aria-label="Seitenleiste ein-/ausklappen"
        >
          <PanelLeft className="h-5 w-5" />
          <span className="sr-only">Seitenleiste</span>
        </Button>
      )}

      {/* Shortcuts Help Toggle (Strg+N) */}
      {onShortcutsToggle && (
        <ShortcutsToggleButton onToggle={onShortcutsToggle} />
      )}

      <NotificationCenter />

      <Button
        variant="ghost"
        size="icon"
        onClick={toggleTheme}
        className="hidden sm:inline-flex"
        title={isDark ? 'Zum hellen Modus wechseln' : 'Zum dunklen Modus wechseln'}
        aria-label={isDark ? 'Zum hellen Modus wechseln' : 'Zum dunklen Modus wechseln'}
      >
        {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
      </Button>

      <Button variant="ghost" size="icon" title="Hilfe" className="hidden lg:inline-flex">
        <HelpCircle className="h-5 w-5" />
        <span className="sr-only">Hilfe</span>
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="rounded-full">
            <User className="h-5 w-5" />
            <span className="sr-only">User menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            <span>Profil</span>
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            <span>Einstellungen</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive">
            <LogOut className="mr-2 h-4 w-4" />
            <span>Abmelden</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
