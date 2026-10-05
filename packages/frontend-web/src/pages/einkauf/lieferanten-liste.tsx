import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Building2, FileDown, Loader2, Plus, Search } from 'lucide-react'
import { useSuppliers, type Supplier } from '@/lib/api/crm'
import { api } from '@/lib/axios'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function LieferantenListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const [exporting, setExporting] = useState(false)

  const persistExport = async (): Promise<void> => {
    const res = await api.post('/api/v1/export/list', { entity: 'creditors', format: 'csv' }, { responseType: 'blob' })
    const blob = res.data as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export_lieferanten_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleExport = async (): Promise<void> => {
    if (exporting) return
    setExporting(true)
    try {
      await persistExport()
      toast({ title: 'Export erstellt', description: 'Download gestartet.' })
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    } finally {
      setExporting(false)
    }
  }

  const { data, isLoading } = useSuppliers({
    search: searchTerm || undefined,
  })

  const lieferanten = data?.items ?? []

  const columns = [
    {
      key: 'name' as const,
      label: 'Lieferant',
      render: (l: Supplier) => (
        <button
          type="button"
          onClick={() => navigate(`/einkauf/lieferant/${l.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {l.name}
        </button>
      ),
    },
    {
      key: 'supplier_number' as const,
      label: 'Lieferantennr.',
      render: (l: Supplier) => (
        <span className="font-mono text-sm">{l.supplier_number || '–'}</span>
      ),
    },
    {
      key: 'type' as const,
      label: 'Typ',
      render: (l: Supplier) => l.type ? <Badge variant="outline">{l.type}</Badge> : '–',
    },
    { key: 'city' as const, label: 'Ort', render: (l: Supplier) => l.city || '–' },
    {
      key: 'rating' as const,
      label: 'Bewertung',
      render: (l: Supplier) =>
        l.rating ? (
          <div className="flex items-center gap-1">
            <span className="font-bold">{l.rating.toFixed(1)}</span>
            <span className="text-sm text-muted-foreground">/ 5</span>
          </div>
        ) : (
          '–'
        ),
    },
    {
      key: 'is_active' as const,
      label: 'Status',
      render: (l: Supplier) => (
        <Badge variant={l.is_active ? 'outline' : 'destructive'}>
          {l.is_active ? 'Aktiv' : 'Gesperrt'}
        </Badge>
      ),
    },
  ]

  const aktiveLieferanten = lieferanten.filter((l) => l.is_active)
  const avgRating =
    lieferanten.length > 0
      ? lieferanten.reduce((sum, l) => sum + (l.rating || 0), 0) / lieferanten.length
      : 0

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Lieferanten</h1>
          <p className="text-muted-foreground">Lieferanten suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/einkauf/lieferant/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neuer Lieferant
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferanten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-muted-foreground" />
              {isLoading ? (
                <Skeleton className="h-8 w-12" />
              ) : (
                <span className="text-2xl font-bold">{data?.total ?? lieferanten.length}</span>
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
              <span className="text-2xl font-bold text-status-success">{aktiveLieferanten.length}</span>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Bewertung</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <span className="text-2xl font-bold">{avgRating.toFixed(1)} / 5</span>
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
                aria-label="Suche Lieferanten"
                placeholder="Name, Typ oder Ort suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={() => { void handleExport() }} disabled={exporting}>
              {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
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
            <DataTable data={lieferanten} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
