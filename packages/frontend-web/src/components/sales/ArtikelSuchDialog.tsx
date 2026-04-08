/**
 * Artikel-Suchmaske
 * 1:1 Nachbau der zvoove Artikel-Suchmaske
 */

import { useState, useMemo, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient } from '@/lib/api-client'

export type Article = {
  id: string
  articleNumber: string
  description: string
  description2?: string
  shortDescription?: string
  articleType?: string
  unit?: string
  matchcode2?: string
  articleGroup?: string
  customerArticleNumber?: string
  // Backend fields (for mapping)
  name?: string
  article_number?: string
  suchbegriff?: string
  barcode?: string
  ean?: string
  supplier_number?: string
  is_active?: boolean
}

type ArtikelSuchDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (article: Article) => void
  customerId?: string
}

const SEARCH_DEBOUNCE_MS = 300

export function ArtikelSuchDialog({
  open,
  onClose,
  onSelect,
}: ArtikelSuchDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('')
  const [searchIn, setSearchIn] = useState<'all' | 'number' | 'description'>('all')
  const [pool, setPool] = useState<'O' | 'A'>('O')
  const [showBlocked, setShowBlocked] = useState(false)
  const [withPurpose, setWithPurpose] = useState(false)
  const [withPackaging, setWithPackaging] = useState(false)
  const [withSupplierNumber, setWithSupplierNumber] = useState(false)
  const [withEAN, setWithEAN] = useState(false)
  const [withAltEAN, setWithAltEAN] = useState(false)
  const [withCustomerArticleNumber, setWithCustomerArticleNumber] = useState(true)
  const [allArticleTypes, setAllArticleTypes] = useState(true)
  const [onlySustainableBiomass, setOnlySustainableBiomass] = useState(false)
  const [activeTab, setActiveTab] = useState<'all' | 'group' | 'selection' | 'variants'>('all')
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
    }, SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [searchTerm])

  // Server-side search: only fetch when debounced search term has 2+ chars
  const { data: articles = [], isLoading, error } = useQuery({
    queryKey: ['articles', 'search', debouncedSearchTerm],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('search', debouncedSearchTerm)
      params.append('limit', '50')

      const response = await apiClient.get<any>('/api/v1/articles', { params })

      let items: any[] = []
      if (Array.isArray(response)) {
        items = response
      } else if (response?.items && Array.isArray(response.items)) {
        items = response.items
      } else if (response?.data?.items && Array.isArray(response.data.items)) {
        items = response.data.items
      } else if (response?.data && Array.isArray(response.data)) {
        items = response.data
      }

      if (items.length === 0 && response) {
        for (const key of Object.keys(response)) {
          if (Array.isArray((response as any)[key])) {
            items = (response as any)[key]
            break
          }
        }
      }

      // Map backend article format to frontend format
      return items.map((a: any) => ({
        id: a.id,
        articleNumber: a.article_number || a.articleNumber || '',
        description: (a.name || a.description || '').trim(),
        description2: a.description2 || a.description_2 || '',
        shortDescription: a.short_description || a.shortDescription || a.suchbegriff || '',
        articleType: a.article_type || a.articleType || a.category || '',
        unit: a.unit || a.me || '',
        matchcode2: a.matchcode2 || a.matchcode_2 || a.suchbegriff || '',
        articleGroup: a.article_group || a.articleGroup || a.warengruppe || a.category || '',
        customerArticleNumber: a.customer_article_number || a.customerArticleNumber || '',
        name: a.name,
        article_number: a.article_number,
        suchbegriff: a.suchbegriff,
        barcode: a.barcode,
        ean: a.barcode,
        supplier_number: a.supplier_number,
        is_active: a.is_active ?? true,
      }))
    },
    enabled: open && debouncedSearchTerm.length >= 2,
    staleTime: 30_000,
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 401) {
        return false
      }
      return failureCount < 3
    },
    throwOnError: false,
  })

  const filteredArticles = useMemo(() => {
    let result = articles
    
    if (activeTab === 'group') {
      result = result.filter((a: any) => a.articleGroup || a.article_group)
    } else if (activeTab === 'selection') {
      result = result.filter((a: any) => a.selection || a.is_selected)
    } else if (activeTab === 'variants') {
      result = result.filter((a: any) => a.isVariant || a.is_variant || a.parent_article_id)
    }

    if (pool === 'A') {
      result = result.filter((a: any) => a.isAlternative || a.is_alternative)
    }
    
    // Apply blocked articles filter
    if (!showBlocked) {
      result = result.filter((a) => a.is_active !== false)
    }
    
    // Apply search filter
    if (!debouncedSearchTerm) {
      // If no search term, show first 10 articles (alphabetically sorted)
      return result
        .sort((a, b) => a.description.localeCompare(b.description, 'de', { sensitivity: 'base' }))
        .slice(0, 10)
    }
    
    const term = debouncedSearchTerm.toLowerCase()
    const hasWildcard = debouncedSearchTerm.includes('*')
    
    // Helper function for wildcard matching
    const matchesPattern = (text: string | undefined, pattern: string): boolean => {
      if (!text) return false
      const regexPattern = pattern.replace(/\*/g, '.*').replace(/\?/g, '.')
      try {
        const regex = new RegExp(regexPattern, 'i')
        return regex.test(text)
      } catch {
        return text.toLowerCase().includes(pattern.toLowerCase().replace(/\*/g, '').replace(/\?/g, ''))
      }
    }
    
    if (hasWildcard) {
      // Wildcard search
      if (searchIn === 'number') {
        result = result.filter((a) => matchesPattern(a.articleNumber, debouncedSearchTerm))
      } else if (searchIn === 'description') {
        result = result.filter(
          (a) =>
            matchesPattern(a.description, debouncedSearchTerm) ||
            matchesPattern(a.description2, debouncedSearchTerm) ||
            matchesPattern(a.shortDescription, debouncedSearchTerm)
        )
      } else {
        // all columns
        result = result.filter(
          (a) =>
            matchesPattern(a.articleNumber, debouncedSearchTerm) ||
            matchesPattern(a.description, debouncedSearchTerm) ||
            matchesPattern(a.description2, debouncedSearchTerm) ||
            matchesPattern(a.shortDescription, debouncedSearchTerm) ||
            matchesPattern(a.matchcode2, debouncedSearchTerm) ||
            matchesPattern(a.customerArticleNumber, debouncedSearchTerm) ||
            matchesPattern(a.name, debouncedSearchTerm) ||
            matchesPattern(a.suchbegriff, debouncedSearchTerm) ||
            matchesPattern(a.barcode, debouncedSearchTerm) ||
            matchesPattern(a.supplier_number, debouncedSearchTerm)
        )
      }
    } else {
      // Normal search
      if (searchIn === 'number') {
        result = result.filter((a) => a.articleNumber.toLowerCase().includes(term))
      } else if (searchIn === 'description') {
        result = result.filter(
          (a) =>
            a.description.toLowerCase().includes(term) ||
            a.description2?.toLowerCase().includes(term) ||
            a.shortDescription?.toLowerCase().includes(term)
        )
      } else {
        // all columns
        result = result.filter(
          (a) =>
            a.articleNumber.toLowerCase().includes(term) ||
            a.description.toLowerCase().includes(term) ||
            a.description2?.toLowerCase().includes(term) ||
            a.shortDescription?.toLowerCase().includes(term) ||
            a.matchcode2?.toLowerCase().includes(term) ||
            a.customerArticleNumber?.toLowerCase().includes(term) ||
            a.name?.toLowerCase().includes(term) ||
            a.suchbegriff?.toLowerCase().includes(term) ||
            a.barcode?.toLowerCase().includes(term) ||
            a.supplier_number?.toLowerCase().includes(term)
        )
      }
    }
    
    // Apply additional filters (withPurpose, withPackaging, etc.)
    // These are currently client-side filters based on available data
    // TODO: Implement proper filtering when backend supports these fields
    
    // Sort alphabetically by description
    const sorted = result.sort((a, b) =>
      a.description.localeCompare(b.description, 'de', { sensitivity: 'base' })
    )
    
    console.log('[ArtikelSuchDialog] Filtered articles:', {
      total: articles.length,
      filtered: sorted.length,
      searchTerm: debouncedSearchTerm,
      searchIn,
      activeTab,
    })
    
    return sorted
  }, [articles, debouncedSearchTerm, searchIn, activeTab, pool, showBlocked])

  const handleSelect = (): void => {
    if (selectedArticle) {
      onSelect(selectedArticle)
      setSelectedArticle(null)
      setSearchTerm('')
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Artikel suchen - nur Kunden-Artikel -</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          {/* Suchbereich */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="matchcode">Matchcode:</Label>
              <Input
                id="matchcode"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Artikel suchen..."
                autoFocus
                className="bg-green-50"
              />
            </div>
            <div>
              <Label htmlFor="search-in">Suche nach:</Label>
              <select
                id="search-in"
                className="w-full rounded-md border border-input bg-background px-3 py-2 h-10"
                value={searchIn}
                onChange={(e) => setSearchIn(e.target.value as typeof searchIn)}
              >
                <option value="all">alle Spalten</option>
                <option value="number">Artikel-Nr.</option>
                <option value="description">Bezeichnung</option>
              </select>
            </div>
          </div>

          {/* Filter-Checkboxen */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input
                  type="radio"
                  id="pool-o"
                  name="pool"
                  checked={pool === 'O'}
                  onChange={() => setPool('O')}
                />
                <Label htmlFor="pool-o" className="text-sm font-normal cursor-pointer">
                  O Pool
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="show-blocked"
                  checked={showBlocked}
                  onCheckedChange={(checked) => setShowBlocked(checked === true)}
                />
                <Label htmlFor="show-blocked" className="text-sm font-normal cursor-pointer">
                  auch gesperrte Artikel anzeigen
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-purpose"
                  checked={withPurpose}
                  onCheckedChange={(checked) => setWithPurpose(checked === true)}
                />
                <Label htmlFor="with-purpose" className="text-sm font-normal cursor-pointer">
                  mit Verwendungszweck
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-packaging"
                  checked={withPackaging}
                  onCheckedChange={(checked) => setWithPackaging(checked === true)}
                />
                <Label htmlFor="with-packaging" className="text-sm font-normal cursor-pointer">
                  mit Gebinde
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-supplier-number"
                  checked={withSupplierNumber}
                  onCheckedChange={(checked) => setWithSupplierNumber(checked === true)}
                />
                <Label htmlFor="with-supplier-number" className="text-sm font-normal cursor-pointer">
                  mit Lieferanten-Artikel-Nr
                </Label>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-ean"
                  checked={withEAN}
                  onCheckedChange={(checked) => setWithEAN(checked === true)}
                />
                <Label htmlFor="with-ean" className="text-sm font-normal cursor-pointer">
                  mit EAN-Code
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-alt-ean"
                  checked={withAltEAN}
                  onCheckedChange={(checked) => setWithAltEAN(checked === true)}
                />
                <Label htmlFor="with-alt-ean" className="text-sm font-normal cursor-pointer">
                  Alt.-EAN-Code
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="all-article-types"
                  checked={allArticleTypes}
                  onCheckedChange={(checked) => setAllArticleTypes(checked === true)}
                />
                <Label htmlFor="all-article-types" className="text-sm font-normal cursor-pointer">
                  alle Artikelarten
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="with-customer-article-number"
                  checked={withCustomerArticleNumber}
                  onCheckedChange={(checked) => setWithCustomerArticleNumber(checked === true)}
                />
                <Label htmlFor="with-customer-article-number" className="text-sm font-normal cursor-pointer">
                  mit Kunden-Artikel-Nr.
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="only-sustainable-biomass"
                  checked={onlySustainableBiomass}
                  onCheckedChange={(checked) => setOnlySustainableBiomass(checked === true)}
                />
                <Label htmlFor="only-sustainable-biomass" className="text-sm font-normal cursor-pointer">
                  nur "Nachhaltige Biomasse"
                </Label>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
            <TabsList>
              <TabsTrigger value="all">alle Artikel</TabsTrigger>
              <TabsTrigger value="group">Artikel-Gruppe...</TabsTrigger>
              <TabsTrigger value="selection">Artikel-Selektion...</TabsTrigger>
              <TabsTrigger value="variants">Varianten...</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Ergebnistabelle */}
          <div className="flex-1 overflow-auto border rounded">
            {isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Artikel...</div>
            ) : error ? (
              <div className="p-4 text-center text-red-500">
                Fehler beim Laden der Artikel: {error instanceof Error ? error.message : 'Unbekannter Fehler'}
              </div>
            ) : filteredArticles.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                {articles.length === 0
                  ? 'Keine Artikel in der Datenbank gefunden.'
                  : debouncedSearchTerm
                    ? `Keine Artikel gefunden für "${debouncedSearchTerm}"`
                    : 'Bitte geben Sie einen Suchbegriff ein...'}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Artikel-Nr.</TableHead>
                    <TableHead>Bezeichnung</TableHead>
                    <TableHead>Bezeichnung 2</TableHead>
                    <TableHead>Kurzbezeichnung</TableHead>
                    <TableHead>Artikel-Art</TableHead>
                    <TableHead>ME1</TableHead>
                    <TableHead>2. Matchcode</TableHead>
                    <TableHead>Artikel-G...</TableHead>
                    <TableHead>Kunden-Artikel-Nr.</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredArticles.map((article) => (
                    <TableRow
                      key={article.id}
                      className={selectedArticle?.id === article.id ? 'bg-muted cursor-pointer' : 'cursor-pointer'}
                      onClick={() => setSelectedArticle(article)}
                    >
                      <TableCell>{article.articleNumber}</TableCell>
                      <TableCell>{article.description}</TableCell>
                      <TableCell>{article.description2 || '-'}</TableCell>
                      <TableCell>{article.shortDescription || '-'}</TableCell>
                      <TableCell>{article.articleType || '-'}</TableCell>
                      <TableCell>{article.unit || '-'}</TableCell>
                      <TableCell>{article.matchcode2 || '-'}</TableCell>
                      <TableCell>{article.articleGroup || '-'}</TableCell>
                      <TableCell>{article.customerArticleNumber || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>

          {/* Footer-Tabs */}
          <Tabs defaultValue="prices">
            <TabsList>
              <TabsTrigger value="alternatives">Alternativ-Artikel</TabsTrigger>
              <TabsTrigger value="prices">Preise</TabsTrigger>
              <TabsTrigger value="stock">Lager-Bestand</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Abbrechen
          </Button>
          <Button onClick={handleSelect} disabled={!selectedArticle}>
            OK
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

