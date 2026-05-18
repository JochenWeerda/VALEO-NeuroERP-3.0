import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, Tag } from 'lucide-react'

type Promotion = {
  id: string
  name: string
  promo_type: 'PROZENT' | 'BETRAG' | 'GRATISARTIKEL'
  discount_value: number
  valid_from: string
  valid_to: string
  aktiv: boolean
}

const TYPE_VARIANT: Record<string, 'default' | 'secondary' | 'outline'> = {
  PROZENT: 'default',
  BETRAG: 'secondary',
  GRATISARTIKEL: 'outline',
}

export default function PosPromotionenPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: promotionen = [], isError, error, refetch } = useQuery<Promotion[]>({
    queryKey: ['pos-promotions'],
    queryFn: async () => (await apiClient.get('/api/v1/pos/promotions')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = promotionen.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'name' as const, label: 'Name', render: (p: Promotion) => <span className="font-medium">{p.name}</span> },
    { key: 'promo_type' as const, label: 'Typ', render: (p: Promotion) => <Badge variant={TYPE_VARIANT[p.promo_type] ?? 'outline'}>{p.promo_type}</Badge> },
    {
      key: 'discount_value' as const,
      label: 'Rabatt',
      render: (p: Promotion) =>
        p.promo_type === 'PROZENT'
          ? `${p.discount_value} %`
          : p.promo_type === 'BETRAG'
          ? `${p.discount_value.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`
          : '–',
    },
    { key: 'valid_from' as const, label: 'Gültig von', render: (p: Promotion) => new Date(p.valid_from).toLocaleDateString('de-DE') },
    { key: 'valid_to' as const, label: 'Gültig bis', render: (p: Promotion) => new Date(p.valid_to).toLocaleDateString('de-DE') },
    { key: 'aktiv' as const, label: 'Status', render: (p: Promotion) => <Badge variant={p.aktiv ? 'default' : 'secondary'}>{p.aktiv ? 'Aktiv' : 'Inaktiv'}</Badge> },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">POS Promotionen</h1>
            <p className="text-muted-foreground">Aktionen und Rabatte für das Kassensystem</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neue Aktion</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Tag className="h-4 w-4" />Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{promotionen.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{promotionen.filter((p) => p.aktiv).length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Inaktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-muted-foreground">{promotionen.filter((p) => !p.aktiv).length}</span></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Aktionsliste ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Aktionsname suchen..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
