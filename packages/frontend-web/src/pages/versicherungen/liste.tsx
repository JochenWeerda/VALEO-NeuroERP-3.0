import { useMemo, useState } from 'react'
import { Callout } from '@/components/ui/callout'
import { useNavigate } from '@/app/routing/typed-router'
import { useVersicherungen, type Versicherung } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search, Shield } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function VersicherungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: versicherungen = [], isError, error, refetch } = useVersicherungen()

  const gefilterteVersicherungen = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return versicherungen
    return versicherungen.filter((v) =>
      [v.art, v.versicherer, v.vertragsnummer, v.status].some((value) => value.toLowerCase().includes(needle)),
    )
  }, [searchTerm, versicherungen])

  const kritischePolicen = gefilterteVersicherungen.filter((v) => new Date(v.ablauf) < new Date(Date.now() + 60 * 24 * 60 * 60 * 1000))

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const rows = [
      ['Art', 'Versicherer', 'Vertragsnummer', 'Praemie', 'Ablauf', 'Status'],
      ...gefilterteVersicherungen.map((v) => [v.art, v.versicherer, v.vertragsnummer, v.praemie, v.ablauf, v.status]),
    ]
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'versicherungen.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    { key: 'art' as const, label: 'Art', render: (v: Versicherung) => <button type="button" onClick={() => navigate(`/versicherungen/${v.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">{v.art}</button> },
    { key: 'versicherer' as const, label: 'Versicherer' },
    { key: 'vertragsnummer' as const, label: 'Vertragsnummer', render: (v: Versicherung) => <span className="font-mono text-sm">{v.vertragsnummer}</span> },
    { key: 'praemie' as const, label: 'Praemie (jaehrl.)', render: (v: Versicherung) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v.praemie) },
    { key: 'ablauf' as const, label: 'Ablauf', render: (v: Versicherung) => { const datum = new Date(v.ablauf); const bald = datum < new Date(Date.now() + 60 * 24 * 60 * 60 * 1000); return <span className={bald ? 'font-semibold text-status-warning' : ''}>{datum.toLocaleDateString('de-DE')}</span> } },
    { key: 'status' as const, label: 'Status', render: (v: Versicherung) => <Badge variant={v.status === 'aktiv' ? 'outline' : v.status === 'auslaufend' ? 'secondary' : 'destructive'}>{v.status === 'aktiv' ? 'Aktiv' : v.status === 'auslaufend' ? 'Auslaufend' : 'Gekuendigt'}</Badge> },
  ]

  const gesamtPraemie = gefilterteVersicherungen.reduce((sum, v) => sum + v.praemie, 0)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><h1 className="text-2xl font-bold md:text-3xl">Versicherungen</h1><p className="text-muted-foreground">Policen suchen und pruefen</p></div><Button onClick={() => navigate('/crm/aktivitaet/neu')} className="min-h-touch gap-2 touch-manipulation"><Plus className="h-4 w-4" />Wiedervorlage anlegen</Button></div>
      {kritischePolicen.length > 0 && <Callout variant="warning" className="pt-4"><div className="flex items-center gap-2 text-status-warning"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{kritischePolicen.length} Versicherung(en) laufen in den naechsten 60 Tagen ab!</span></div></Callout>}
      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Versicherungen Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Shield className="h-5 w-5 text-muted-foreground" /><span className="text-2xl font-bold">{gefilterteVersicherungen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Praemie (jaehrl.)</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtPraemie)}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Ablauf in 60 Tagen</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{kritischePolicen.length}</span></CardContent></Card>
      </div>
      ) : null}
      <div className={`grid gap-4 ${isTouch ? '' : 'xl:grid-cols-[minmax(0,1fr)_320px]'}`}>
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Suche Versicherungen" placeholder="Art, Versicherer, Vertrag" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" /></div><Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        {!isTouch ? (
        <Card><CardHeader><CardTitle>Policen-Fokus</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Ablaufdruck</div><div className="text-muted-foreground">{kritischePolicen.length} kritische Policen im aktuellen Arbeitsraum.</div></div><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => { const target = kritischePolicen[0] ?? gefilterteVersicherungen[0]; if (target) setSearchTerm(target.vertragsnummer) }}>Kritische Police fokussieren</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full min-h-touch justify-start" variant="outline" onClick={() => navigate('/crm/aktivitaet/neu')}>Wiedervorlage anlegen</Button></CardContent></Card>
        ) : null}
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteVersicherungen} columns={columns} /></CardContent></Card>
    </div>
  )
}
