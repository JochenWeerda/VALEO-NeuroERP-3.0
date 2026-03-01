import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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

export default function LieferantenListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')

  const handleExport = async () => {
    try {
      const res = await api.post('/api/v1/export/list', { entity: 'creditors', format: 'csv' }, { responseType: 'blob' })
      const blob = res.data as Blob
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `export_lieferanten_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'Export erstellt', description: 'Download gestartet.' })
    } catch (e: any) {
      toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
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
          onClick={() => navigate(`/einkauf/lieferant/${l.id}`)}
          className="font-medium text-blue-600 hover:underline"
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
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Lieferanten</h1>
          <p className="text-muted-foreground">Lieferantenverwaltung</p>
        </div>
        <Button onClick={() => navigate('/einkauf/lieferant/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Lieferant
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferanten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-600" />
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
              <span className="text-2xl font-bold text-green-600">{aktiveLieferanten.length}</span>
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

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Name, Typ, Ort..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
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
            <DataTable data={lieferanten} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
