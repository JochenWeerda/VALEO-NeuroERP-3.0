import { useState, useMemo } from 'react'
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
import { apiClient } from '@/lib/axios'

export type Article = {
  id: string
  articleNumber: string
  description: string
  description2?: string
  shortDescription?: string
  articleType?: string
  unit?: string
  matchcode2?: string
  customerArticleNumber?: string
}

type ArticleSearchDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (article: Article) => void
  customerId?: string
}

export function ArticleSearchDialog({
  open,
  onClose,
  onSelect,
  customerId,
}: ArticleSearchDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchIn, setSearchIn] = useState<'all' | 'number' | 'description'>('all')
  const [showBlocked, setShowBlocked] = useState(false)
  const [withPurpose, setWithPurpose] = useState(false)
  const [withPackaging, setWithPackaging] = useState(false)
  const [withSupplierNumber, setWithSupplierNumber] = useState(false)
  const [withEAN, setWithEAN] = useState(false)
  const [withCustomerArticleNumber, setWithCustomerArticleNumber] = useState(true)
  const [allArticleTypes, setAllArticleTypes] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'group' | 'selection' | 'variants'>('all')
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)

  const { data: articles = [], isLoading } = useQuery({
    queryKey: ['articles', 'search', searchTerm, customerId, activeTab],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      if (customerId) params.append('customer_id', customerId)
      if (showBlocked) params.append('include_blocked', 'true')
      if (withPurpose) params.append('with_purpose', 'true')
      if (withPackaging) params.append('with_packaging', 'true')
      if (withSupplierNumber) params.append('with_supplier_number', 'true')
      if (withEAN) params.append('with_ean', 'true')
      if (withCustomerArticleNumber) params.append('with_customer_article_number', 'true')
      if (allArticleTypes) params.append('all_types', 'true')
      
      const response = await apiClient.get<Article[]>('/api/v1/inventory/articles', { params })
      return response.data
    },
    enabled: open,
    staleTime: 30_000,
  })

  const filteredArticles = useMemo(() => {
    if (!searchTerm) return articles
    
    const term = searchTerm.toLowerCase()
    return articles.filter((article) => {
      if (searchIn === 'number') {
        return article.articleNumber.toLowerCase().includes(term)
      }
      if (searchIn === 'description') {
        return (
          article.description.toLowerCase().includes(term) ||
          article.description2?.toLowerCase().includes(term) ||
          article.shortDescription?.toLowerCase().includes(term)
        )
      }
      // all columns
      return (
        article.articleNumber.toLowerCase().includes(term) ||
        article.description.toLowerCase().includes(term) ||
        article.description2?.toLowerCase().includes(term) ||
        article.shortDescription?.toLowerCase().includes(term) ||
        article.matchcode2?.toLowerCase().includes(term) ||
        article.customerArticleNumber?.toLowerCase().includes(term)
      )
    })
  }, [articles, searchTerm, searchIn])

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
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Artikel suchen - nur Kunden-Artikel</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="article-matchcode">Matchcode:</Label>
              <Input
                id="article-matchcode"
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
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={searchIn}
                onChange={(e) => setSearchIn(e.target.value as typeof searchIn)}
              >
                <option value="all">alle Spalten</option>
                <option value="number">Artikel-Nr.</option>
                <option value="description">Bezeichnung</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input type="radio" id="pool" name="pool" defaultChecked />
                <Label htmlFor="pool" className="text-sm font-normal cursor-pointer">
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
            </div>
            <div className="space-y-2">
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
                  id="all-article-types"
                  checked={allArticleTypes}
                  onCheckedChange={(checked) => setAllArticleTypes(checked === true)}
                />
                <Label htmlFor="all-article-types" className="text-sm font-normal cursor-pointer">
                  alle Artikelarten
                </Label>
              </div>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
            <TabsList>
              <TabsTrigger value="all">alle Artikel</TabsTrigger>
              <TabsTrigger value="group">Artikel-Gruppe...</TabsTrigger>
              <TabsTrigger value="selection">Artikel-Selektion...</TabsTrigger>
              <TabsTrigger value="variants">Varianten...</TabsTrigger>
            </TabsList>
          </Tabs>

          <div className="flex-1 overflow-auto border rounded">
            {isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Artikel...</div>
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
                    <TableHead>Kunden-Artikel-Nr.</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredArticles.map((article) => (
                    <TableRow
                      key={article.id}
                      className={selectedArticle?.id === article.id ? 'bg-muted' : 'cursor-pointer'}
                      onClick={() => setSelectedArticle(article)}
                    >
                      <TableCell>{article.articleNumber}</TableCell>
                      <TableCell>{article.description}</TableCell>
                      <TableCell>{article.description2 || '-'}</TableCell>
                      <TableCell>{article.shortDescription || '-'}</TableCell>
                      <TableCell>{article.articleType || '-'}</TableCell>
                      <TableCell>{article.unit || '-'}</TableCell>
                      <TableCell>{article.matchcode2 || '-'}</TableCell>
                      <TableCell>{article.customerArticleNumber || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>

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


