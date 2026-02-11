import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, Loader2, Package, Plus, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

type Artikel = {
  id: string
  artikelnr: string
  bezeichnung: string
  warengruppe: string
  vkPreis: number
  bestand: number
  status: 'aktiv' | 'auslaufend'
}

const fallbackArtikel: Artikel[] = [
  { id: '1', artikelnr: '10001', bezeichnung: 'Weizen Premium', warengruppe: 'Getreide', vkPreis: 220.5, bestand: 450, status: 'aktiv' },
  { id: '2', artikelnr: '20005', bezeichnung: 'Sojaschrot 44%', warengruppe: 'Futtermittel', vkPreis: 520.0, bestand: 280, status: 'aktiv' },
  { id: '3', artikelnr: '30012', bezeichnung: 'NPK-Dünger 15-15-15', warengruppe: 'Düngemittel', vkPreis: 380.0, bestand: 220, status: 'aktiv' },
  { id: '4', artikelnr: '10008', bezeichnung: 'Gerste Brau', warengruppe: 'Getreide', vkPreis: 195.0, bestand: 380, status: 'aktiv' },
  { id: '5', artikelnr: '30025', bezeichnung: 'Kalkammonsalpeter', warengruppe: 'Düngemittel', vkPreis: 310.0, bestand: 150, status: 'auslaufend' },
]

function mapApiArticle(a: any): Artikel {
  return {
    id: a.id,
    artikelnr: a.article_number || a.sku || a.id?.substring(0, 5),
    bezeichnung: a.name || a.description || '–',
    warengruppe: a.category || a.product_group || 'Sonstige',
    vkPreis: Number(a.price || a.sell_price || 0),
    bestand: Number(a.stock_quantity || a.quantity || 0),
    status: a.is_active === false ? 'auslaufend' : 'aktiv',
  }
}

export default function ArtikelListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: artikel = fallbackArtikel, isLoading } = useQuery({
    queryKey: ['articles', searchTerm],
    queryFn: async () => {
      try {
        const res = await apiClient.get<{ items: any[]; total?: number }>('/api/v1/articles', {
          params: { search: searchTerm || undefined },
        })
        if (res.data?.items?.length) {
          return res.data.items.map(mapApiArticle)
        }
      } catch {
        // API not available – use fallback
      }
      // Filter fallback
      if (searchTerm) {
        const s = searchTerm.toLowerCase()
        return fallbackArtikel.filter(
          (a) =>
            a.bezeichnung.toLowerCase().includes(s) ||
            a.artikelnr.includes(s) ||
            a.warengruppe.toLowerCase().includes(s),
        )
      }
      return fallbackArtikel
    },
    staleTime: 2 * 60 * 1000,
  })

  const columns = [
    {
      key: 'artikelnr' as const,
      label: 'Artikelnr.',
      render: (a: Artikel) => <span className="font-mono">{a.artikelnr}</span>,
    },
    {
      key: 'bezeichnung' as const,
      label: 'Bezeichnung',
      render: (a: Artikel) => (
        <button
          onClick={() => navigate(`/artikel/${a.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {a.bezeichnung}
        </button>
      ),
    },
    {
      key: 'warengruppe' as const,
      label: 'Warengruppe',
      render: (a: Artikel) => <Badge variant="outline">{a.warengruppe}</Badge>,
    },
    {
      key: 'vkPreis' as const,
      label: 'VK-Preis',
      render: (a: Artikel) =>
        `${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(a.vkPreis)} / t`,
    },
    {
      key: 'bestand' as const,
      label: 'Bestand (t)',
      render: (a: Artikel) => `${a.bestand} t`,
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Artikel) => (
        <Badge variant={a.status === 'aktiv' ? 'outline' : 'secondary'}>
          {a.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
        </Badge>
      ),
    },
  ]

  const lagerwert = artikel.reduce((sum, a) => sum + a.vkPreis * a.bestand, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Artikel</h1>
          <p className="text-muted-foreground">Artikelstamm</p>
        </div>
        <Button onClick={() => navigate('/artikel/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Artikel
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              {isLoading ? (
                <Skeleton className="h-8 w-12" />
              ) : (
                <span className="text-2xl font-bold">{artikel.length}</span>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-12" />
            ) : (
              <span className="text-2xl font-bold text-green-600">
                {artikel.filter((a) => a.status === 'aktiv').length}
              </span>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lagerwert</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', {
                  style: 'currency',
                  currency: 'EUR',
                  maximumFractionDigits: 0,
                }).format(lagerwert)}
              </span>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Artikelnr., Bezeichnung, Warengruppe..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <DataTable data={artikel} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
