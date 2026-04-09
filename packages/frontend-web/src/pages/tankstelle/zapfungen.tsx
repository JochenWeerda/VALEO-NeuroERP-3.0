import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileDown, Fuel, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { toast } from '@/hooks/use-toast'
import { useZapfungen, type Zapfung } from '@/lib/api/betrieb'

export default function ZapfungenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: zapfungen = [], isError, error, refetch } = useZapfungen()

  const filteredZapfungen = useMemo(() => {
    if (!searchTerm) return zapfungen
    const term = searchTerm.toLowerCase()
    return zapfungen.filter((z) =>
      z.kennzeichen.toLowerCase().includes(term) ||
      z.fahrer.toLowerCase().includes(term) ||
      z.artikel.toLowerCase().includes(term),
    )
  }, [zapfungen, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = () => {
    const header = 'Zeitpunkt;Kennzeichen;Fahrer;Artikel;Menge\n'
    const rows = filteredZapfungen.map((z) =>
      [z.zeitstempel, z.kennzeichen, z.fahrer, z.artikel, z.menge]
        .map((value) => `"${String(value).replace(/"/g, '""')}"`)
        .join(';'),
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Zapfungen_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredZapfungen.length} Zapfungen exportiert.` })
  }

  const columns = [
    { key: 'zeitstempel' as const, label: 'Zeitpunkt', render: (z: Zapfung) => <span className="font-mono text-sm">{z.zeitstempel}</span> },
    { key: 'kennzeichen' as const, label: 'Fahrzeug', render: (z: Zapfung) => <span className="font-mono font-bold">{z.kennzeichen}</span> },
    { key: 'fahrer' as const, label: 'Fahrer' },
    { key: 'artikel' as const, label: 'Kraftstoff', render: (z: Zapfung) => <Badge variant="outline">{z.artikel}</Badge> },
    { key: 'menge' as const, label: 'Menge (l)', render: (z: Zapfung) => `${z.menge} l` },
  ]

  const gesamtMenge = filteredZapfungen.reduce((sum, z) => sum + z.menge, 0)
  const dieselCount = filteredZapfungen.filter((z) => z.artikel.toLowerCase().includes('diesel')).length

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Tankstellen-Zapfungen</h1>
        <p className="text-muted-foreground">Betriebstankstelle</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Zapfungen</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Fuel className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{filteredZapfungen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Menge</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{gesamtMenge.toFixed(1)} l</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Durchschnitt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{(gesamtMenge / Math.max(filteredZapfungen.length, 1)).toFixed(1)} l</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Diesel-Vorgaenge</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{dieselCount}</span></CardContent></Card>
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
        <CardHeader><CardTitle>Betriebs-Folgewege</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => navigate('/logistik/tourenplanung')}>Disposition</Button>
          <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Belege</Button>
          <Button variant="outline" onClick={() => navigate('/annahme/abrechnung')}>Abrechnung</Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredZapfungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
