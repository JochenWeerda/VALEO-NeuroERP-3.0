import { useState, useEffect } from 'react'
import { Command, CommandInput, CommandList, CommandItem, CommandEmpty, CommandGroup } from '@/components/ui/command'
import { Badge } from '@/components/ui/badge'

type Article = {
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
  onSelect: (article: Article) => void
  placeholder?: string
  autoFocus?: boolean
}

// Mock-Daten (später: API)
const mockArticles: Article[] = [
  { id: '1', artikelnr: 'A-001', bezeichnung: 'Blumenerde Premium 20L', ean: '4001234567890', preis: 12.99, image: '🌱', kategorie: 'Erde', lagerbestand: 45 },
  { id: '2', artikelnr: 'A-002', bezeichnung: 'Tomatensamen BIO', ean: '4001234567891', preis: 2.99, image: '🍅', kategorie: 'Saatgut', lagerbestand: 120 },
  { id: '3', artikelnr: 'A-003', bezeichnung: 'Universaldünger 5kg', ean: '4001234567892', preis: 24.99, image: '🌿', kategorie: 'Dünger', lagerbestand: 28 },
  { id: '4', artikelnr: 'A-004', bezeichnung: 'Gartenschere Professional', ean: '4001234567893', preis: 19.99, image: '✂️', kategorie: 'Werkzeug', lagerbestand: 15 },
  { id: '5', artikelnr: 'A-005', bezeichnung: 'Blumentopf Terrakotta 30cm', ean: '4001234567894', preis: 8.99, image: '🪴', kategorie: 'Zubehör', lagerbestand: 67 },
  { id: '6', artikelnr: 'A-006', bezeichnung: 'Gießkanne 10L', ean: '4001234567895', preis: 14.99, image: '💧', kategorie: 'Zubehör', lagerbestand: 33 },
  { id: '7', artikelnr: 'A-007', bezeichnung: 'Rasensamen Turbo 1kg', ean: '4001234567896', preis: 18.50, image: '🌾', kategorie: 'Saatgut', lagerbestand: 92 },
  { id: '8', artikelnr: 'A-008', bezeichnung: 'Pflanzerde Bio 40L', ean: '4001234567897', preis: 16.99, image: '🌱', kategorie: 'Erde', lagerbestand: 23 },
]

export function ArticleSearch({ onSelect, placeholder = 'Artikel suchen (Name, EAN, Artikelnr)...', autoFocus = true }: ArticleSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Article[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Debounced Search
  useEffect((): (() => void) | undefined => {
    if (query.length < 2) {
      setResults([])
      return
    }

    setIsSearching(true)
    const timer = setTimeout(() => {
      // Mock-Suche (später: API-Call)
      const searchLower = query.toLowerCase()
      const filtered = mockArticles.filter(
        (article) =>
          article.bezeichnung.toLowerCase().includes(searchLower) ||
          article.artikelnr.toLowerCase().includes(searchLower) ||
          article.ean?.includes(query) ||
          article.kategorie?.toLowerCase().includes(searchLower)
      )
      setResults(filtered)
      setIsSearching(false)
    }, 300) // 300ms Debounce

    return () => clearTimeout(timer)
  }, [query])

  const handleSelect = (article: Article): void => {
    onSelect(article)
    setQuery('')
    setResults([])
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
        {query.length < 2 ? (
          <CommandEmpty>
            <p className="text-sm text-muted-foreground py-6">
              Mindestens 2 Zeichen eingeben...
            </p>
          </CommandEmpty>
        ) : isSearching ? (
          <CommandEmpty>
            <p className="text-sm text-muted-foreground py-6">Suche läuft...</p>
          </CommandEmpty>
        ) : results.length === 0 ? (
          <CommandEmpty>
            <p className="text-sm text-muted-foreground py-6">
              Keine Artikel gefunden für "{query}"
            </p>
          </CommandEmpty>
        ) : (
          <CommandGroup heading={`${results.length} Treffer`}>
            {results.map((article) => (
              <CommandItem
                key={article.id}
                onSelect={() => handleSelect(article)}
                className="flex items-center gap-4 py-4 cursor-pointer"
              >
                {/* Artikel-Bild */}
                <span className="text-4xl">{article.image ?? '📦'}</span>

                {/* Artikel-Details */}
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-base truncate">
                    {article.bezeichnung}
                  </div>
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

                {/* Preis & Lagerbestand */}
                <div className="text-right">
                  <div className="text-lg font-bold text-primary">
                    {article.preis.toFixed(2)} €
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
