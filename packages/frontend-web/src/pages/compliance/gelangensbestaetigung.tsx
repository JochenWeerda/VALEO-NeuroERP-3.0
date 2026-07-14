import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search } from 'lucide-react'

type Gelangensbestaetigung = {
  id: string
  gelangensbestaetigung_nr: string
  empfaenger_name: string
  empfaenger_land: string
  versanddatum: string
  status: 'AUSSTEHEND' | 'ERHALTEN' | 'ABGELAUFEN'
  token: string
}

const STATUS_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  AUSSTEHEND: 'secondary',
  ERHALTEN: 'default',
  ABGELAUFEN: 'destructive',
}

function addDays(dateStr: string, days: number): string {
  const d = new Date(dateStr)
  d.setDate(d.getDate() + days)
  return d.toLocaleDateString('de-DE')
}

export default function GelangensBestaetigungPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: items = [], isError, error, refetch } = useQuery<Gelangensbestaetigung[]>({
    queryKey: ['gelangensbestaetigung'],
    queryFn: async () => (await apiClient.get<Gelangensbestaetigung[]>('/api/v1/gelangensbestaetigung')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = items.filter(
    (i) =>
      i.gelangensbestaetigung_nr.toLowerCase().includes(search.toLowerCase()) ||
      i.empfaenger_name.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'gelangensbestaetigung_nr' as const, label: 'Nr.', render: (i: Gelangensbestaetigung) => <span className="font-mono">{i.gelangensbestaetigung_nr}</span> },
    { key: 'empfaenger_name' as const, label: 'Empfänger' },
    { key: 'empfaenger_land' as const, label: 'Land' },
    { key: 'versanddatum' as const, label: 'Versanddatum', render: (i: Gelangensbestaetigung) => new Date(i.versanddatum).toLocaleDateString('de-DE') },
    { key: 'id' as const, label: 'Frist (90 Tage)', render: (i: Gelangensbestaetigung) => addDays(i.versanddatum, 90) },
    {
      key: 'status' as const,
      label: 'Status',
      render: (i: Gelangensbestaetigung) => (
        <Badge variant={STATUS_VARIANT[i.status] ?? 'outline'}>{i.status}</Badge>
      ),
    },
  ]

  const ausstehend = items.filter((i) => i.status === 'AUSSTEHEND').length

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Gelangensbestätigung §17a UStG</h1>
            <p className="text-muted-foreground">Nachweis der steuerfreien innergemeinschaftlichen Lieferung</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neu</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{items.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Ausstehend</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{ausstehend}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Erhalten</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{items.filter((i) => i.status === 'ERHALTEN').length}</span></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Bestätigungen</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Nr. oder Empfänger..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
