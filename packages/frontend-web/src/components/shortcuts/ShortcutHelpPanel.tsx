/**
 * Shortcut-Help-Panel
 * Einklappbares Panel am rechten Bildschirmrand mit Shortcut-Übersicht
 * Unterstützt verschiedene Anzeige-Modi (Anfänger/Geübter/Experte)
 */

import { useState, useEffect } from 'react'
import { clsx } from 'clsx'
import { ChevronLeft, Keyboard } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export type ShortcutDefinition = {
  key: string
  label: string
  description: string
  category?: string
}

export type ShortcutDisplayMode = 'always' | 'hover' | 'hidden'

type ShortcutHelpPanelProps = {
  shortcuts: ShortcutDefinition[]
  displayMode?: ShortcutDisplayMode
  onDisplayModeChange?: (mode: ShortcutDisplayMode) => void
  className?: string
}

export function ShortcutHelpPanel({
  shortcuts,
  displayMode = 'always',
  onDisplayModeChange,
  className,
}: ShortcutHelpPanelProps): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(false) // Standardmäßig eingeklappt
  
  // Expose toggle function globally for Strg+N
  useEffect(() => {
    const toggleFn = (): void => {
      setIsExpanded((prev) => !prev)
    }
    const expandFn = (): void => {
      setIsExpanded(true)
    }
    ;(window as any).__toggleShortcutHelpPanel = toggleFn
    ;(window as any).__expandShortcutHelpPanel = expandFn
    
    return () => {
      delete (window as any).__toggleShortcutHelpPanel
      delete (window as any).__expandShortcutHelpPanel
    }
  }, [])
  const [isHovering, setIsHovering] = useState(false)

  // Lade gespeicherte Präferenz
  useEffect(() => {
    const saved = localStorage.getItem('shortcut-help-display-mode')
    if (saved && onDisplayModeChange) {
      onDisplayModeChange(saved as ShortcutDisplayMode)
    }
  }, [onDisplayModeChange])

  // Gruppiere Shortcuts nach Kategorie
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    const category = shortcut.category || 'Allgemein'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(shortcut)
    return acc
  }, {} as Record<string, ShortcutDefinition[]>)

  // Rendere nichts wenn hidden
  if (displayMode === 'hidden') {
    return <></>
  }

  // Für hover-Modus: nur bei Hover anzeigen
  // Wenn nicht expanded, komplett ausblenden
  const shouldShow = isExpanded && (displayMode === 'always' || (displayMode === 'hover' && isHovering))

  // Wenn komplett ausgeblendet, nichts rendern
  if (!isExpanded && displayMode !== 'always') {
    return <></>
  }

  return (
    <div
      className={clsx(
        'fixed right-0 top-1/2 -translate-y-1/2 z-50 transition-all duration-300',
        shouldShow ? 'translate-x-0' : 'translate-x-full',
        !isExpanded && 'translate-x-full', // Komplett ausblenden wenn collapsed
        className
      )}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <Card
        className={clsx(
          'w-80 max-h-[80vh] overflow-hidden flex flex-col shadow-lg',
          'bg-white/95 backdrop-blur-sm border-r-0 rounded-l-lg',
          displayMode === 'hover' && 'opacity-90'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b bg-green-50">
          <div className="flex items-center gap-2">
            <Keyboard className="h-4 w-4 text-green-700" />
            <h3 className="font-semibold text-sm text-green-900">Tastenkürzel</h3>
          </div>
          <div className="flex items-center gap-1">
            {/* Display-Mode Toggle */}
            <select
              value={displayMode}
              onChange={(e) => {
                const mode = e.target.value as ShortcutDisplayMode
                localStorage.setItem('shortcut-help-display-mode', mode)
                if (onDisplayModeChange) {
                  onDisplayModeChange(mode)
                }
              }}
              className="text-xs px-2 py-1 rounded border bg-white"
              onClick={(e) => e.stopPropagation()}
            >
              <option value="always">Immer</option>
              <option value="hover">Bei Hover</option>
              <option value="hidden">Ausblenden</option>
            </select>
            {/* Expand/Collapse */}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronLeft className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4 rotate-180" />
              )}
            </Button>
          </div>
        </div>

        {/* Content */}
        {isExpanded && (
          <div className="overflow-y-auto p-3 space-y-4">
            {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h4 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                  {category}
                </h4>
                <div className="space-y-2">
                  {categoryShortcuts.map((shortcut) => (
                    <div
                      key={shortcut.key}
                      className="flex items-start justify-between gap-2 text-sm"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{shortcut.label}</div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {shortcut.description}
                        </div>
                      </div>
                      <kbd className="px-2 py-1 text-xs font-mono bg-gray-100 border border-gray-300 rounded shadow-sm text-gray-700 whitespace-nowrap">
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

/**
 * Button mit Shortcut-Hint (für Rechtsklick/Hover)
 */
type ShortcutHintButtonProps = {
  shortcut?: string
  children: React.ReactNode
  className?: string
}

export function ShortcutHintButton({
  shortcut,
  children,
  className,
}: ShortcutHintButtonProps): JSX.Element {
  const [showHint, setShowHint] = useState(false)

  // Lade Display-Mode
  const displayMode = (localStorage.getItem('shortcut-help-display-mode') ||
    'always') as ShortcutDisplayMode

  if (!shortcut || displayMode === 'hidden') {
    return <>{children}</>
  }

  return (
    <div
      className={clsx('relative', className)}
      onMouseEnter={() => displayMode === 'hover' && setShowHint(true)}
      onMouseLeave={() => setShowHint(false)}
      onContextMenu={(e) => {
        if (displayMode === 'hover') {
          e.preventDefault()
          setShowHint(!showHint)
        }
      }}
    >
      {children}
      {showHint && (
        <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded shadow-lg whitespace-nowrap z-50">
          <kbd className="font-mono">{shortcut}</kbd>
        </div>
      )}
    </div>
  )
}

