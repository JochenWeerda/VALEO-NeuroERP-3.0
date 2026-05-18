import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, Users } from 'lucide-react'

type Mitglied = {
  id: string
  mitglieds_nr: string
  name: string
  vorname: string
  eintrittsdatum: string
  geschaeftsanteile: number
  gesamtkapital: number
}

export default function GenossenschaftMitgliederPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: mitglieder = [], isError, error, refetch } = useQuery<Mitglied[]>({
    queryKey: ['genossenschaft-mitglieder'],
    queryFn: async () => (await apiClient.get('/api/v1/genossenschaft/mitglieder')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = mitglieder.filter(
    (m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.mitglieds_nr.toLowerCase().includes(search.toLowerCase()),
  )

  const gesamtkapital = mitglieder.reduce((sum, m) => sum + m.gesamtkapital, 0)

  const columns = [
    { key: 'mitglieds_nr' as const, label: 'Mitglieds-Nr', render: (m: Mitglied) => <span className="font-mono">{m.mitglieds_nr}</span> },
    { key: 'name' as const, label: 'Name', render: (m: Mitglied) => `${m.name}, ${m.vorname}` },
    { key: 'eintrittsdatum' as const, label: 'Eintrittsdatum', render: (m: Mitglied) => new Date(m.eintrittsdatum).toLocaleDateString('de-DE') },
    { key: 'geschaeftsanteile' as const, label: 'Geschäftsanteile', render: (m: Mitglied) => m.geschaeftsanteile.toLocaleString('de-DE') },
    { key: 'gesamtkapital' as const, label: 'Gesamtkapital', render: (m: Mitglied) => `${m.gesamtkapital.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €` },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Genossenschaftsmitglieder</h1>
            <p className="text-muted-foreground">Mitgliederverwaltung der Genossenschaft</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neues Mitglied</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Users className="h-4 w-4" />Gesamtmitglieder</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{mitglieder.length}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Gesamtkapital</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{gesamtkapital.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</span></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Mitgliederliste ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Name oder Mitglieds-Nr..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
