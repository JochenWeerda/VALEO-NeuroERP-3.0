/**
 * Semantic Search Dialog
 * RAG-powered search across customers, articles, and documents
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Search, Loader2, User, Package, FileText, ArrowRight } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

type SearchResult = {
  id: string
  type: 'customer' | 'article' | 'document'
  title: string
  subtitle?: string
  score: number
  link: string
  metadata?: Record<string, string>
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function SemanticSearch() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Listen for custom event
  useEffect(() => {
    const handleOpen = () => setOpen(true)
    window.addEventListener('open-semantic-search', handleOpen)
    return () => window.removeEventListener('open-semantic-search', handleOpen)
  }, [])

  // Keyboard shortcut: Ctrl+Shift+F
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'f' && e.ctrlKey && e.shiftKey) {
        e.preventDefault()
        setOpen(true)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  // Debounced search
  useEffect(() => {
    if (query.length < 3) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      
      try {
        // Call RAG API
        const response = await apiClient.get('/api/v1/rag/search', {
          params: { query, limit: 10 }
        })

        const data = response.data

        // Transform to SearchResults
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const searchResults: SearchResult[] = (data as any).results?.map((r: any) => ({
          id: r.id || r.metadata?.id || 'unknown',
          type: r.metadata?.type || 'document',
          title: r.metadata?.name || r.document || 'Unbekannt',
          subtitle: r.metadata?.description || r.metadata?.email,
          score: r.score || 0,
          link: getLink(r.metadata?.type, r.metadata?.id || r.id),
          metadata: r.metadata
        })) || []

        setResults(searchResults)
      } catch (error) {
        console.error('Semantic search error:', error)
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 400)

    return () => clearTimeout(timer)
  }, [query])

  const getLink = (type: string, id: string): string => {
    switch (type) {
      case 'customer':
        return `/verkauf/kunde/${id}`
      case 'article':
        return `/artikel/${id}`
      case 'document':
        return `/dokumente/${id}`
      default:
        return '#'
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'customer':
        return <User className="h-5 w-5 text-blue-600" />
      case 'article':
        return <Package className="h-5 w-5 text-green-600" />
      case 'document':
        return <FileText className="h-5 w-5 text-orange-600" />
      default:
        return <Search className="h-5 w-5" />
    }
  }

  const getTypeBadge = (type: string) => {
    const labels: Record<string, string> = {
      customer: 'Kunde',
      article: 'Artikel',
      document: 'Dokument'
    }
    return labels[type] || type
  }

  const handleSelect = (result: SearchResult) => {
    navigate(result.link)
    setOpen(false)
    setQuery('')
    setResults([])
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Semantische Suche
          </DialogTitle>
          <DialogDescription>
            Finde Kunden, Artikel und Dokumente mit KI-gestützter Suche
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              placeholder="Suche nach Kunden, Artikeln, Dokumenten..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-10 h-12 text-lg"
              autoFocus
            />
          </div>

          {/* Results */}
          <div className="min-h-[300px] max-h-[400px] overflow-y-auto">
            {query.length < 3 ? (
              <div className="text-center py-12">
                <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-sm text-muted-foreground">
                  Mindestens 3 Zeichen eingeben...
                </p>
              </div>
            ) : loading ? (
              <div className="text-center py-12">
                <Loader2 className="h-12 w-12 mx-auto mb-4 text-primary animate-spin" />
                <p className="text-sm text-muted-foreground">
                  Durchsuche Datenbank...
                </p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-sm text-muted-foreground">
                  Keine Ergebnisse für "{query}"
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {results.map((result) => (
                  <Card
                    key={result.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => handleSelect(result)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {getIcon(result.type)}
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{result.title}</div>
                            {result.subtitle && (
                              <div className="text-sm text-muted-foreground truncate">
                                {result.subtitle}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <Badge variant="secondary">
                            {getTypeBadge(result.type)}
                          </Badge>
                          <Badge variant="outline">
                            {Math.round(result.score * 100)}%
                          </Badge>
                          <ArrowRight className="h-4 w-4 text-muted-foreground" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Shortcuts Hint */}
          <div className="text-xs text-muted-foreground text-center border-t pt-3">
            💡 Tipp: <kbd className="bg-muted px-1.5 py-0.5 rounded">Ctrl+Shift+F</kbd> zum schnellen Öffnen
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

