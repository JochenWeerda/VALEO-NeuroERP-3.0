import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search } from 'lucide-react'

type KontraktKlasse = {
  id: string
  klassen_code: string
  name: string
  kontrakt_typ: 'FIXPREIS' | 'BASIS' | 'PRAEMIE' | 'POOLPREIS'
  incoterm_parität: string
}

const TYP_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  FIXPREIS: 'default',
  BASIS: 'secondary',
  PRAEMIE: 'outline',
  POOLPREIS: 'destructive',
}

export default function KontraktklassenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showNew, setShowNew] = useState(false)
  const [newCode, setNewCode] = useState('')
  const [newName, setNewName] = useState('')

  const { data: klassen = [], isError, error, refetch } = useQuery<KontraktKlasse[]>({
    queryKey: ['kontrakt-klassen'],
    queryFn: async () => (await apiClient.get('/api/v1/kontrakt-klassen')).data,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: { klassen_code: string; name: string }) =>
      (await apiClient.post('/api/v1/kontrakt-klassen', payload)).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['kontrakt-klassen'] })
      setShowNew(false)
      setNewCode('')
      setNewName('')
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = klassen.filter(
    (k) =>
      k.klassen_code.toLowerCase().includes(search.toLowerCase()) ||
      k.name.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'klassen_code' as const, label: 'Code', render: (k: KontraktKlasse) => <span className="font-mono font-medium">{k.klassen_code}</span> },
    { key: 'name' as const, label: 'Name' },
    {
      key: 'kontrakt_typ' as const,
      label: 'Kontrakttyp',
      render: (k: KontraktKlasse) => (
        <Badge variant={TYP_VARIANT[k.kontrakt_typ] ?? 'outline'}>{k.kontrakt_typ}</Badge>
      ),
    },
    { key: 'incoterm_parität' as const, label: 'INCOTERM' },
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
                <Input placeholder="Code (z.B. FK1)" value={newCode} onChange={(e) => setNewCode(e.target.value)} />
                <Input placeholder="Bezeichnung" value={newName} onChange={(e) => setNewName(e.target.value)} />
                <Button onClick={() => createMutation.mutate({ klassen_code: newCode, name: newName })} disabled={!newCode || !newName}>Speichern</Button>
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
                <Input placeholder="Suche Code oder Name..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
              </div>
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
