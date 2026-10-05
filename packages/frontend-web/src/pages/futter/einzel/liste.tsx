import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useEinzelfutter, type Einzelfutter } from '@/lib/api/futter'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type Futter = {
  id: string
  artikel: string
  art: string
  protein: number
  gvoStatus: string
  verfuegbar: number
}

export default function EinzelfutterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: apiFutter = [], isError, error, refetch } = useEinzelfutter()

  // Die Abbildung haengt nur an der Antwort — ohne useMemo bekaeme der
  // Filter unten bei jedem Tastendruck eine neue Liste und rechnete neu.
  const futter: Futter[] = useMemo(
    () =>
      apiFutter.map((f: Einzelfutter) => ({
        id: f.id,
        artikel: f.name,
        art: f.kategorie,
        protein: f.rohprotein,
        gvoStatus: 'GVO-Status n/a',
        verfuegbar: f.bestand,
      })),
    [apiFutter],
  )

  const filteredFutter = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    if (!term) return futter
    return futter.filter((f) =>
      f.artikel.toLowerCase().includes(term) ||
      f.art.toLowerCase().includes(term) ||
      f.gvoStatus.toLowerCase().includes(term),
    )
  }, [futter, searchTerm])

  // Erst nach allen Hooks aussteigen — ein Abbruch davor wuerde die
  // Hook-Reihenfolge zwischen Fehler- und Normalfall unterschiedlich machen.
  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'artikel' as const,
      label: 'Artikel',
      render: (f: Futter) => (
        <button type="button" onClick={() => navigate(`/futter/einzel/stamm/${f.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {f.artikel}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Art' },
    { key: 'protein' as const, label: 'Protein', render: (f: Futter) => `${f.protein}%` },
    { key: 'gvoStatus' as const, label: 'GVO-Status', render: (f: Futter) => <Badge variant="outline">{f.gvoStatus}</Badge> },
    { key: 'verfuegbar' as const, label: 'Verfuegbar (t)' },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Einzelfuttermittel</h1>
          <p className="text-muted-foreground">Futter suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/futter/einzel/stamm/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neues Futtermittel
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Einzelfutter"
                placeholder="Artikel oder Art"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={() => {
                const header = 'Artikel;Art;Protein;GVO;Verfuegbar\n'
                const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
                const rows = filteredFutter.map((f) => [f.artikel, f.art, f.protein, f.gvoStatus, f.verfuegbar].map(esc).join(';')).join('\n')
                const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `einzelfutter-${new Date().toISOString().slice(0, 10)}.csv`
                a.click()
                URL.revokeObjectURL(url)
              }}
            ><FileDown className="h-4 w-4" />Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card><CardContent className="pt-6"><DataTable data={filteredFutter} columns={columns} /></CardContent></Card>
    </div>
  )
}
