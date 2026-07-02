import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, UserCog } from 'lucide-react'

type Bewerbung = {
  id: string
  bewerber_name: string
  stelle: string
  stage: 'EINGANG' | 'VORAUSWAHL' | 'ERSTGESPRAECH' | 'ENDGESPRAECH' | 'ANGEBOT' | 'EINGESTELLT' | 'ABGELEHNT'
  eingangsdatum: string
}

const STAGE_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  EINGANG: 'outline',
  VORAUSWAHL: 'secondary',
  ERSTGESPRAECH: 'secondary',
  ENDGESPRAECH: 'default',
  ANGEBOT: 'default',
  EINGESTELLT: 'default',
  ABGELEHNT: 'destructive',
}

const STAGES: Bewerbung['stage'][] = ['EINGANG', 'VORAUSWAHL', 'ERSTGESPRAECH', 'ENDGESPRAECH', 'ANGEBOT', 'EINGESTELLT', 'ABGELEHNT']

export default function BewerbungenPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: bewerbungen = [], isError, error, refetch } = useQuery<Bewerbung[]>({
    queryKey: ['bewerbungen'],
    queryFn: async () => (await apiClient.get<Bewerbung[]>('/api/v1/personal/bewerbungen')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = bewerbungen.filter(
    (b) =>
      b.bewerber_name.toLowerCase().includes(search.toLowerCase()) ||
      b.stelle.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'bewerber_name' as const, label: 'Bewerber', render: (b: Bewerbung) => <span className="font-medium">{b.bewerber_name}</span> },
    { key: 'stelle' as const, label: 'Stelle' },
    { key: 'stage' as const, label: 'Stage', render: (b: Bewerbung) => <Badge variant={STAGE_VARIANT[b.stage] ?? 'outline'}>{b.stage}</Badge> },
    { key: 'eingangsdatum' as const, label: 'Eingangsdatum', render: (b: Bewerbung) => new Date(b.eingangsdatum).toLocaleDateString('de-DE') },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Bewerbungen</h1>
            <p className="text-muted-foreground">Bewerbungen und Rekrutierungsprozesse</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neue Bewerbung</Button>
        </div>

        <div className="grid gap-2 md:grid-cols-4 lg:grid-cols-7">
          {STAGES.map((stage) => (
            <Card key={stage}>
              <CardHeader className="pb-1 pt-3 px-3"><CardTitle className="text-xs">{stage}</CardTitle></CardHeader>
              <CardContent className="pb-3 px-3">
                <span className="text-xl font-bold">{bewerbungen.filter((b) => b.stage === stage).length}</span>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><UserCog className="h-5 w-5" />Alle Bewerbungen ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Bewerber oder Stelle suchen..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
