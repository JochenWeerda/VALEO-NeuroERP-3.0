import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useProjekte, type Projekt } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, FolderKanban, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function ProjekteListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: projekte = [], isError, error, refetch } = useProjekte()

  const gefilterteProjekte = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return projekte
    return projekte.filter((p) =>
      [p.name, p.kunde, p.status].some((value) => value.toLowerCase().includes(needle)),
    )
  }, [projekte, searchTerm])

  const stockendeProjekte = gefilterteProjekte.filter((p) => p.status === 'pausiert' || (p.status === 'aktiv' && p.fortschritt < 35))

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const rows = [
      ['Projekt', 'Auftraggeber', 'Startdatum', 'Enddatum', 'Fortschritt', 'Budget', 'Status'],
      ...gefilterteProjekte.map((p) => [p.name, p.kunde, p.startdatum, p.enddatum, p.fortschritt, p.budget, p.status]),
    ]
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'projekte.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    { key: 'name' as const, label: 'Projekt', render: (p: Projekt) => <button type="button" onClick={() => navigate(`/projekte/${p.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">{p.name}</button> },
    { key: 'kunde' as const, label: 'Auftraggeber' },
    { key: 'startdatum' as const, label: 'Zeitraum', render: (p: Projekt) => <span className="text-sm">{new Date(p.startdatum).toLocaleDateString('de-DE')} - {new Date(p.enddatum).toLocaleDateString('de-DE')}</span> },
    { key: 'fortschritt' as const, label: 'Fortschritt', render: (p: Projekt) => <div className="flex items-center gap-2"><div className="flex-1 h-2 bg-muted rounded-full overflow-hidden max-w-24"><div className="h-full bg-primary" style={{ width: `${p.fortschritt}%` }} /></div><span className="text-sm font-semibold">{p.fortschritt}%</span></div> },
    { key: 'budget' as const, label: 'Budget', render: (p: Projekt) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(p.budget) },
    { key: 'status' as const, label: 'Status', render: (p: Projekt) => <Badge variant={p.status === 'aktiv' ? 'default' : p.status === 'abgeschlossen' ? 'outline' : 'secondary'}>{p.status === 'aktiv' ? 'Aktiv' : p.status === 'pausiert' ? 'Pausiert' : 'Abgeschlossen'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><h1 className="text-2xl font-bold md:text-3xl">Projekte</h1><p className="text-muted-foreground">Projekte suchen und oeffnen</p></div><Button onClick={() => navigate('/controlling/massnahmen')} className="min-h-touch gap-2 touch-manipulation"><Plus className="h-4 w-4" />Massnahme anlegen</Button></div>
      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Projekte Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><FolderKanban className="h-5 w-5 text-muted-foreground" /><span className="text-2xl font-bold">{gefilterteProjekte.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{gefilterteProjekte.filter((p) => p.status === 'aktiv').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Stockend/Pausiert</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{stockendeProjekte.length}</span></CardContent></Card>
      </div>
      ) : null}
      <div className={`grid gap-4 ${isTouch ? '' : 'xl:grid-cols-[minmax(0,1fr)_320px]'}`}>
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Suche Projekte" placeholder="Projekt, Auftraggeber, Status" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" /></div><Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        {!isTouch ? (
        <Card><CardHeader><CardTitle>Projekt-Folgeaktionen</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Stockende Projekte</div><div className="text-muted-foreground">{stockendeProjekte.length} Projekt(e) mit Pausen- oder Fortschrittsdruck.</div></div><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => { const target = stockendeProjekte[0] ?? gefilterteProjekte[0]; if (target) setSearchTerm(target.name) }}>Wichtigstes Projekt fokussieren</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/controlling/massnahmen')}>Massnahmenraum oeffnen</Button></CardContent></Card>
        ) : null}
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteProjekte} columns={columns} /></CardContent></Card>
    </div>
  )
}
