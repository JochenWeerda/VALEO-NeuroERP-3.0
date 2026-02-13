import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWartungAnlagen, type WartungAnlage } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search, Settings } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function AnlagenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: anlagen = [], isError, error, refetch } = useWartungAnlagen()

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const wartungFaellig = anlagen.filter((a) => new Date(a.naechsteWartung) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)).length

  const columns = [
    {
      key: 'name' as const,
      label: 'Anlage',
      render: (a: WartungAnlage) => (
        <div>
          <button onClick={() => navigate(`/wartung/anlage/${a.id}`)} className="font-medium text-blue-600 hover:underline">{a.name}</button>
          <div className="text-sm text-muted-foreground">{a.typ}</div>
        </div>
      ),
    },
    { key: 'standort' as const, label: 'Standort' },
    { key: 'letzteWartung' as const, label: 'Letzte Wartung', render: (a: WartungAnlage) => new Date(a.letzteWartung).toLocaleDateString('de-DE') },
    {
      key: 'naechsteWartung' as const,
      label: 'Naechste Wartung',
      render: (a: WartungAnlage) => {
        const datum = new Date(a.naechsteWartung)
        const faellig = datum < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        return <span className={faellig ? 'font-semibold text-orange-600' : ''}>{datum.toLocaleDateString('de-DE')}</span>
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: WartungAnlage) => (
        <Badge variant={a.status === 'aktiv' ? 'outline' : a.status === 'wartung' ? 'secondary' : 'destructive'}>
          {a.status === 'aktiv' ? 'Aktiv' : a.status === 'wartung' ? 'Wartung' : 'Defekt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold">Anlagen-Wartung</h1><p className="text-muted-foreground">Wartungsmanagement</p></div>
        <Button onClick={() => navigate('/wartung/anlage/neu')} className="gap-2"><Plus className="h-4 w-4" />Neue Anlage</Button>
      </div>
      {wartungFaellig > 0 && <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{wartungFaellig} Wartung(en) in den naechsten 7 Tagen faellig!</span></div></CardContent></Card>}
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Anlagen Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Settings className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{anlagen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{anlagen.filter((a) => a.status === 'aktiv').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Wartung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{anlagen.filter((a) => a.status === 'wartung').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Wartung faellig</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{wartungFaellig}</span></CardContent></Card>
      </div>
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={anlagen} columns={columns} /></CardContent></Card>
    </div>
  )
}
