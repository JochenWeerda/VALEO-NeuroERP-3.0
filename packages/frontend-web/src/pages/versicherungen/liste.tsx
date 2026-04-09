import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useVersicherungen, type Versicherung } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search, Shield } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function VersicherungenListePage(): JSX.Element {
  const navigate = useNavigate()
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
    { key: 'art' as const, label: 'Art', render: (v: Versicherung) => <button onClick={() => navigate(`/versicherungen/${v.id}`)} className="font-medium text-blue-600 hover:underline">{v.art}</button> },
    { key: 'versicherer' as const, label: 'Versicherer' },
    { key: 'vertragsnummer' as const, label: 'Vertragsnummer', render: (v: Versicherung) => <span className="font-mono text-sm">{v.vertragsnummer}</span> },
    { key: 'praemie' as const, label: 'Praemie (jaehrl.)', render: (v: Versicherung) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v.praemie) },
    { key: 'ablauf' as const, label: 'Ablauf', render: (v: Versicherung) => { const datum = new Date(v.ablauf); const bald = datum < new Date(Date.now() + 60 * 24 * 60 * 60 * 1000); return <span className={bald ? 'font-semibold text-orange-600' : ''}>{datum.toLocaleDateString('de-DE')}</span> } },
    { key: 'status' as const, label: 'Status', render: (v: Versicherung) => <Badge variant={v.status === 'aktiv' ? 'outline' : v.status === 'auslaufend' ? 'secondary' : 'destructive'}>{v.status === 'aktiv' ? 'Aktiv' : v.status === 'auslaufend' ? 'Auslaufend' : 'Gekuendigt'}</Badge> },
  ]

  const gesamtPraemie = gefilterteVersicherungen.reduce((sum, v) => sum + v.praemie, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Versicherungen</h1><p className="text-muted-foreground">Versicherungs-Verwaltung</p></div><Button onClick={() => navigate('/crm/aktivitaet/neu')} className="gap-2"><Plus className="h-4 w-4" />Wiedervorlage anlegen</Button></div>
      {kritischePolicen.length > 0 && <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{kritischePolicen.length} Versicherung(en) laufen in den naechsten 60 Tagen ab!</span></div></CardContent></Card>}
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Versicherungen Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Shield className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{gefilterteVersicherungen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Praemie (jaehrl.)</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtPraemie)}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Ablauf in 60 Tagen</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{kritischePolicen.length}</span></CardContent></Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        <Card><CardHeader><CardTitle>Policen-Fokus</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Ablaufdruck</div><div className="text-muted-foreground">{kritischePolicen.length} kritische Policen im aktuellen Arbeitsraum.</div></div><Button className="w-full justify-start" variant="outline" onClick={() => { const target = kritischePolicen[0] ?? gefilterteVersicherungen[0]; if (target) setSearchTerm(target.vertragsnummer) }}>Kritische Police fokussieren</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/crm/aktivitaet/neu')}>Wiedervorlage anlegen</Button></CardContent></Card>
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteVersicherungen} columns={columns} /></CardContent></Card>
    </div>
  )
}
