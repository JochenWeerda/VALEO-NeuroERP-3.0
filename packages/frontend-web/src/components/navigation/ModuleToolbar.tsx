'use client'

import { useCallback, useEffect, useState } from 'react'
import { clsx } from 'clsx'
import { Link, useNavigate } from '@/app/routing/react-router-compat'
import { ArrowLeft, ChevronLeft, ChevronRight, Home, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

export interface ModuleToolbarProps {
  /** Ziel beim Klick auf "Zurück" (z. B. Modul-Liste). */
  backTarget?: string
  /** Ziel beim Klick auf "Schließen" (z. B. Modul-Start oder Liste). */
  closeTarget?: string
  /** Startseite-Button anzeigen (Link zu /). */
  showHome?: boolean
  /** Optional: Vorheriger Eintrag (z. B. vorheriger Beleg). */
  onPrev?: () => void
  /** Optional: Nächster Eintrag. */
  onNext?: () => void
  /** Optional: Vor/Zurück deaktiviert (z. B. am Anfang/Ende). */
  prevDisabled?: boolean
  nextDisabled?: boolean
  /** Toolbar beim Scrollen nach unten ausblenden, nach oben einblenden. */
  autohide?: boolean
  /** Optionale Überschrift in der Toolbar. */
  title?: React.ReactNode
  /** Zusätzliche Aktionen rechts. */
  actions?: React.ReactNode
  className?: string
}

export function ModuleToolbar({
  backTarget,
  closeTarget,
  showHome = true,
  onPrev,
  onNext,
  prevDisabled,
  nextDisabled,
  autohide = false,
  title,
  actions,
  className,
}: ModuleToolbarProps): JSX.Element | null {
  const navigate = useNavigate()
  const [visible, setVisible] = useState(true)
  const [lastScrollY, setLastScrollY] = useState(0)

  useEffect(() => {
    if (!autohide) return
    const threshold = 60
    const handleScroll = (): void => {
      const y = window.scrollY
      setVisible(y <= 10 || y < lastScrollY || lastScrollY - y > threshold)
      setLastScrollY(y)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [autohide, lastScrollY])

  const handleBack = useCallback((): void => {
    if (backTarget) navigate(backTarget)
    else navigate(-1)
  }, [navigate, backTarget])

  const handleClose = useCallback((): void => {
    if (closeTarget) navigate(closeTarget)
    else navigate(-1)
  }, [navigate, closeTarget])

  const hasNav = Boolean(backTarget ?? closeTarget ?? showHome ?? onPrev ?? onNext ?? title ?? actions)
  if (!hasNav) return null

  return (
    <div
      className={clsx(
        'flex h-11 shrink-0 items-center gap-2 border-b bg-background px-3 transition-transform duration-200',
        autohide && !visible && '-translate-y-full',
        className,
      )}
      role="toolbar"
      aria-label="Modul-Navigation"
    >
      {backTarget != null && (
        <Button variant="ghost" size="sm" onClick={handleBack} aria-label="Zurück">
          <ArrowLeft className="h-4 w-4" />
          <span className="hidden sm:inline">Zurück</span>
        </Button>
      )}
      {closeTarget != null && backTarget !== closeTarget && (
        <Button variant="ghost" size="icon" onClick={handleClose} title="Schließen" aria-label="Schließen">
          <X className="h-4 w-4" />
        </Button>
      )}
      {showHome && (
        <Button variant="ghost" size="icon" title="Zur Startseite" aria-label="Zur Startseite" asChild>
          <Link to="/">
            <Home className="h-4 w-4" />
          </Link>
        </Button>
      )}
      {(onPrev != null || onNext != null) && (
        <div className="flex items-center gap-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={onPrev ?? undefined}
            disabled={prevDisabled}
            aria-label="Vorheriger"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onNext ?? undefined}
            disabled={nextDisabled}
            aria-label="Nächster"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
      {title != null && (
        <div className="min-w-0 flex-1 truncate text-sm font-medium text-foreground">
          {title}
        </div>
      )}
      {actions != null && <div className="ml-auto flex items-center gap-2">{actions}</div>}
    </div>
  )
}
