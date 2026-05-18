import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, Leaf } from 'lucide-react'

type SaatzuchtPartie = {
  id: string
  partie_nr: string
  sorte: string
  generation: 'Z1' | 'Z2' | 'Z3' | 'ZA'
  status: string
  anbauflaeche_ha: number
  zertifikat_nr: string
}

const GEN_VARIANT: Record<string, 'default' | 'secondary' | 'outline'> = {
  Z1: 'default',
  Z2: 'secondary',
  Z3: 'outline',
  ZA: 'outline',
}

export default function SaatzuchtPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: partien = [], isError, error, refetch } = useQuery<SaatzuchtPartie[]>({
    queryKey: ['saatzucht'],
    queryFn: async () => (await apiClient.get<SaatzuchtPartie[]>('/api/v1/saatzucht')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = partien.filter(
    (p) =>
      p.partie_nr.toLowerCase().includes(search.toLowerCase()) ||
      p.sorte.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'partie_nr' as const, label: 'Partie-Nr', render: (p: SaatzuchtPartie) => <span className="font-mono">{p.partie_nr}</span> },
    { key: 'sorte' as const, label: 'Sorte' },
    { key: 'generation' as const, label: 'Generation', render: (p: SaatzuchtPartie) => <Badge variant={GEN_VARIANT[p.generation] ?? 'outline'}>{p.generation}</Badge> },
    { key: 'status' as const, label: 'Status' },
    { key: 'anbauflaeche_ha' as const, label: 'Anbaufläche (ha)', render: (p: SaatzuchtPartie) => `${p.anbauflaeche_ha.toLocaleString('de-DE')} ha` },
    { key: 'zertifikat_nr' as const, label: 'Zertifikat-Nr', render: (p: SaatzuchtPartie) => <span className="font-mono text-sm">{p.zertifikat_nr}</span> },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Saatzucht</h1>
            <p className="text-muted-foreground">Partien und Zertifizierungen verwalten</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neue Partie</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {(['Z1', 'Z2', 'Z3', 'ZA'] as const).map((gen) => (
            <Card key={gen}>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Leaf className="h-4 w-4" />Generation {gen}</CardTitle></CardHeader>
              <CardContent><span className="text-2xl font-bold">{partien.filter((p) => p.generation === gen).length}</span></CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader><CardTitle>Saatzucht-Partien ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Partie-Nr oder Sorte..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
