/**
 * Quick Search
 *
 * Globale Schnellsuche über alle Entitäten
 * Suche nach Kunden, Aufträgen, Artikeln, Rechnungen
 * TanStack Query für Echtzeit-Ergebnisse
 */

import { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
import {
  Search,
  Users,
  ShoppingCart,
  Package,
  FileText,
  Clock,
  X,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { useDebounce } from '@/hooks/useDebounce'

export interface SearchResult {
  id: string
  type: 'customer' | 'order' | 'article' | 'invoice' | 'delivery'
  title: string
  subtitle?: string
  meta?: string
  url: string
}

interface QuickSearchProps {
  placeholder?: string
  onSelect?: (result: SearchResult) => void
  className?: string
  autoFocus?: boolean
}

// Mock-Suche (später durch echte API ersetzen)
async function searchAll(query: string): Promise<SearchResult[]> {
  if (!query || query.length < 2) return []

  // Simuliere API-Aufruf
  await new Promise(resolve => setTimeout(resolve, 300))

  const results: SearchResult[] = []

  // Mock-Ergebnisse basierend auf Query
  if (query.toLowerCase().includes('müller')) {
    results.push({
      id: 'c1',
      type: 'customer',
      title: 'Landwirtschaft Müller GmbH',
      subtitle: 'Hauptstraße 15, 12345 Neustadt',
      meta: 'Kunde seit 2019',
      url: '/crm/kunden-stamm/1',
    })
  }

  if (query.match(/\d{4,}/)) {
    results.push({
      id: 'o1',
      type: 'order',
      title: `Auftrag #${query}`,
      subtitle: 'Landwirtschaft Müller GmbH',
      meta: '15.01.2026',
      url: `/sales/auftraege-liste/${query}`,
    })
  }

  if (query.toLowerCase().includes('weizen') || query.toLowerCase().includes('dünger')) {
    results.push({
      id: 'a1',
      type: 'article',
      title: 'Weizen Saatgut Premium Elite',
      subtitle: 'ART-001 | 25,50 €/kg',
      meta: 'Bestand: 2.500 kg',
      url: '/artikel/1',
    })
    results.push({
      id: 'a2',
      type: 'article',
      title: 'NPK Dünger 15-15-15',
      subtitle: 'ART-002 | 180,00 €/t',
      meta: 'Bestand: 45 t',
      url: '/artikel/2',
    })
  }

  // Default-Ergebnisse wenn nichts spezifisches gefunden
  if (results.length === 0 && query.length >= 2) {
    results.push({
      id: 'c2',
      type: 'customer',
      title: `Suche nach "${query}" in Kunden...`,
      url: `/crm/kunden-stamm?search=${encodeURIComponent(query)}`,
    })
    results.push({
      id: 'a3',
      type: 'article',
      title: `Suche nach "${query}" in Artikeln...`,
      url: `/artikel?search=${encodeURIComponent(query)}`,
    })
  }

  return results
}

const typeIcons: Record<SearchResult['type'], React.ReactNode> = {
  customer: <Users className="h-4 w-4" />,
  order: <ShoppingCart className="h-4 w-4" />,
  article: <Package className="h-4 w-4" />,
  invoice: <FileText className="h-4 w-4" />,
  delivery: <Package className="h-4 w-4" />,
}

const typeColors: Record<SearchResult['type'], string> = {
  customer: 'text-blue-600 bg-blue-100',
  order: 'text-emerald-600 bg-emerald-100',
  article: 'text-purple-600 bg-purple-100',
  invoice: 'text-amber-600 bg-amber-100',
  delivery: 'text-cyan-600 bg-cyan-100',
}

export function QuickSearch({
  placeholder = 'Suchen... (Ctrl+/)',
  onSelect,
  className,
  autoFocus = false,
}: QuickSearchProps) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const debouncedQuery = useDebounce(query, 200)

  // TanStack Query für Suchergebnisse
  const { data: results = [], isLoading } = useQuery({
    queryKey: ['quick-search', debouncedQuery],
    queryFn: () => searchAll(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 30 * 1000,
  })

  // Letzte Suchen aus localStorage
  const recentSearches = useMemo(() => {
    try {
      const stored = localStorage.getItem('valeo-recent-searches')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }, [])

  // Ergebnis auswählen
  const handleSelect = useCallback((result: SearchResult) => {
    // In Recent speichern
    try {
      const recent = [result, ...recentSearches.filter((r: SearchResult) => r.id !== result.id)].slice(0, 5)
      localStorage.setItem('valeo-recent-searches', JSON.stringify(recent))
    } catch {
      // Ignore
    }

    setQuery('')
    setIsOpen(false)

    if (onSelect) {
      onSelect(result)
    } else {
      navigate(result.url)
    }
  }, [navigate, onSelect, recentSearches])

  // Keyboard Navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(i => Math.min(i + 1, results.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(i => Math.max(i - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (results[selectedIndex]) {
          handleSelect(results[selectedIndex])
        }
        break
      case 'Escape':
        e.preventDefault()
        setIsOpen(false)
        inputRef.current?.blur()
        break
    }
  }, [isOpen, results, selectedIndex, handleSelect])

  // Global Shortcut
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  // Klick außerhalb schließt Dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Reset selected index bei neuen Ergebnissen
  useEffect(() => {
    setSelectedIndex(0)
  }, [results])

  const showDropdown = isOpen && (query.length >= 2 || recentSearches.length > 0)

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {/* Suchfeld */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={cn(
            'w-full h-10 pl-9 pr-10 rounded-lg border bg-background',
            'text-sm placeholder:text-muted-foreground',
            'focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary',
            'transition-colors'
          )}
        />
        {query && (
          <button
            onClick={() => {
              setQuery('')
              inputRef.current?.focus()
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-muted"
          >
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        )}
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground animate-spin" />
        )}
      </div>

      {/* Dropdown */}
      {showDropdown && (
        <div className="absolute z-50 w-full mt-1 py-2 bg-popover border rounded-lg shadow-lg max-h-[400px] overflow-y-auto">
          {/* Letzte Suchen */}
          {query.length < 2 && recentSearches.length > 0 && (
            <div>
              <div className="px-3 py-1.5 text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Clock className="h-3 w-3" />
                Zuletzt gesucht
              </div>
              {recentSearches.map((result: SearchResult, index: number) => (
                <SearchResultItem
                  key={result.id}
                  result={result}
                  isSelected={index === selectedIndex}
                  onClick={() => handleSelect(result)}
                  onMouseEnter={() => setSelectedIndex(index)}
                />
              ))}
            </div>
          )}

          {/* Suchergebnisse */}
          {query.length >= 2 && (
            <>
              {results.length === 0 && !isLoading && (
                <div className="px-3 py-6 text-center text-muted-foreground">
                  <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>Keine Ergebnisse für "{query}"</p>
                </div>
              )}

              {results.map((result, index) => (
                <SearchResultItem
                  key={result.id}
                  result={result}
                  isSelected={index === selectedIndex}
                  onClick={() => handleSelect(result)}
                  onMouseEnter={() => setSelectedIndex(index)}
                />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}

function SearchResultItem({
  result,
  isSelected,
  onClick,
  onMouseEnter,
}: {
  result: SearchResult
  isSelected: boolean
  onClick: () => void
  onMouseEnter: () => void
}) {
  return (
    <button
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2 text-left transition-colors',
        isSelected ? 'bg-primary/10' : 'hover:bg-muted'
      )}
    >
      <span className={cn('shrink-0 p-1.5 rounded', typeColors[result.type])}>
        {typeIcons[result.type]}
      </span>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{result.title}</p>
        {result.subtitle && (
          <p className="text-sm text-muted-foreground truncate">{result.subtitle}</p>
        )}
      </div>
      {result.meta && (
        <span className="shrink-0 text-xs text-muted-foreground">{result.meta}</span>
      )}
      {isSelected && <ArrowRight className="h-4 w-4 shrink-0 text-primary" />}
    </button>
  )
}

