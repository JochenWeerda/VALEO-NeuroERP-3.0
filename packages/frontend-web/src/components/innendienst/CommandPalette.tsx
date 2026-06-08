/**
 * Command Palette
 *
 * Schnellzugriff auf Aktionen und Navigation via Ctrl+K
 * Optimiert fuer Power-User im Innendienst
 * Metro Design mit Keyboard-Navigation
 */

import { useState, useEffect, useCallback, useMemo, useRef, type ReactNode } from 'react'
import { clsx } from 'clsx'
import { useNavigate } from '@/app/routing/react-router-compat'
import {
  Search,
  ArrowRight,
  Command,
  CornerDownLeft,
  ChevronUp,
  ChevronDown,
} from 'lucide-react'
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog'
import { getDefaultCommands } from '@/components/innendienst/command-palette-data'

export interface CommandItem {
  id: string
  label: string
  description?: string
  icon?: ReactNode
  shortcut?: string
  category: 'navigation' | 'action' | 'search' | 'recent'
  action: () => void
  keywords?: string[]
}

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  additionalCommands?: CommandItem[]
}

export function CommandPalette({
  open,
  onOpenChange,
  additionalCommands = [],
}: CommandPaletteProps) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const allCommands = useMemo(() => {
    return [...getDefaultCommands(navigate), ...additionalCommands]
  }, [navigate, additionalCommands])

  const filteredCommands = useMemo(() => {
    if (!query.trim()) {
      return allCommands
    }

    const lowerQuery = query.toLowerCase()
    return allCommands.filter((cmd) => {
      const labelMatch = cmd.label.toLowerCase().includes(lowerQuery)
      const descMatch = cmd.description?.toLowerCase().includes(lowerQuery)
      const keywordMatch = cmd.keywords?.some((keyword) => keyword.includes(lowerQuery))
      return labelMatch || descMatch || keywordMatch
    })
  }, [allCommands, query])

  const groupedCommands = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {
      action: [],
      navigation: [],
      search: [],
      recent: [],
    }

    filteredCommands.forEach((cmd) => {
      groups[cmd.category]?.push(cmd)
    })

    return groups
  }, [filteredCommands])

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedIndex(0)
      window.setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((index) => Math.min(index + 1, filteredCommands.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((index) => Math.max(index - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action()
          onOpenChange(false)
        }
        break
      case 'Escape':
        e.preventDefault()
        onOpenChange(false)
        break
    }
  }, [filteredCommands, onOpenChange, selectedIndex])

  useEffect(() => {
    const item = listRef.current?.querySelector(`[data-index="${selectedIndex}"]`)
    item?.scrollIntoView({ block: 'nearest' })
  }, [selectedIndex])

  const executeCommand = useCallback((cmd: CommandItem) => {
    cmd.action()
    onOpenChange(false)
  }, [onOpenChange])

  const categoryLabels: Record<string, string> = {
    action: 'Aktionen',
    navigation: 'Navigation',
    search: 'Suche',
    recent: 'Zuletzt verwendet',
  }

  let itemIndex = -1

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg gap-0 overflow-hidden p-0">
        <div className="flex items-center gap-3 border-b px-4 py-3">
          <Search className="h-5 w-5 shrink-0 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            placeholder="Suchen oder Befehl eingeben..."
            className="flex-1 bg-transparent text-base outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden h-6 items-center gap-1 rounded border bg-muted px-2 text-xs text-muted-foreground sm:inline-flex">
            <Command className="h-3 w-3" />K
          </kbd>
        </div>

        <div ref={listRef} className="max-h-[400px] overflow-y-auto py-2">
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-muted-foreground">
              <Search className="mx-auto mb-2 h-8 w-8 opacity-50" />
              <p>Keine Ergebnisse fuer "{query}"</p>
            </div>
          ) : (
            Object.entries(groupedCommands).map(([category, commands]) => {
              if (commands.length === 0) {
                return null
              }

              return (
                <div key={category} className="mb-2">
                  <div className="px-4 py-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {categoryLabels[category]}
                  </div>
                  {commands.map((cmd) => {
                    itemIndex += 1
                    const isSelected = itemIndex === selectedIndex
                    const currentIndex = itemIndex

                    return (
                      <button
                        key={cmd.id}
                        data-index={currentIndex}
                        onClick={() => executeCommand(cmd)}
                        onMouseEnter={() => setSelectedIndex(currentIndex)}
                        className={clsx(
                          'flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors',
                          isSelected ? 'bg-primary/10 text-primary' : 'hover:bg-muted',
                        )}
                      >
                        <span className={clsx('shrink-0', isSelected ? 'text-primary' : 'text-muted-foreground')}>
                          {cmd.icon}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate font-medium">{cmd.label}</p>
                          {cmd.description && (
                            <p className="truncate text-sm text-muted-foreground">{cmd.description}</p>
                          )}
                        </div>
                        {cmd.shortcut && (
                          <kbd className="hidden h-5 shrink-0 items-center gap-0.5 rounded border bg-muted px-1.5 text-xs text-muted-foreground sm:inline-flex">
                            {cmd.shortcut}
                          </kbd>
                        )}
                        {isSelected && <ArrowRight className="h-4 w-4 shrink-0" />}
                      </button>
                    )
                  })}
                </div>
              )
            })
          )}
        </div>

        <div className="flex items-center justify-between border-t bg-muted/50 px-4 py-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <ChevronUp className="h-3 w-3" />
              <ChevronDown className="h-3 w-3" />
              Navigieren
            </span>
            <span className="flex items-center gap-1">
              <CornerDownLeft className="h-3 w-3" />
              Auswaehlen
            </span>
          </div>
          <span>Esc zum Schliessen</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export function useCommandPalette() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen((current) => !current)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { open, setOpen }
}
