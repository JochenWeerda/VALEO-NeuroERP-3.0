import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Command, CommandInput, CommandList, CommandItem, CommandEmpty, CommandGroup } from '@/components/ui/command'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'

export type Article = {
  id: string
  artikelnr: string
  bezeichnung: string
  ean?: string
  preis: number
  image?: string
  kategorie?: string
  lagerbestand?: number
}

interface ArticleSearchProps {
  onSelect: (_article: Article) => void
  placeholder?: string
  autoFocus?: boolean
}

type ArticleApi = {
  id: string
  article_number: string
  name: string
  barcode?: string | null
  category?: string | null
  sales_price: string | number
  available_stock?: string | number
}

type PaginatedArticleResponse = {
  items: ArticleApi[]
}

const MIN_QUERY_LENGTH = 2
const SEARCH_DEBOUNCE_MS = 300
const DEFAULT_PLACEHOLDER_ICON = '[ ]'

function mapArticle(api: ArticleApi): Article {
  const price = typeof api.sales_price === 'string' ? Number(api.sales_price) : api.sales_price ?? 0
  const stock = typeof api.available_stock === 'string' ? Number(api.available_stock) : api.available_stock

  return {
    id: api.id,
    artikelnr: api.article_number,
    bezeichnung: api.name,
    ean: api.barcode ?? undefined,
    preis: Number.isFinite(price) ? price : 0,
    kategorie: api.category ?? undefined,
    lagerbestand: stock !== undefined && Number.isFinite(stock) ? Number(stock) : undefined,
    image: DEFAULT_PLACEHOLDER_ICON,
  }
}

export function ArticleSearch({ onSelect, placeholder = 'Artikel suchen (Name, EAN, Artikelnr)...', autoFocus = true }: ArticleSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Article[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  const trimmedQuery = useMemo(() => query.trim(), [query])

  useEffect(() => {
    if (trimmedQuery.length < MIN_QUERY_LENGTH) {
      setResults([])
      setLoadError(null)
      return
    }

    const controller = new AbortController()
    setIsSearching(true)
    setLoadError(null)

    const timeout = setTimeout(() => {
      apiClient
        .get<PaginatedArticleResponse>('/api/v1/articles', {
          params: { search: trimmedQuery, limit: 15 },
          signal: controller.signal,
        })
        .then((response) => {
          const mapped = response.data.items.map(mapArticle)
          setResults(mapped)
        })
        .catch((error) => {
          if (axios.isCancel(error)) return
          setLoadError('Fehler beim Laden der Artikel')
          setResults([])
        })
        .finally(() => {
          setIsSearching(false)
        })
    }, SEARCH_DEBOUNCE_MS)

    return () => {
      clearTimeout(timeout)
      controller.abort()
    }
  }, [trimmedQuery])

  const handleSelect = (article: Article): void => {
    onSelect(article)
    setQuery('')
    setResults([])
  }

  const renderEmptyState = () => {
    if (trimmedQuery.length < MIN_QUERY_LENGTH) {
      return <p className="text-sm text-muted-foreground py-6">Mindestens {MIN_QUERY_LENGTH} Zeichen eingeben...</p>
    }

    if (isSearching) {
      return <p className="text-sm text-muted-foreground py-6">Suche laeuft...</p>
    }

    if (loadError) {
      return <p className="text-sm text-red-600 py-6">{loadError}</p>
    }

    return <p className="text-sm text-muted-foreground py-6">Keine Artikel gefunden fuer "{trimmedQuery}"</p>
  }

  return (
    <Command className="border rounded-lg shadow-lg">
      <CommandInput
        placeholder={placeholder}
        value={query}
        onValueChange={setQuery}
        autoFocus={autoFocus}
        className="text-lg h-14"
      />
      <CommandList className="max-h-[400px]">
        {results.length === 0 ? (
          <CommandEmpty>{renderEmptyState()}</CommandEmpty>
        ) : (
          <CommandGroup heading={`${results.length} Treffer`}>
            {results.map((article) => (
              <CommandItem
                key={article.id}
                onSelect={() => handleSelect(article)}
                className="flex items-center gap-4 py-4 cursor-pointer"
              >
                <span className="text-4xl">{article.image ?? DEFAULT_PLACEHOLDER_ICON}</span>

                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-base truncate">{article.bezeichnung}</div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                    <span>Art.-Nr: {article.artikelnr}</span>
                    {article.ean && <span>EAN: {article.ean}</span>}
                    {article.kategorie && (
                      <Badge variant="secondary" className="text-xs">
                        {article.kategorie}
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-bold text-primary">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 }).format(article.preis)}
                  </div>
                  {article.lagerbestand !== undefined && (
                    <div
                      className={`text-xs ${
                        article.lagerbestand > 20
                          ? 'text-green-600'
                          : article.lagerbestand > 5
                            ? 'text-orange-600'
                            : 'text-red-600'
                      }`}
                    >
                      Lager: {article.lagerbestand} Stk
                    </div>
                  )}
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </Command>
  )
}


