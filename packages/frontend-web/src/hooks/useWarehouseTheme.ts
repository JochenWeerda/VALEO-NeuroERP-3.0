/**
 * Warehouse Theme Hook
 *
 * Verwaltet das High-Contrast Warehouse Theme
 * Automatisch aktiviert auf /lager/* Routen
 */

import { useEffect, useCallback, useState } from 'react'
import { useLocation } from '@/app/routing/typed-router'

interface UseWarehouseThemeOptions {
  /** Automatisch aktivieren auf Lager-Routen */
  autoActivate?: boolean
  /** Pfad-Präfixe für Auto-Aktivierung */
  pathPrefixes?: string[]
}

interface UseWarehouseThemeReturn {
  /** Ist das Warehouse Theme aktiv? */
  isActive: boolean
  /** Theme aktivieren */
  activate: () => void
  /** Theme deaktivieren */
  deactivate: () => void
  /** Theme umschalten */
  toggle: () => void
}

const WAREHOUSE_THEME_CLASS = 'theme-warehouse'
const STORAGE_KEY = 'valeo-warehouse-theme-manual'

/**
 * Hook zum Verwalten des Warehouse High-Contrast Themes
 */
export function useWarehouseTheme(
  options: UseWarehouseThemeOptions = {}
): UseWarehouseThemeReturn {
  const {
    autoActivate = true,
    pathPrefixes = ['/lager', '/warehouse', '/wareneingang', '/warenausgang'],
  } = options

  const location = useLocation()
  const [isManuallySet, setIsManuallySet] = useState<boolean | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  })

  // Prüfe ob wir auf einer Lager-Route sind
  const isWarehouseRoute = pathPrefixes.some(prefix =>
    location.pathname.startsWith(prefix)
  )

  // Berechne ob Theme aktiv sein soll
  const shouldBeActive = isManuallySet !== null ? isManuallySet : (autoActivate && isWarehouseRoute)

  const [isActive, setIsActive] = useState(shouldBeActive)

  // Aktiviere/Deaktiviere Theme
  useEffect(() => {
    const root = document.documentElement

    if (shouldBeActive) {
      root.classList.add(WAREHOUSE_THEME_CLASS)
      root.classList.remove('light', 'dark')
    } else {
      root.classList.remove(WAREHOUSE_THEME_CLASS)
    }

    setIsActive(shouldBeActive)

    return () => {
      // Cleanup nur wenn nicht manuell gesetzt
      if (isManuallySet === null) {
        root.classList.remove(WAREHOUSE_THEME_CLASS)
      }
    }
  }, [shouldBeActive, isManuallySet])

  const activate = useCallback(() => {
    setIsManuallySet(true)
    localStorage.setItem(STORAGE_KEY, 'true')
  }, [])

  const deactivate = useCallback(() => {
    setIsManuallySet(false)
    localStorage.setItem(STORAGE_KEY, 'false')
    document.documentElement.classList.remove(WAREHOUSE_THEME_CLASS)
  }, [])

  const toggle = useCallback(() => {
    if (isActive) {
      deactivate()
    } else {
      activate()
    }
  }, [isActive, activate, deactivate])

  return {
    isActive,
    activate,
    deactivate,
    toggle,
  }
}

/**
 * Hook für Warehouse-Seiten die das Theme erzwingen
 */
export function useForceWarehouseTheme(): void {
  useEffect(() => {
    const root = document.documentElement
    root.classList.add(WAREHOUSE_THEME_CLASS)
    root.classList.remove('light', 'dark')

    return () => {
      root.classList.remove(WAREHOUSE_THEME_CLASS)
    }
  }, [])
}
