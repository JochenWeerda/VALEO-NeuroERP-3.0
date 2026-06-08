/**
 * Quick Search
 *
 * Globale Schnellsuche ueber alle Entitaeten.
 * Suche nach Kunden, Auftraegen, Artikeln und Rechnungen.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { clsx } from 'clsx'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useQuery } from '@tanstack/react-query'
import {
  Search,
  X,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { useDebounce } from '@/hooks/useDebounce'
import {
  emptySearchIcon,
  loadRecentSearches,
  recentSearchIcon,
  searchAll,
  storeRecentSearches,
  typeColors,
  typeIcons,
} from '@/components/innendienst/quick-search-data'

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
  const [recentSearches, setRecentSearches] = useState<SearchResult[]>(() => loadRecentSearches())
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const debouncedQuery = useDebounce(query, 200)

  const { data: results = [], isLoading } = useQuery({
    queryKey: ['quick-search', debouncedQuery],
    queryFn: () => searchAll(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 30 * 1000,
  })

  const handleSelect = useCallback((result: SearchResult) => {
    const nextRecentSearches = [result, ...recentSearches.filter((entry) => entry.id !== result.id)].slice(0, 5)
    setRecentSearches(nextRecentSearches)
    storeRecentSearches(nextRecentSearches)

    setQuery('')
    setIsOpen(false)

    if (onSelect) {
      onSelect(result)
      return
    }

    navigate(result.url)
  }, [navigate, onSelect, recentSearches])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isOpen) {
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((index) => Math.min(index + 1, results.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((index) => Math.max(index - 1, 0))
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
  }, [handleSelect, isOpen, results, selectedIndex])

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

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    setSelectedIndex(0)
  }, [results])

  const showDropdown = isOpen && (query.length >= 2 || recentSearches.length > 0)

  return (
    <div ref={containerRef} className={clsx('relative', className)}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
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
          className={clsx(
            'h-10 w-full rounded-lg border bg-background pl-9 pr-10 text-sm transition-colors',
            'placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20',
          )}
        />
        {query && (
          <button
            onClick={() => {
              setQuery('')
              inputRef.current?.focus()
            }}
            className="absolute right-3 top-1/2 rounded p-0.5 hover:bg-muted"
          >
            <X className="h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          </button>
        )}
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
      </div>

      {showDropdown && (
        <div className="absolute z-50 mt-1 max-h-[400px] w-full overflow-y-auto rounded-lg border bg-popover py-2 shadow-lg">
          {query.length < 2 && recentSearches.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-muted-foreground">
                {recentSearchIcon}
                Zuletzt gesucht
              </div>
              {recentSearches.map((result, index) => (
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

          {query.length >= 2 && (
            <>
              {results.length === 0 && !isLoading && (
                <div className="px-3 py-6 text-center text-muted-foreground">
                  {emptySearchIcon}
                  <p>Keine Ergebnisse fuer "{query}"</p>
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
      className={clsx(
        'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors',
        isSelected ? 'bg-primary/10' : 'hover:bg-muted',
      )}
    >
      <span className={clsx('shrink-0 rounded p-1.5', typeColors[result.type])}>
        {typeIcons[result.type]}
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{result.title}</p>
        {result.subtitle && <p className="truncate text-sm text-muted-foreground">{result.subtitle}</p>}
      </div>
      {result.meta && <span className="shrink-0 text-xs text-muted-foreground">{result.meta}</span>}
      {isSelected && <ArrowRight className="h-4 w-4 shrink-0 text-primary" />}
    </button>
  )
}
