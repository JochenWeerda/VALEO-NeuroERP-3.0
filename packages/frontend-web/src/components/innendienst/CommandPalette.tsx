/**
 * Command Palette
 *
 * Schnellzugriff auf Aktionen und Navigation via Ctrl+K
 * Optimiert für Power-User im Innendienst
 * Metro Design mit Keyboard-Navigation
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  Search,
  FileText,
  Users,
  ShoppingCart,
  Package,
  Truck,
  BarChart3,
  Settings,
  Plus,
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

export interface CommandItem {
  id: string
  label: string
  description?: string
  icon?: React.ReactNode
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

// Standard-Kommandos
const createDefaultCommands = (navigate: (path: string) => void): CommandItem[] => [
  // Navigation
  {
    id: 'nav-dashboard',
    label: 'Dashboard',
    description: 'Zur Startseite',
    icon: <BarChart3 className="h-4 w-4" />,
    category: 'navigation',
    action: () => navigate('/'),
    keywords: ['home', 'start', 'übersicht'],
  },
  {
    id: 'nav-customers',
    label: 'Kunden',
    description: 'Kundenstamm öffnen',
    icon: <Users className="h-4 w-4" />,
    shortcut: 'G K',
    category: 'navigation',
    action: () => navigate('/crm/kunden-stamm'),
    keywords: ['crm', 'kontakte', 'adressen'],
  },
  {
    id: 'nav-orders',
    label: 'Aufträge',
    description: 'Auftragsliste öffnen',
    icon: <ShoppingCart className="h-4 w-4" />,
    shortcut: 'G A',
    category: 'navigation',
    action: () => navigate('/sales/auftraege-liste'),
    keywords: ['verkauf', 'bestellungen', 'orders'],
  },
  {
    id: 'nav-invoices',
    label: 'Rechnungen',
    description: 'Rechnungsliste öffnen',
    icon: <FileText className="h-4 w-4" />,
    shortcut: 'G R',
    category: 'navigation',
    action: () => navigate('/sales/rechnungen-liste'),
    keywords: ['finanzen', 'buchhaltung', 'belege'],
  },
  {
    id: 'nav-inventory',
    label: 'Lagerbestand',
    description: 'Bestandsübersicht öffnen',
    icon: <Package className="h-4 w-4" />,
    shortcut: 'G L',
    category: 'navigation',
    action: () => navigate('/lager/bestandsuebersicht'),
    keywords: ['warehouse', 'artikel', 'stock'],
  },
  {
    id: 'nav-deliveries',
    label: 'Lieferungen',
    description: 'Lieferungsliste öffnen',
    icon: <Truck className="h-4 w-4" />,
    category: 'navigation',
    action: () => navigate('/sales/lieferungen-liste'),
    keywords: ['versand', 'transport', 'logistik'],
  },
  {
    id: 'nav-settings',
    label: 'Einstellungen',
    description: 'Systemeinstellungen',
    icon: <Settings className="h-4 w-4" />,
    category: 'navigation',
    action: () => navigate('/einstellungen'),
    keywords: ['config', 'optionen', 'profil'],
  },

  // Aktionen
  {
    id: 'action-new-customer',
    label: 'Neuer Kunde',
    description: 'Kunde anlegen',
    icon: <Plus className="h-4 w-4" />,
    shortcut: 'N K',
    category: 'action',
    action: () => navigate('/verkauf/kunde-neu'),
    keywords: ['erstellen', 'anlegen', 'create'],
  },
  {
    id: 'action-new-order',
    label: 'Neuer Auftrag',
    description: 'Auftrag erstellen',
    icon: <Plus className="h-4 w-4" />,
    shortcut: 'N A',
    category: 'action',
    action: () => navigate('/sales/order-editor'),
    keywords: ['erstellen', 'anlegen', 'create'],
  },
  {
    id: 'action-new-offer',
    label: 'Neues Angebot',
    description: 'Angebot erstellen',
    icon: <Plus className="h-4 w-4" />,
    shortcut: 'N O',
    category: 'action',
    action: () => navigate('/sales/angebot-erstellen'),
    keywords: ['erstellen', 'anlegen', 'quote'],
  },
  {
    id: 'action-new-invoice',
    label: 'Neue Rechnung',
    description: 'Rechnung erstellen',
    icon: <Plus className="h-4 w-4" />,
    shortcut: 'N R',
    category: 'action',
    action: () => navigate('/finance/invoice-form'),
    keywords: ['erstellen', 'anlegen', 'billing'],
  },
]

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

  // Alle Kommandos zusammenführen
  const allCommands = useMemo(() => {
    const defaults = createDefaultCommands(navigate)
    return [...defaults, ...additionalCommands]
  }, [navigate, additionalCommands])

  // Gefilterte Kommandos
  const filteredCommands = useMemo(() => {
    if (!query.trim()) {
      return allCommands
    }

    const lowerQuery = query.toLowerCase()
    return allCommands.filter(cmd => {
      const labelMatch = cmd.label.toLowerCase().includes(lowerQuery)
      const descMatch = cmd.description?.toLowerCase().includes(lowerQuery)
      const keywordMatch = cmd.keywords?.some(kw => kw.includes(lowerQuery))
      return labelMatch || descMatch || keywordMatch
    })
  }, [allCommands, query])

  // Gruppierte Kommandos
  const groupedCommands = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {
      action: [],
      navigation: [],
      search: [],
      recent: [],
    }

    filteredCommands.forEach(cmd => {
      groups[cmd.category]?.push(cmd)
    })

    return groups
  }, [filteredCommands])

  // Reset bei Öffnen
  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  // Keyboard Navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(i => Math.min(i + 1, filteredCommands.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(i => Math.max(i - 1, 0))
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
  }, [filteredCommands, selectedIndex, onOpenChange])

  // Scroll zu ausgewähltem Element
  useEffect(() => {
    const item = listRef.current?.querySelector(`[data-index="${selectedIndex}"]`)
    item?.scrollIntoView({ block: 'nearest' })
  }, [selectedIndex])

  // Ausgewähltes Kommando ausführen
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
      <DialogContent className="p-0 gap-0 max-w-lg overflow-hidden">
        {/* Suchfeld */}
        <div className="flex items-center gap-3 px-4 py-3 border-b">
          <Search className="h-5 w-5 text-muted-foreground shrink-0" />
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
          <kbd className="hidden sm:inline-flex h-6 items-center gap-1 rounded border bg-muted px-2 text-xs text-muted-foreground">
            <Command className="h-3 w-3" />K
          </kbd>
        </div>

        {/* Kommandoliste */}
        <div ref={listRef} className="max-h-[400px] overflow-y-auto py-2">
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-muted-foreground">
              <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Keine Ergebnisse für "{query}"</p>
            </div>
          ) : (
            Object.entries(groupedCommands).map(([category, commands]) => {
              if (commands.length === 0) return null

              return (
                <div key={category} className="mb-2">
                  <div className="px-4 py-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {categoryLabels[category]}
                  </div>
                  {commands.map((cmd) => {
                    itemIndex++
                    const isSelected = itemIndex === selectedIndex
                    const currentIndex = itemIndex

                    return (
                      <button
                        key={cmd.id}
                        data-index={currentIndex}
                        onClick={() => executeCommand(cmd)}
                        onMouseEnter={() => setSelectedIndex(currentIndex)}
                        className={cn(
                          'w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors',
                          isSelected ? 'bg-primary/10 text-primary' : 'hover:bg-muted'
                        )}
                      >
                        <span className={cn(
                          'shrink-0',
                          isSelected ? 'text-primary' : 'text-muted-foreground'
                        )}>
                          {cmd.icon}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{cmd.label}</p>
                          {cmd.description && (
                            <p className="text-sm text-muted-foreground truncate">
                              {cmd.description}
                            </p>
                          )}
                        </div>
                        {cmd.shortcut && (
                          <kbd className="hidden sm:inline-flex shrink-0 h-5 items-center gap-0.5 rounded border bg-muted px-1.5 text-xs text-muted-foreground">
                            {cmd.shortcut}
                          </kbd>
                        )}
                        {isSelected && (
                          <ArrowRight className="h-4 w-4 shrink-0" />
                        )}
                      </button>
                    )
                  })}
                </div>
              )
            })
          )}
        </div>

        {/* Footer mit Tastatur-Hinweisen */}
        <div className="flex items-center justify-between px-4 py-2 border-t bg-muted/50 text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <ChevronUp className="h-3 w-3" />
              <ChevronDown className="h-3 w-3" />
              Navigieren
            </span>
            <span className="flex items-center gap-1">
              <CornerDownLeft className="h-3 w-3" />
              Auswählen
            </span>
          </div>
          <span>Esc zum Schließen</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}

/**
 * Hook zum Registrieren der Command Palette
 */
export function useCommandPalette() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen(o => !o)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { open, setOpen }
}
