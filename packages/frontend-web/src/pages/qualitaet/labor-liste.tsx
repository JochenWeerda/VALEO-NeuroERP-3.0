import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useLaborAuftraege, type LaborAuftrag } from '@/lib/api/betrieb'
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

export default function LaborListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: auftraege = [], isError, error, refetch } = useLaborAuftraege()

  const gefilterteAuftraege = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return auftraege
    return auftraege.filter((l) =>
      [l.id, l.chargenId, l.labor, l.status].some((value) => String(value).toLowerCase().includes(needle)),
    )
  }, [auftraege, searchTerm])

  const offeneAuftraege = gefilterteAuftraege.filter((a) => a.status !== 'abgeschlossen')
  const operationalStatus = normalizeOperationalStatus(
    offeneAuftraege.some((auftrag) => auftrag.status === 'offen')
      ? 'wartet_auf_mensch'
      : offeneAuftraege.length > 0
        ? 'in_pruefung'
        : gefilterteAuftraege.length > 0
          ? 'abgeschlossen'
          : 'offen',
  )
  const contextSections = [
    {
      title: 'Laborlage',
      items: [
        { label: 'Offene Auftraege', value: `${offeneAuftraege.length}` },
        { label: 'In Bearbeitung', value: `${gefilterteAuftraege.filter((a) => a.status === 'in-bearbeitung').length}` },
        { label: 'Abgeschlossen', value: `${gefilterteAuftraege.filter((a) => a.status === 'abgeschlossen').length}` },
      ],
    },
    {
      title: 'Qualitaetskontext',
      items: [
        { label: 'Labore', value: `${new Set(gefilterteAuftraege.map((auftrag) => auftrag.labor).filter(Boolean)).size}` },
        { label: 'Chargen', value: `${new Set(gefilterteAuftraege.map((auftrag) => auftrag.chargenId).filter(Boolean)).size}` },
        { label: 'Naechste Aktion', value: offeneAuftraege.length > 0 ? 'Naechsten offenen Auftrag oeffnen' : 'Befunde archivieren oder exportieren' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: offeneAuftraege.length > 0 ? 'Laborlast aktiv' : 'Keine offenen Laborauftraege',
      detail: offeneAuftraege.length > 0
        ? `${offeneAuftraege.length} Auftrag/Auftraege benoetigen noch Abschluss oder Analyse.`
        : 'Alle sichtbaren Auftraege sind abgeschlossen.',
    },
    {
      label: gefilterteAuftraege[0] ? `Letzter Auftrag ${gefilterteAuftraege[0].id}` : 'Noch kein Auftrag',
      detail: gefilterteAuftraege[0]
        ? `${gefilterteAuftraege[0].labor} bearbeitet Charge ${gefilterteAuftraege[0].chargenId}.`
        : 'Die Liste enthaelt derzeit keine Auftragsobjekte.',
    },
  ]

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const rows = [
      ['Auftrag', 'Charge', 'Labor', 'Analysen', 'Datum', 'Status'],
      ...gefilterteAuftraege.map((l) => [l.id, l.chargenId, l.labor, l.analysen, l.auftragsdatum, l.status]),
    ]
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'labor-auftraege.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    { key: 'id' as const, label: 'Auftrag', render: (l: LaborAuftrag) => <button onClick={() => navigate(`/qualitaet/labor/${l.id}`)} className="font-medium text-blue-600 hover:underline">{l.id}</button> },
    { key: 'chargenId' as const, label: 'Charge', render: (l: LaborAuftrag) => <span className="font-mono">{l.chargenId}</span> },
    { key: 'labor' as const, label: 'Labor' },
    { key: 'analysen' as const, label: 'Analysen', render: (l: LaborAuftrag) => `${l.analysen} Analysen` },
    { key: 'auftragsdatum' as const, label: 'Datum', render: (l: LaborAuftrag) => new Date(l.auftragsdatum).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (l: LaborAuftrag) => <Badge variant={l.status === 'abgeschlossen' ? 'outline' : l.status === 'in-bearbeitung' ? 'secondary' : 'default'}>{l.status === 'offen' ? 'Offen' : l.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Abgeschlossen'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title="Labor-Auftraege"
        description="Der Qualitaetsraum zeigt offene Analysen, Chargebezug und naechste Folgeaktion ueber der Arbeitsliste."
        status={operationalStatus}
        owner="Qualitaet / Labor"
        blocker={offeneAuftraege.some((auftrag) => auftrag.status === 'offen') ? 'Mindestens ein Auftrag ist noch nicht gestartet.' : null}
        nextAction={offeneAuftraege.length > 0 ? 'Naechsten offenen Auftrag bearbeiten' : 'Abgeschlossene Analysen nachbereiten'}
        caseLabel="Vorgang: Laborauftrag"
        tags={['Qualitaet', 'Charge']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Analyseverlauf" items={timelineItems} />
        <OperationalContextPanel title="Labor-Kontext" sections={contextSections} />
      </div>
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Labor-Auftraege</h1><p className="text-muted-foreground">Qualitaetsanalysen</p></div><Button onClick={() => navigate('/qualitaet/labor-auftrag')} className="gap-2"><Plus className="h-4 w-4" />Neuer Auftrag</Button></div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Auftraege Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Beaker className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{gefilterteAuftraege.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{gefilterteAuftraege.filter((a) => a.status === 'in-bearbeitung').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{gefilterteAuftraege.filter((a) => a.status === 'abgeschlossen').length}</span></CardContent></Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        <Card><CardHeader><CardTitle>Labor-Folgeaktionen</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Offene Analysen</div><div className="text-muted-foreground">{offeneAuftraege.length} Auftrag/Auftraege noch nicht abgeschlossen.</div></div><Button className="w-full justify-start" variant="outline" onClick={() => { const target = offeneAuftraege[0] ?? gefilterteAuftraege[0]; if (target) navigate(`/qualitaet/labor/${target.id}`) }}>Naechsten Auftrag oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/qualitaet/labor-auftrag')}>Neuen Auftrag anlegen</Button></CardContent></Card>
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteAuftraege} columns={columns} /></CardContent></Card>
    </div>
  )
}
