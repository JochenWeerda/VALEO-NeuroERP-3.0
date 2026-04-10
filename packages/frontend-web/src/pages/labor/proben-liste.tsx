import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLaborProben, type Probe } from '@/lib/api/betrieb'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Beaker, FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export default function LaborProbenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: proben = [], isError, error, refetch } = useLaborProben()

  const gefilterteProben = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return proben
    return proben.filter((probe) =>
      [probe.probennummer, probe.typ, probe.artikel, probe.labor, probe.status]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    )
  }, [proben, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const pendingCount = gefilterteProben.filter((probe) => probe.status === 'ausstehend').length
  const processingCount = gefilterteProben.filter((probe) => probe.status === 'in-bearbeitung').length
  const completedCount = gefilterteProben.filter((probe) => probe.status === 'abgeschlossen').length
  const operationalStatus = normalizeOperationalStatus(
    pendingCount > 0 ? 'wartet_auf_mensch' : processingCount > 0 ? 'in_pruefung' : completedCount > 0 ? 'abgeschlossen' : 'offen',
  )
  const contextSections = [
    {
      title: 'Probenlage',
      items: [
        { label: 'Ausstehend', value: `${pendingCount}` },
        { label: 'In Bearbeitung', value: `${processingCount}` },
        { label: 'Abgeschlossen', value: `${completedCount}` },
      ],
    },
    {
      title: 'Labor-Kontext',
      items: [
        { label: 'Labore', value: `${new Set(gefilterteProben.map((probe) => probe.labor).filter(Boolean)).size}` },
        { label: 'Probentypen', value: `${new Set(gefilterteProben.map((probe) => probe.typ).filter(Boolean)).size}` },
        { label: 'Naechste Aktion', value: pendingCount > 0 ? 'Ausstehende Probe priorisieren' : 'Abgeschlossene Befunde dokumentieren' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: pendingCount > 0 ? 'Probenstau sichtbar' : 'Kein offener Probenstau',
      detail: pendingCount > 0
        ? `${pendingCount} Proben warten auf Start oder Zuordnung.`
        : 'Alle sichtbaren Proben befinden sich in Bearbeitung oder sind abgeschlossen.',
    },
    {
      label: processingCount > 0 ? 'Analysen laufen' : 'Keine aktive Analyse',
      detail: processingCount > 0
        ? `${processingCount} Proben werden gerade bearbeitet.`
        : 'Es gibt aktuell keinen aktiven Analyseprozess in der Liste.',
    },
  ]

  const columns = [
    { key: 'probennummer' as const, label: 'Probennummer', render: (p: Probe) => <button onClick={() => navigate(`/labor/probe/${p.id}`)} className="font-medium text-blue-600 hover:underline font-mono">{p.probennummer}</button> },
    { key: 'typ' as const, label: 'Typ', render: (p: Probe) => <Badge variant="outline">{p.typ}</Badge> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'datum' as const, label: 'Datum', render: (p: Probe) => new Date(p.datum).toLocaleDateString('de-DE') },
    { key: 'labor' as const, label: 'Labor' },
    { key: 'status' as const, label: 'Status', render: (p: Probe) => <Badge variant={p.status === 'abgeschlossen' ? 'outline' : p.status === 'in-bearbeitung' ? 'secondary' : 'default'}>{p.status === 'ausstehend' ? 'Ausstehend' : p.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Abgeschlossen'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title="Laborproben"
        description="Der Probenraum zeigt Probenstau, Laborlast und Folgeaktion vor der eigentlichen Liste."
        status={operationalStatus}
        owner="Labor / Qualitaet"
        blocker={pendingCount > 0 ? `${pendingCount} Proben sind noch ausstehend.` : null}
        nextAction={pendingCount > 0 ? 'Naechste offene Probe oeffnen' : 'Befunde pruefen und dokumentieren'}
        caseLabel="Vorgang: Probenerfassung"
        tags={['Labor', 'Qualitaet']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Probenverlauf" items={timelineItems} />
        <OperationalContextPanel title="Probenkontext" sections={contextSections} />
      </div>
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Laborproben</h1><p className="text-muted-foreground">Proben-Verwaltung</p></div><Button onClick={() => navigate('/labor/probe/neu')} className="gap-2"><Plus className="h-4 w-4" />Neue Probe</Button></div>
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Proben Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Beaker className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{gefilterteProben.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{processingCount}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{completedCount}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Ausstehend</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{pendingCount}</span></CardContent></Card>
      </div>
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteProben} columns={columns} /></CardContent></Card>
    </div>
  )
}
