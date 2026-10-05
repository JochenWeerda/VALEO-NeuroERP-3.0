import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useAussaaten, type Aussaat } from '@/lib/api/agrar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { Calendar, FileDown, Plus, Search } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function AussaatListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, isError, error, refetch } = useAussaaten()

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

  const aussaaten: Aussaat[] = data ?? []

  const columns = [
    {
      key: 'schlag' as const,
      label: 'Schlag',
      render: (a: Aussaat) => (
        <button type="button" onClick={() => navigate(`/agrar/aussaat/${a.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {a.schlag}
        </button>
      ),
    },
    { key: 'kultur' as const, label: 'Kultur', render: (a: Aussaat) => <Badge variant="outline">{a.kultur}</Badge> },
    { key: 'sorte' as const, label: 'Sorte' },
    {
      key: 'datum' as const,
      label: 'Aussaat-Datum',
      render: (a: Aussaat) => new Date(a.datum).toLocaleDateString('de-DE'),
    },
    { key: 'flaeche' as const, label: 'Flaeche (ha)', render: (a: Aussaat) => `${a.flaeche} ha` },
    { key: 'saatmenge' as const, label: 'Saatgut (kg)' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Aussaat) => (
        <Badge variant={a.status === 'ausgesaet' ? 'outline' : 'default'}>
          {a.status === 'geplant' ? 'Geplant' : 'Ausgesaet'}
        </Badge>
      ),
    },
  ]

  const gesamtFlaeche = aussaaten.reduce((sum, a) => sum + a.flaeche, 0)
  const filteredAussaaten = searchTerm.trim()
    ? aussaaten.filter((a) =>
        [a.schlag, a.kultur, a.sorte, a.status].some((v) => String(v ?? '').toLowerCase().includes(searchTerm.toLowerCase())),
      )
    : aussaaten

  const handleExport = (): void => {
    const header = 'Schlag;Kultur;Sorte;Datum;Flaeche_ha;Saatmenge_kg;Status\n'
    const rows = filteredAussaaten.map((a) =>
      [a.schlag, a.kultur, a.sorte, a.datum, a.flaeche, a.saatmenge, a.status].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';'),
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Aussaat_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredAussaaten.length} Aussaaten exportiert.` })
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Aussaat-Planung</h1>
          <p className="text-muted-foreground">Aussaaten suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/aussaat/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Aussaat
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schlaege Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{aussaaten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtflaeche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtFlaeche.toFixed(1)} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{aussaaten.filter((a) => a.status === 'geplant').length}</span>
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
              <Input aria-label="Suche Aussaaten" placeholder="Schlag, Kultur oder Sorte suchen" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
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
          <DataTable data={filteredAussaaten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
