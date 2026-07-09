import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, Download } from 'lucide-react'

type IntrastatMeldung = {
  id: string
  meldenummer: string
  meldungsart: 'EINGANG' | 'VERSAND'
  meldezeitraum: string
  status: 'ENTWURF' | 'GEMELDET' | 'KORREKTUR'
  statistischer_wert_eur: number
}

const STATUS_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  ENTWURF: 'secondary',
  GEMELDET: 'default',
  KORREKTUR: 'destructive',
}

export default function IntrastatPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: meldungen = [], isError, error, refetch } = useQuery<IntrastatMeldung[]>({
    queryKey: ['intrastat'],
    queryFn: async () => (await apiClient.get<IntrastatMeldung[]>('/api/v1/intrastat/meldungen')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = meldungen.filter((m) => m.meldenummer.toLowerCase().includes(search.toLowerCase()))

  const handleExport = async (meldezeitraum: string) => {
    const response = await apiClient.post(`/api/v1/intrastat/meldungen/${meldezeitraum}/export-csv`, undefined, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `intrastat-${meldezeitraum}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    { key: 'meldenummer' as const, label: 'Meldungs-Nr', render: (m: IntrastatMeldung) => <span className="font-mono">{m.meldenummer}</span> },
    {
      key: 'meldungsart' as const,
      label: 'Typ',
      render: (m: IntrastatMeldung) => (
        <Badge variant={m.meldungsart === 'EINGANG' ? 'default' : 'secondary'}>
          {m.meldungsart === 'EINGANG' ? 'Eingang' : 'Versand'}
        </Badge>
      ),
    },
    { key: 'meldezeitraum' as const, label: 'Periode' },
    { key: 'status' as const, label: 'Status', render: (m: IntrastatMeldung) => <Badge variant={STATUS_VARIANT[m.status] ?? 'outline'}>{m.status}</Badge> },
    { key: 'statistischer_wert_eur' as const, label: 'Gesamtwert', render: (m: IntrastatMeldung) => `${m.statistischer_wert_eur.toLocaleString('de-DE', { minimumFractionDigits: 2 })} EUR` },
    {
      key: 'id' as const,
      label: 'Aktionen',
      render: (m: IntrastatMeldung) => (
        <Button size="sm" variant="outline" className="gap-1" onClick={() => { void handleExport(m.meldezeitraum) }}>
          <Download className="h-3 w-3" />CSV
        </Button>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Intrastat-Meldungen</h1>
            <p className="text-muted-foreground">Statistik des Warenverkehrs innerhalb der EU</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neue Meldung</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{meldungen.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Eingang</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{meldungen.filter((m) => m.meldungsart === 'EINGANG').length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Versand</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{meldungen.filter((m) => m.meldungsart === 'VERSAND').length}</span></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Meldungen ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Meldungs-Nr suchen..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
