import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Command as CommandIcon, HelpCircle, LogOut, Search, Settings, Sparkles, User } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'

interface TopBarProps {
  onCommandOpen?: () => void
  commandPaletteEnabled?: boolean
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

export function TopBar({ onCommandOpen, commandPaletteEnabled = true }: TopBarProps): JSX.Element {
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
      className="flex h-16 items-center gap-4 border-b bg-background px-6"
      role="banner"
      data-mcp-component="top-bar"
    >
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
        data-mcp-action="ask-valeo"
        data-mcp-intent="ai-assistance"
      >
        <Sparkles className="h-5 w-5 text-primary" />
        <span className="sr-only">AI-Hilfe</span>
      </Button>

      <Button variant="ghost" size="icon" title="Hilfe">
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
