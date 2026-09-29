import { useMemo, useState } from 'react'
import { Callout } from '@/components/ui/callout'
import { useNavigate } from '@/app/routing/typed-router'
import { useRahmenvertraege, type Vertrag } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, FileText, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function RahmenvertraegePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: vertraege = [], isError, error, refetch } = useRahmenvertraege()

  const gefilterteVertraege = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return vertraege
    return vertraege.filter((v) =>
      [v.nummer, v.partner, v.typ, v.artikel, v.status].some((value) => value.toLowerCase().includes(needle)),
    )
  }, [searchTerm, vertraege])

  const auslaufendeVertraege = gefilterteVertraege.filter((v) => v.status === 'auslaufend')
  const kritischeRestmengen = gefilterteVertraege.filter((v) => v.restmenge < v.menge * 0.2)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const rows = [
      ['Vertragsnummer', 'Partner', 'Typ', 'Artikel', 'Restmenge', 'Menge', 'Laufzeit bis', 'Status'],
      ...gefilterteVertraege.map((v) => [v.nummer, v.partner, v.typ, v.artikel, v.restmenge, v.menge, v.laufzeitBis, v.status]),
    ]
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'rahmenvertraege.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    { key: 'nummer' as const, label: 'Vertragsnummer', render: (v: Vertrag) => <button type="button" onClick={() => navigate(`/vertrag/${v.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">{v.nummer}</button> },
    { key: 'partner' as const, label: 'Partner' },
    { key: 'typ' as const, label: 'Typ', render: (v: Vertrag) => <Badge variant="outline">{v.typ}</Badge> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'restmenge' as const, label: 'Restmenge', render: (v: Vertrag) => <span className={v.restmenge < v.menge * 0.2 ? 'font-semibold text-status-warning' : ''}>{v.restmenge} / {v.menge} t</span> },
    { key: 'laufzeitBis' as const, label: 'Laufzeit bis', render: (v: Vertrag) => new Date(v.laufzeitBis).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (v: Vertrag) => <Badge variant={v.status === 'aktiv' ? 'outline' : v.status === 'auslaufend' ? 'secondary' : 'destructive'}>{v.status === 'aktiv' ? 'Aktiv' : v.status === 'auslaufend' ? 'Auslaufend' : 'Beendet'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><h1 className="text-2xl font-bold md:text-3xl">Rahmenvertraege</h1><p className="text-muted-foreground">Vertraege suchen und oeffnen</p></div><Button onClick={() => navigate('/vertrag/neu')} className="min-h-touch gap-2 touch-manipulation"><Plus className="h-4 w-4" />Neuer Vertrag</Button></div>
      {auslaufendeVertraege.length > 0 && <Callout variant="warning" className="pt-4"><div className="flex items-center gap-2 text-status-warning"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{auslaufendeVertraege.length} Vertrag/Vertraege laufen bald aus!</span></div></Callout>}
      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Vertraege Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><FileText className="h-5 w-5 text-muted-foreground" /><span className="text-2xl font-bold">{gefilterteVertraege.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{gefilterteVertraege.filter((v) => v.status === 'aktiv').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kritische Restmenge</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{kritischeRestmengen.length}</span></CardContent></Card>
      </div>
      ) : null}
      <div className={`grid gap-4 ${isTouch ? '' : 'xl:grid-cols-[minmax(0,1fr)_320px]'}`}>
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Suche Rahmenvertraege" placeholder="Nummer, Partner, Artikel" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" /></div><Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        {!isTouch ? (
        <Card><CardHeader><CardTitle>Vertragsfokus</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Operative Faelle</div><div className="text-muted-foreground">{auslaufendeVertraege.length} auslaufende und {kritischeRestmengen.length} Vertraege mit niedriger Restmenge.</div></div><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => { const target = auslaufendeVertraege[0] ?? kritischeRestmengen[0] ?? gefilterteVertraege[0]; if (target) navigate(`/vertrag/${target.id}`) }}>Kritischen Vertrag oeffnen</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/contracts-v2')}>Kontraktsteuerung oeffnen</Button></CardContent></Card>
        ) : null}
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteVertraege} columns={columns} /></CardContent></Card>
    </div>
  )
}
