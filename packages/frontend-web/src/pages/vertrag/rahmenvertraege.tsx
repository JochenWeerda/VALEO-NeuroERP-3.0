import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useRahmenvertraege, type Vertrag } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, FileText, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function RahmenvertraegePage(): JSX.Element {
  const navigate = useNavigate()
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
    { key: 'nummer' as const, label: 'Vertragsnummer', render: (v: Vertrag) => <button onClick={() => navigate(`/vertrag/${v.id}`)} className="font-medium text-blue-600 hover:underline">{v.nummer}</button> },
    { key: 'partner' as const, label: 'Partner' },
    { key: 'typ' as const, label: 'Typ', render: (v: Vertrag) => <Badge variant="outline">{v.typ}</Badge> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'restmenge' as const, label: 'Restmenge', render: (v: Vertrag) => <span className={v.restmenge < v.menge * 0.2 ? 'font-semibold text-orange-600' : ''}>{v.restmenge} / {v.menge} t</span> },
    { key: 'laufzeitBis' as const, label: 'Laufzeit bis', render: (v: Vertrag) => new Date(v.laufzeitBis).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (v: Vertrag) => <Badge variant={v.status === 'aktiv' ? 'outline' : v.status === 'auslaufend' ? 'secondary' : 'destructive'}>{v.status === 'aktiv' ? 'Aktiv' : v.status === 'auslaufend' ? 'Auslaufend' : 'Beendet'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Rahmenvertraege</h1><p className="text-muted-foreground">Liefervertraege</p></div><Button onClick={() => navigate('/vertrag/neu')} className="gap-2"><Plus className="h-4 w-4" />Neuer Vertrag</Button></div>
      {auslaufendeVertraege.length > 0 && <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{auslaufendeVertraege.length} Vertrag/Vertraege laufen bald aus!</span></div></CardContent></Card>}
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Vertraege Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><FileText className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{gefilterteVertraege.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{gefilterteVertraege.filter((v) => v.status === 'aktiv').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kritische Restmenge</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{kritischeRestmengen.length}</span></CardContent></Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
        <Card><CardHeader><CardTitle>Vertragsfokus</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Operative Faelle</div><div className="text-muted-foreground">{auslaufendeVertraege.length} auslaufende und {kritischeRestmengen.length} Vertraege mit niedriger Restmenge.</div></div><Button className="w-full justify-start" variant="outline" onClick={() => { const target = auslaufendeVertraege[0] ?? kritischeRestmengen[0] ?? gefilterteVertraege[0]; if (target) navigate(`/vertrag/${target.id}`) }}>Kritischen Vertrag oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/contracts-v2')}>Kontraktsteuerung oeffnen</Button></CardContent></Card>
      </div>
      <Card><CardContent className="pt-6"><DataTable data={gefilterteVertraege} columns={columns} /></CardContent></Card>
    </div>
  )
}
