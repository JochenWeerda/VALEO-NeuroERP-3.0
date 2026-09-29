import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useMischfutter, type Mischfutter as ApiMischfutter } from '@/lib/api/futter'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type Mischfutter = {
  id: string
  typ: string
  tierart: string
  protein: number
  verfuegbar: number
}

export default function MischfutterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: apiMischfutter = [], isError, error, refetch } = useMischfutter()

  // Wie in der Einzelfutterliste: die Abbildung haengt nur an der Antwort.
  const mischfutter: Mischfutter[] = useMemo(
    () =>
      apiMischfutter.map((m: ApiMischfutter) => ({
        id: m.id,
        typ: m.name,
        tierart: m.tierart,
        protein: 0,
        verfuegbar: m.bestand,
      })),
    [apiMischfutter],
  )

  const filteredMischfutter = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    if (!term) return mischfutter
    return mischfutter.filter((m) =>
      m.typ.toLowerCase().includes(term) ||
      m.tierart.toLowerCase().includes(term),
    )
  }, [mischfutter, searchTerm])

  // Erst nach allen Hooks aussteigen.
  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (m: Mischfutter) => (
        <button type="button" onClick={() => navigate(`/futter/misch/stamm/${m.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {m.typ}
        </button>
      ),
    },
    { key: 'tierart' as const, label: 'Tierart' },
    { key: 'protein' as const, label: 'Protein (%)', render: (m: Mischfutter) => `${m.protein}%` },
    { key: 'verfuegbar' as const, label: 'Verfuegbar (t)' },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Mischfuttermittel</h1>
          <p className="text-muted-foreground">Mischfutter suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/futter/misch/stamm/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neues Mischfutter
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Mischfutter"
                placeholder="Typ oder Tierart"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={() => {
                const header = 'Typ;Tierart;Protein;Verfuegbar\n'
                const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
                const rows = filteredMischfutter.map((m) => [m.typ, m.tierart, m.protein, m.verfuegbar].map(esc).join(';')).join('\n')
                const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `mischfutter-${new Date().toISOString().slice(0, 10)}.csv`
                a.click()
                URL.revokeObjectURL(url)
              }}
            ><FileDown className="h-4 w-4" />Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card><CardContent className="pt-6"><DataTable data={filteredMischfutter} columns={columns} /></CardContent></Card>
    </div>
  )
}
