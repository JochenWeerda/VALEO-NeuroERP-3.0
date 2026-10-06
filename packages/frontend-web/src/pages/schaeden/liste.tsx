import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { AlertTriangle, FileDown, Plus, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { toast } from '@/hooks/use-toast'
import { useSchaeden, type Schaden } from '@/lib/api/betrieb'

/** Der Stand, wie das Register ihn fuehrt — `ENTWURF` heisst: noch nicht gemeldet. */
const STATUS_TEXT: Record<string, string> = {
  ENTWURF: 'Entwurf — noch nicht gemeldet',
  GEMELDET: 'Gemeldet',
  IN_BEARBEITUNG: 'In Bearbeitung',
  REGULIERT: 'Reguliert',
  ABGELEHNT: 'Abgelehnt',
}

export default function SchaedenListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: schaeden = [], isError, error, refetch } = useSchaeden()

  const filteredSchaeden = useMemo(() => {
    if (!searchTerm) return schaeden
    const term = searchTerm.toLowerCase()
    return schaeden.filter((s) =>
      s.meldungsnummer.toLowerCase().includes(term) ||
      s.art.toLowerCase().includes(term) ||
      (s.ort ?? '').toLowerCase().includes(term) ||
      s.status.toLowerCase().includes(term),
    )
  }, [schaeden, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = () => {
    const header = 'Schadennummer;Art;Datum;Ort;Schadenhoehe;Status\n'
    const rows = filteredSchaeden.map((s) =>
      [s.meldungsnummer, s.art, s.schadendatum ?? '', s.ort ?? '', s.schadenhoehe, s.status]
        .map((value) => `"${String(value).replace(/"/g, '""')}"`)
        .join(';'),
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Schaeden_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredSchaeden.length} Schaeden exportiert.` })
  }

  const columns = [
    {
      key: 'meldungsnummer' as const,
      label: 'Meldungsnummer',
      render: (s: Schaden) => (
        <button type="button" onClick={() => navigate(`/schaeden/${s.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {s.meldungsnummer}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Schadenart', render: (s: Schaden) => <Badge variant="outline">{s.art}</Badge> },
    { key: 'schadendatum' as const, label: 'Schadendatum', render: (s: Schaden) => (s.schadendatum ? new Date(s.schadendatum).toLocaleDateString('de-DE') : '–') },
    { key: 'ort' as const, label: 'Ort', render: (s: Schaden) => s.ort ?? '–' },
    {
      key: 'schadenhoehe' as const,
      label: 'Schadenhoehe',
      render: (s: Schaden) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(Number(s.schadenhoehe)),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schaden) => (
        <Badge variant={s.status === 'REGULIERT' ? 'outline' : s.status === 'ABGELEHNT' ? 'destructive' : 'secondary'}>
          {STATUS_TEXT[s.status] ?? s.status}
        </Badge>
      ),
    },
  ]

  // Geldbeträge kommen als Dezimalzeichenkette aus dem Backend.
  const gesamtSchaden = filteredSchaeden.reduce((sum, s) => sum + Number(s.schadenhoehe), 0)
  const reguliert = filteredSchaeden.filter((s) => s.status === 'REGULIERT').length
  const offenePruefung = filteredSchaeden.filter((s) => s.status === 'IN_BEARBEITUNG')

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Schaeden</h1>
          <p className="text-muted-foreground">Schaeden suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/schaeden/meldung')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Schaden melden
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Schaeden Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-status-warning" /><span className="text-2xl font-bold">{filteredSchaeden.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Schadenhoehe</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtSchaden)}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Reguliert</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{reguliert}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Pruefung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{offenePruefung.length}</span></CardContent></Card>
      </div>
      ) : null}

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input aria-label="Suche Schaeden" placeholder="Nummer, Art, Ort, Status" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Regulierungs-Folgewege</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => offenePruefung[0] && navigate(`/schaeden/${offenePruefung[0].id}`)} disabled={offenePruefung.length === 0}>
            Offenen Fall oeffnen
          </Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate('/dokumente/ablage')}>Dokumente</Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate('/schaeden/meldung')}>Neue Meldung</Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredSchaeden} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
