import { Suspense, lazy, useEffect, useState, useCallback, useRef } from 'react'
import { clsx } from 'clsx'
import { Link } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Command as CommandIcon, Check, HelpCircle, Home, Keyboard, LogOut, Menu, Moon, PanelLeft, Search, Settings, Sparkles, Sun, User } from 'lucide-react'
import { useFeature } from '@/hooks/useFeature'
import { useTheme } from '@/hooks/useTheme'
import { availableLanguages, loadLanguage } from '@/i18n/config'

interface TopBarProps {
  onCommandOpen?: () => void
  commandPaletteEnabled?: boolean
  onMobileMenuToggle?: () => void
  onSidebarToggle?: () => void
  onShortcutsToggle?: () => void
}

const NotificationCenter = lazy(() =>
  import('@/components/ui/notification-center').then((module) => ({ default: module.NotificationCenter })),
)

const VoiceButton = lazy(() =>
  import('@/features/ki-usability').then((module) => ({ default: module.VoiceButton })),
)


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
      <Keyboard className={clsx(
        'h-5 w-5',
        displayMode === 'hidden' && 'opacity-50',
        displayMode === 'hover' && 'opacity-75'
      )} />
      <span className="sr-only">Shortcuts</span>
    </Button>
  )
}

function LanguageSelector(): JSX.Element {
  const { i18n } = useTranslation()
  const [switching, setSwitching] = useState(false)
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const activeLangs = availableLanguages.filter(l => l.available)
  const currentLang = availableLanguages.find(l => l.code === i18n.language)

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent): void => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  const handleSwitch = useCallback(async (code: string) => {
    if (code === i18n.language) return
    setSwitching(true)
    try {
      await loadLanguage(code)
      setOpen(false)
    } finally {
      setSwitching(false)
    }
  }, [i18n.language])

  return (
    <div className="relative hidden sm:block" ref={menuRef}>
      <Button
        variant="ghost"
        size="icon"
        className="text-base"
        title={currentLang?.name ?? 'Language'}
        disabled={switching}
        onClick={() => setOpen((current) => !current)}
      >
        {switching ? (
          <span className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        ) : (
          <span className="text-sm font-medium">{(currentLang?.code ?? 'de').toUpperCase()}</span>
        )}
        <span className="sr-only">Language</span>
      </Button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-44 rounded-lg border bg-popover p-1 shadow-lg">
          <div className="px-2 py-1 text-xs text-muted-foreground">Sprache / Language</div>
          <div className="my-1 h-px bg-border" />
          {activeLangs.map((lang) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => void handleSwitch(lang.code)}
              className="flex w-full cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent"
            >
              <span>{lang.flag}</span>
              <span className="flex-1">{lang.name}</span>
              {lang.code === i18n.language && <Check className="h-4 w-4 text-primary" />}
            </button>
          ))}
        </div>
      )}
    </div>
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
  const voiceControlEnabled = useFeature('voiceControl')
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)
  const user = {
    name: 'Test Admin',
    email: 'test-admin@valeo.local',
  }

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent): void => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  const handleSearchClick = (): void => {
    if (!commandPaletteEnabled) {
      return
    }
    onCommandOpen?.()
  }

  return (
    <header
      className="flex h-[var(--toolbar-height,56px)] items-center gap-2 border-b border-border bg-card/90 px-3 shadow-sm backdrop-blur md:gap-4 md:px-6"
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

      <Link to="/" className="md:hidden flex items-center" aria-label="Zur Startseite">
        <img
          src="/branding/valeo-erp-logo.png"
          alt="VALEO ERP Logo"
          className="h-8 w-auto max-w-[132px] object-contain"
        />
      </Link>
      <Button variant="ghost" size="icon" className="hidden md:inline-flex" title="Zur Startseite" aria-label="Zur Startseite" asChild>
        <Link to="/">
          <Home className="h-5 w-5" />
        </Link>
      </Button>

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

      {/* Sprachsteuerung (KI Usability) – Feature-Flag: voiceControl */}
      {voiceControlEnabled && (
        <Suspense fallback={null}>
          <VoiceButton variant="ghost" size="icon" className="hidden sm:inline-flex" />
        </Suspense>
      )}

      <Suspense fallback={null}>
        <NotificationCenter />
      </Suspense>

      <LanguageSelector />

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

      <div className="relative" ref={userMenuRef}>
        <Button
          variant="ghost"
          size="icon"
          className="rounded-full"
          onClick={() => setUserMenuOpen((current) => !current)}
        >
          <User className="h-5 w-5" />
          <span className="sr-only">User menu</span>
        </Button>
        {userMenuOpen && (
          <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border bg-popover p-1 shadow-lg">
            <div className="px-3 py-2">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
            <div className="my-1 h-px bg-border" />
            <button type="button" className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-accent">
              <User className="h-4 w-4" />
              <span>Profil</span>
            </button>
            <button type="button" className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-accent">
              <Settings className="h-4 w-4" />
              <span>Einstellungen</span>
            </button>
            <div className="my-1 h-px bg-border" />
            <button type="button" className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-destructive hover:bg-accent">
              <LogOut className="h-4 w-4" />
              <span>Abmelden</span>
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

