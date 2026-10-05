import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useFoerderAntraege, type Antrag } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function FoerderantraegeListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: antraege = [], isLoading } = useFoerderAntraege()

  const filteredAntraege = useMemo(() => {
    if (!searchTerm) return antraege
    const term = searchTerm.toLowerCase()
    return antraege.filter(a => 
      a.nummer?.toLowerCase().includes(term) ||
      a.programm?.toLowerCase().includes(term)
    )
  }, [antraege, searchTerm])

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-2" />
          </div>
          <Skeleton className="h-10 w-48" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
        </div>
        <Card><CardContent className="pt-4"><Skeleton className="h-64 w-full" /></CardContent></Card>
      </div>
    )
  }

  const columns = [
    { key: 'nummer' as const, label: 'Antragsnummer', render: (a: Antrag) => <button type="button" onClick={() => navigate(`/foerderung/antrag/${a.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">{a.nummer}</button> },
    { key: 'programm' as const, label: 'Programm', render: (a: Antrag) => <Badge variant="outline">{a.programm}</Badge> },
    { key: 'antragsdatum' as const, label: 'Antragsdatum', render: (a: Antrag) => new Date(a.antragsdatum).toLocaleDateString('de-DE') },
    { key: 'flaeche' as const, label: 'Flaeche (ha)', render: (a: Antrag) => `${a.flaeche} ha` },
    { key: 'betrag' as const, label: 'Betrag', render: (a: Antrag) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.betrag) },
    { key: 'status' as const, label: 'Status', render: (a: Antrag) => <Badge variant={a.status === 'bewilligt' ? 'outline' : a.status === 'abgelehnt' ? 'destructive' : 'secondary'}>{a.status === 'entwurf' ? 'Entwurf' : a.status === 'eingereicht' ? 'Eingereicht' : a.status === 'bewilligt' ? 'Bewilligt' : 'Abgelehnt'}</Badge> },
  ]

  const gesamtBetrag = antraege.filter((a) => a.status === 'bewilligt').reduce((sum, a) => sum + a.betrag, 0)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><h1 className="text-2xl font-bold md:text-3xl">Foerderantraege</h1><p className="text-muted-foreground">Antraege suchen und oeffnen</p></div><Button onClick={() => navigate('/foerderung/antrag')} className="min-h-touch gap-2 touch-manipulation"><Plus className="h-4 w-4" />Neuer Antrag</Button></div>
      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Antraege Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><FileText className="h-5 w-5 text-muted-foreground" /><span className="text-2xl font-bold">{antraege.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bewilligt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{antraege.filter((a) => a.status === 'bewilligt').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Eingereicht</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{antraege.filter((a) => a.status === 'eingereicht').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bewilligte Summe</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBetrag)}</span></CardContent></Card>
      </div>
      ) : null}
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Suche Foerderantraege" placeholder="Nummer oder Programm" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" /></div><Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={() => {
        const header = 'Nummer;Programm;Antragsdatum;Flaeche;Betrag;Status\n'
        const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
        const rows = filteredAntraege.map((a) => [a.nummer, a.programm, a.antragsdatum, a.flaeche, a.betrag, a.status].map(esc).join(';')).join('\n')
        const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `foerderantraege-${new Date().toISOString().slice(0, 10)}.csv`
        link.click()
        URL.revokeObjectURL(url)
      }}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={filteredAntraege} columns={columns} /></CardContent></Card>
    </div>
  )
}
