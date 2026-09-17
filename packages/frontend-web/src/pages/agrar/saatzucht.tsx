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

/**
 * Schluessel wie im Endpunkt `GET /saatgut/partien`.
 *
 * Vorher stand hier ein Wunschmodell (`sorte`, `generation`, `zertifikat_nr`)
 * und der Abruf ging an `/api/v1/saatzucht` — eine Route, die es nicht gibt.
 * Der Fehler war doppelt: falscher Pfad und falsche Felder.
 */
type SaatzuchtPartie = {
  id: string
  partie_nr: string
  sorte_bezeichnung: string | null
  /** Vermehrungsstufe (Z1/Z2/…) — im Beleg heisst sie `z_stufe`. */
  z_stufe: string | null
  status: string
  anbauflaeche_ha: number | null
  anerkennungsnr: string | null
  vermehrungsbetrieb: string | null
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
    queryFn: async () => (await apiClient.get<SaatzuchtPartie[]>('/api/v1/saatzucht/partien')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const suche = search.toLowerCase()
  const filtered = partien.filter(
    (p) =>
      (p.partie_nr ?? '').toLowerCase().includes(suche) ||
      (p.sorte_bezeichnung ?? '').toLowerCase().includes(suche),
  )

  const columns = [
    { key: 'partie_nr' as const, label: 'Partie-Nr', render: (p: SaatzuchtPartie) => <span className="font-mono">{p.partie_nr}</span> },
    { key: 'sorte_bezeichnung' as const, label: 'Sorte', render: (p: SaatzuchtPartie) => p.sorte_bezeichnung ?? '—' },
    { key: 'z_stufe' as const, label: 'Vermehrungsstufe', render: (p: SaatzuchtPartie) => (p.z_stufe ? <Badge variant={GEN_VARIANT[p.z_stufe] ?? 'outline'}>{p.z_stufe}</Badge> : '—') },
    { key: 'vermehrungsbetrieb' as const, label: 'Vermehrungsbetrieb', render: (p: SaatzuchtPartie) => p.vermehrungsbetrieb ?? '—' },
    { key: 'status' as const, label: 'Status' },
    // Ohne Flaeche kein "0 ha": Nicht erfasst ist etwas anderes als null.
    { key: 'anbauflaeche_ha' as const, label: 'Anbaufläche (ha)', render: (p: SaatzuchtPartie) => (p.anbauflaeche_ha == null ? '—' : `${p.anbauflaeche_ha.toLocaleString('de-DE')} ha`) },
    { key: 'anerkennungsnr' as const, label: 'Anerkennungs-Nr', render: (p: SaatzuchtPartie) => <span className="font-mono text-sm">{p.anerkennungsnr ?? '—'}</span> },
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
              <CardContent><span className="text-2xl font-bold">{partien.filter((p) => p.z_stufe === gen).length}</span></CardContent>
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
