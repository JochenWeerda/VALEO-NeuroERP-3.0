import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useErnten, type Ernte } from '@/lib/api/agrar'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { Calendar, FileDown, Plus, Search } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function ErnteListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, isError, error, refetch } = useErnten()

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const ernten: Ernte[] = data ?? []

  const columns = [
    {
      key: 'schlag' as const,
      label: 'Schlag',
      render: (e: Ernte) => (
        <button type="button" onClick={() => navigate(`/agrar/ernte/${e.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {e.schlag}
        </button>
      ),
    },
    { key: 'kultur' as const, label: 'Kultur', render: (e: Ernte) => <Badge variant="outline">{e.kultur}</Badge> },
    {
      key: 'datum' as const,
      label: 'Erntedatum',
      render: (e: Ernte) => new Date(e.datum).toLocaleDateString('de-DE'),
    },
    { key: 'menge' as const, label: 'Menge (t)', render: (e: Ernte) => e.menge > 0 ? `${e.menge} t` : '-' },
    { key: 'ertrag' as const, label: 'Ertrag (dt/ha)', render: (e: Ernte) => e.ertrag > 0 ? `${e.ertrag} dt/ha` : '-' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (e: Ernte) => (
        <Badge variant={e.status === 'abgeschlossen' ? 'outline' : e.status === 'laufend' ? 'secondary' : 'default'}>
          {e.status === 'geplant' ? 'Geplant' : e.status === 'laufend' ? 'Laufend' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  const gesamtMenge = ernten.reduce((sum, e) => sum + e.menge, 0)
  const filteredErnten = searchTerm.trim()
    ? ernten.filter((e) =>
        [e.schlag, e.kultur, e.status].some((v) => (v ?? '').toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : ernten

  const handleExport = () => {
    const header = 'Schlag;Kultur;Datum;Menge_t;Ertrag_dt_ha;Status\n'
    const rows = filteredErnten.map((e) =>
      [e.schlag, e.kultur, e.datum, e.menge, e.ertrag, e.status].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Ernte_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredErnten.length} Ernten exportiert.` })
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Ernte-Übersicht</h1>
          <p className="text-muted-foreground">Ernten suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/ernte/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Ernte
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schlaege Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{ernten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtertrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtMenge.toFixed(1)} t</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{ernten.filter((e) => e.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{ernten.filter((e) => e.status === 'geplant').length}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input aria-label="Suche Ernten" placeholder="Schlag, Kultur oder Status suchen" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredErnten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
