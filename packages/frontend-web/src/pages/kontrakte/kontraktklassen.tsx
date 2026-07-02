import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Plus, Search } from 'lucide-react'

// Backend-Vertrag: app/api/v1/endpoints/kontrakt_klassen.py
// (id, name, beschreibung, variante, parität, incoterm_ort, notiz)
type KontraktVariante = 'FIXPREIS' | 'BASIS' | 'PRAEMIE' | 'POOLPREIS'

type KontraktKlasse = {
  id: string
  name: string
  beschreibung: string | null
  variante: KontraktVariante
  'parität': string | null
  incoterm_ort: string | null
  notiz: string | null
}

const TYP_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  FIXPREIS: 'default',
  BASIS: 'secondary',
  PRAEMIE: 'outline',
  POOLPREIS: 'destructive',
}

const VARIANTEN: KontraktVariante[] = ['FIXPREIS', 'BASIS', 'PRAEMIE', 'POOLPREIS']

export default function KontraktklassenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [search, setSearch] = useState('')
  const [showNew, setShowNew] = useState(false)
  const [newName, setNewName] = useState('')
  const [newVariante, setNewVariante] = useState<KontraktVariante>('FIXPREIS')

  const { data: klassen = [], isError, error, refetch } = useQuery<KontraktKlasse[]>({
    queryKey: ['kontrakt-klassen'],
    queryFn: async () => (await apiClient.get<KontraktKlasse[]>('/api/v1/kontrakt-klassen')).data,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: { name: string; variante: KontraktVariante }) =>
      (await apiClient.post('/api/v1/kontrakt-klassen', payload)).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['kontrakt-klassen'] })
      setShowNew(false)
      setNewName('')
      toast({ title: 'Kontraktklasse angelegt' })
    },
    onError: (err: Error & { response?: { data?: { detail?: unknown } } }) => {
      const detail = err.response?.data?.detail
      toast({
        title: 'Anlegen fehlgeschlagen',
        description: typeof detail === 'string' ? detail : err.message,
        variant: 'destructive',
      })
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  // Felder können bei unvollständigen Backend-Zeilen fehlen — defensiv filtern
  const filtered = klassen.filter(
    (k) =>
      (k.name ?? '').toLowerCase().includes(search.toLowerCase()) ||
      (k.beschreibung ?? '').toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'name' as const, label: 'Name', render: (k: KontraktKlasse) => <span className="font-medium">{k.name}</span> },
    { key: 'beschreibung' as const, label: 'Beschreibung', render: (k: KontraktKlasse) => k.beschreibung ?? '—' },
    {
      key: 'variante' as const,
      label: 'Kontrakttyp',
      render: (k: KontraktKlasse) => (
        <Badge variant={TYP_VARIANT[k.variante] ?? 'outline'}>{k.variante}</Badge>
      ),
    },
    {
      key: 'parität' as const,
      label: 'INCOTERM / Parität',
      render: (k: KontraktKlasse) =>
        [k['parität'], k.incoterm_ort].filter(Boolean).join(' — ') || '—',
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Kontraktklassen</h1>
            <p className="text-muted-foreground">Klassen und Typen für Kontrakte verwalten</p>
          </div>
          <Button onClick={() => setShowNew(true)} className="gap-2">
            <Plus className="h-4 w-4" />Neue Klasse
          </Button>
        </div>

        {showNew && (
          <Card>
            <CardHeader><CardTitle>Neue Kontraktklasse</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input placeholder="Bezeichnung" value={newName} onChange={(e) => setNewName(e.target.value)} />
                <select
                  value={newVariante}
                  onChange={(e) => setNewVariante(e.target.value as KontraktVariante)}
                  className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {VARIANTEN.map((v) => <option key={v} value={v}>{v}</option>)}
                </select>
                <Button
                  onClick={() => createMutation.mutate({ name: newName, variante: newVariante })}
                  disabled={!newName || createMutation.isPending}
                >
                  {createMutation.isPending ? 'Speichert...' : 'Speichern'}
                </Button>
                <Button variant="outline" onClick={() => setShowNew(false)}>Abbrechen</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle>Klassen ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input placeholder="Suche Name oder Beschreibung..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
              </div>
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
