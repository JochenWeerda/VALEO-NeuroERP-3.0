import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, Loader2, Package, Plus, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'

type Artikel = {
  id: string
  artikelnr: string
  bezeichnung: string
  warengruppe: string
  vkPreis: number
  bestand: number
  status: 'aktiv' | 'auslaufend'
}

function mapApiArticle(a: Record<string, unknown>): Artikel {
  return {
    id: String(a.id ?? ''),
    artikelnr: String(a.article_number ?? a.sku ?? String(a.id ?? '').substring(0, 5)),
    bezeichnung: String(a.name ?? a.description ?? '-'),
    warengruppe: String(a.category ?? a.product_group ?? 'Sonstige'),
    vkPreis: Number(a.sales_price ?? a.price ?? a.sell_price ?? 0),
    bestand: Number(a.current_stock ?? a.stock_quantity ?? a.quantity ?? 0),
    status: a.is_active === false ? 'auslaufend' : 'aktiv',
  }
}

export default function ArtikelListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: artikel = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['articles', searchTerm],
    queryFn: async () => {
      const res = await apiClient.get<{ items?: Record<string, unknown>[]; total?: number }>('/api/v1/articles', {
        params: { search: searchTerm || undefined },
      })
      if (!Array.isArray(res.data?.items)) {
        throw new Error('Ungueltige API-Antwort fuer Artikelliste')
      }
      return res.data.items.map(mapApiArticle)
    },
    staleTime: 2 * 60 * 1000,
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

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
          type="button"
          onClick={() => navigate(`/artikel/${a.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
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

  const persistExport = () => {
    const header = 'Artikelnr;Bezeichnung;Warengruppe;VK-Preis;Bestand;Status\n'
    const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = artikel
      .map((a) => [a.artikelnr, a.bezeichnung, a.warengruppe, a.vkPreis, a.bestand, a.status].map(esc).join(';'))
      .join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `artikel-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Artikel</h1>
          <p className="text-muted-foreground">Artikel suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/artikel/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neuer Artikel
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-muted-foreground" />
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
              <span className="text-2xl font-bold text-status-success">
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
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Artikel"
                placeholder="Artikelnr., Bezeichnung, Warengruppe"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={persistExport}>
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
