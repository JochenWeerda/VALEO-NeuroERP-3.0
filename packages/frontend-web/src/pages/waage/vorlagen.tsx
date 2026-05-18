import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, FileText } from 'lucide-react'

type WaagenVorlage = {
  id: string
  name: string
  beschreibung: string
  artikel_name: string
  fahrzeug_typ: string
}

export default function WaagenVorlagenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showNew, setShowNew] = useState(false)
  const [newName, setNewName] = useState('')

  const { data: vorlagen = [], isError, error, refetch } = useQuery<WaagenVorlage[]>({
    queryKey: ['waage-vorlagen'],
    queryFn: async () => (await apiClient.get('/api/v1/waage/vorlagen')).data,
  })

  const createMutation = useMutation({
    mutationFn: async (name: string) =>
      (await apiClient.post('/api/v1/waage/vorlagen', { name })).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['waage-vorlagen'] })
      setShowNew(false)
      setNewName('')
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = vorlagen.filter(
    (v) =>
      v.name.toLowerCase().includes(search.toLowerCase()) ||
      v.artikel_name.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'name' as const, label: 'Name', render: (v: WaagenVorlage) => <span className="font-medium">{v.name}</span> },
    { key: 'beschreibung' as const, label: 'Beschreibung' },
    { key: 'artikel_name' as const, label: 'Artikel' },
    { key: 'fahrzeug_typ' as const, label: 'Fahrzeugtyp', render: (v: WaagenVorlage) => <Badge variant="outline">{v.fahrzeug_typ}</Badge> },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Waagenvorlagen</h1>
            <p className="text-muted-foreground">Vorlagen für Wiegevorgänge verwalten</p>
          </div>
          <Button onClick={() => setShowNew(true)} className="gap-2">
            <Plus className="h-4 w-4" />Neue Vorlage
          </Button>
        </div>

        {showNew && (
          <Card>
            <CardHeader><CardTitle>Neue Vorlage anlegen</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Vorlagenname"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />
                <Button onClick={() => createMutation.mutate(newName)} disabled={!newName}>Speichern</Button>
                <Button variant="outline" onClick={() => setShowNew(false)}>Abbrechen</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5" />Vorlagen ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Suche nach Name oder Artikel..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
