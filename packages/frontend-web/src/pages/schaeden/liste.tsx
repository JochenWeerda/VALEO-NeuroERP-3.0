import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { AlertTriangle, FileDown, Plus, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { toast } from '@/hooks/use-toast'
import { useSchaeden, type Schaden } from '@/lib/api/betrieb'

export default function SchaedenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: schaeden = [], isError, error, refetch } = useSchaeden()

  const filteredSchaeden = useMemo(() => {
    if (!searchTerm) return schaeden
    const term = searchTerm.toLowerCase()
    return schaeden.filter((s) =>
      s.nummer.toLowerCase().includes(term) ||
      s.art.toLowerCase().includes(term) ||
      s.ort.toLowerCase().includes(term) ||
      s.status.toLowerCase().includes(term),
    )
  }, [schaeden, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = () => {
    const header = 'Schadennummer;Art;Datum;Ort;Schadenhoehe;Status\n'
    const rows = filteredSchaeden.map((s) =>
      [s.nummer, s.art, s.datum, s.ort, s.schadenhoehe, s.status]
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
      key: 'nummer' as const,
      label: 'Schadennummer',
      render: (s: Schaden) => (
        <button onClick={() => navigate(`/schaeden/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.nummer}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Schadenart', render: (s: Schaden) => <Badge variant="outline">{s.art}</Badge> },
    { key: 'datum' as const, label: 'Datum', render: (s: Schaden) => new Date(s.datum).toLocaleDateString('de-DE') },
    { key: 'ort' as const, label: 'Ort' },
    {
      key: 'schadenhoehe' as const,
      label: 'Schadenhoehe',
      render: (s: Schaden) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.schadenhoehe),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schaden) => (
        <Badge variant={s.status === 'reguliert' ? 'outline' : s.status === 'abgelehnt' ? 'destructive' : 'secondary'}>
          {s.status === 'gemeldet' ? 'Gemeldet' : s.status === 'in-pruefung' ? 'In Pruefung' : s.status === 'reguliert' ? 'Reguliert' : 'Abgelehnt'}
        </Badge>
      ),
    },
  ]

  const gesamtSchaden = filteredSchaeden.reduce((sum, s) => sum + s.schadenhoehe, 0)
  const reguliert = filteredSchaeden.filter((s) => s.status === 'reguliert').length
  const offenePruefung = filteredSchaeden.filter((s) => s.status === 'in-pruefung')

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schaeden</h1>
          <p className="text-muted-foreground">Schaden-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/schaeden/meldung')} className="gap-2">
          <Plus className="h-4 w-4" />
          Schaden melden
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Schaeden Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-orange-600" /><span className="text-2xl font-bold">{filteredSchaeden.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Schadenhoehe</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtSchaden)}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Reguliert</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{reguliert}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Pruefung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{offenePruefung.length}</span></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Regulierungs-Folgewege</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => offenePruefung[0] && navigate(`/schaeden/${offenePruefung[0].id}`)} disabled={offenePruefung.length === 0}>
            Offenen Fall oeffnen
          </Button>
          <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumente</Button>
          <Button variant="outline" onClick={() => navigate('/schaeden/meldung')}>Neue Meldung</Button>
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
