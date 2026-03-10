/**
 * FIBU Suite – Layout mit durchgehendem Ribbon (Desktop), Card-Dashboard (Mobile) und Dark-Mode-Umschalter.
 * Wird unter /fibu-suite und allen Kind-Routen gerendert.
 */

import { useState, useEffect, type ReactNode } from 'react'
import { clsx } from 'clsx'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import {
  Euro,
  Moon,
  Sun,
  Smartphone,
  Monitor,
  Home,
} from 'lucide-react'
import { FIBU_SUITE_ITEMS } from '@/app/navigation/fibu-suite'

const FIBU_SUITE_STORAGE_VIEW = 'fibu-suite-view'
const FIBU_SUITE_STORAGE_THEME = 'fibu-suite-theme'

type ViewMode = 'desktop' | 'mobile'
type ThemeMode = 'light' | 'dark'

function getStoredView(): ViewMode {
  try {
    const v = localStorage.getItem(FIBU_SUITE_STORAGE_VIEW)
    if (v === 'desktop' || v === 'mobile') return v
  } catch {
    // ignore
  }
  return window.matchMedia('(min-width: 1024px)').matches ? 'desktop' : 'mobile'
}

function getStoredTheme(): ThemeMode {
  try {
    const v = localStorage.getItem(FIBU_SUITE_STORAGE_THEME)
    if (v === 'light' || v === 'dark') return v
  } catch {
    // ignore
  }
  return 'light'
}

function getSuitePath(child: { path?: string; module?: string }): string | null {
  if (!child.path) return null
  const p = child.path.startsWith('/') ? child.path.slice(1) : child.path
  if (p.startsWith('fibu/')) return p.replace('fibu/', '')
  if (p.startsWith('finance/')) return `finance/${p.replace('finance/', '')}`
  if (p.startsWith('export/')) return p.replace('export/', '')
  if (p.startsWith('pos/')) return p
  return p
}

interface FibuSuiteLayoutProps {
  children?: ReactNode
}

export default function FibuSuiteLayout({ children }: FibuSuiteLayoutProps): JSX.Element {
  const [viewMode, setViewMode] = useState<ViewMode>(getStoredView)
  const [theme, setTheme] = useState<ThemeMode>(getStoredTheme)
  const location = useLocation()

  const suiteBase = '/fibu-suite'

  useEffect(() => {
    try {
      localStorage.setItem(FIBU_SUITE_STORAGE_VIEW, viewMode)
    } catch {
      // ignore
    }
  }, [viewMode])

  useEffect(() => {
    try {
      localStorage.setItem(FIBU_SUITE_STORAGE_THEME, theme)
    } catch {
      // ignore
    }
  }, [theme])

  const setView = (v: ViewMode): void => setViewMode(v)
  const setThemeMode = (t: ThemeMode): void => setTheme(t)

  const ribbonLinks = FIBU_SUITE_ITEMS
    .map((child) => {
      const path = getSuitePath(child)
      if (!path) return null
      return { ...child, suitePath: `${suiteBase}/${path}` }
    })
    .filter((x): x is NonNullable<typeof x> => x != null)
    .slice(0, 20)

  return (
    <div
      className={clsx(
        'flex h-full flex-col min-h-0',
        theme === 'dark' && 'dark bg-slate-950 text-slate-100',
      )}
    >
      {/* Top Bar: Logo, View-Toggle, Dark-Mode */}
      <div className="flex items-center justify-between gap-4 border-b bg-muted/40 px-4 py-2 shrink-0">
        <Link to={suiteBase} className="flex items-center gap-2 font-semibold">
          <Euro className="h-6 w-6 text-primary" />
          <span>FIBU Suite</span>
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Ansicht:</span>
          <Button
            variant={viewMode === 'desktop' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setView('desktop')}
            aria-label="Desktop mit Ribbon"
          >
            <Monitor className="h-4 w-4 mr-1" />
            Desktop
          </Button>
          <Button
            variant={viewMode === 'mobile' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setView('mobile')}
            aria-label="Cards-Dashboard"
          >
            <Smartphone className="h-4 w-4 mr-1" />
            Cards
          </Button>
          <span className="text-xs text-muted-foreground ml-2">Theme:</span>
          <Button
            variant={theme === 'light' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setThemeMode('light')}
            aria-label="Hell"
          >
            <Sun className="h-4 w-4" />
          </Button>
          <Button
            variant={theme === 'dark' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setThemeMode('dark')}
            aria-label="Dark"
          >
            <Moon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Desktop: Ribbon mit START + Links zu allen Masken */}
      {viewMode === 'desktop' && (
        <div className="border-b bg-muted/30 shrink-0">
          <div className="flex flex-wrap items-center gap-1 px-4 py-2">
            <Link to={suiteBase}>
              <Button variant="ghost" size="sm" className="gap-1.5">
                <Home className="h-4 w-4" /> START
              </Button>
            </Link>
            {ribbonLinks.map((child) => {
              const Icon = child.icon
              return (
                <Link key={child.id} to={child.suitePath}>
                  <Button
                    variant={location.pathname === child.suitePath ? 'secondary' : 'ghost'}
                    size="sm"
                    className="gap-1.5"
                  >
                    <Icon className="h-4 w-4" />
                    {child.label}
                  </Button>
                </Link>
              )
            })}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-auto">
        {children ?? <Outlet />}
      </div>
    </div>
  )
}
