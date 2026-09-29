import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useBodenproben, type Bodenprobe } from '@/lib/api/agrar'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { Beaker, FileDown, Plus, Search } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function BodenprobenPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const [exporting, setExporting] = useState(false)
  const { data, isLoading, isError, error, refetch } = useBodenproben()

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

  const proben: Bodenprobe[] = data ?? []
  const filteredProben = searchTerm.trim()
    ? proben.filter((p) =>
        [p.schlag, p.labor, p.status].some((v) => (v ?? '').toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : proben
  const offeneProben = filteredProben.filter((p) => p.status === 'beauftragt')
  const analysierteProben = filteredProben.filter((p) => p.status === 'analysiert')

  function persistExport(): void {
    const header = 'Schlag;Datum;Labor;N;P;K;pH;Status\n'
    const rows = filteredProben.map((p) =>
      [p.schlag, p.datum, p.labor ?? '', p.n, p.p, p.k, p.ph, p.status].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Bodenproben_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleExport(): void {
    if (exporting) return
    setExporting(true)
    try {
      persistExport()
      toast({ title: 'Export', description: `${filteredProben.length} Bodenproben exportiert.` })
    } catch {
      toast({ variant: 'destructive', title: 'Export fehlgeschlagen' })
    } finally {
      setExporting(false)
    }
  }

  const columns = [
    {
      key: 'schlag' as const,
      label: 'Schlag',
      render: (b: Bodenprobe) => (
        <button
          type="button"
          onClick={() => navigate(`/agrar/bodenprobe/${b.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {b.schlag}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Probenahme',
      render: (b: Bodenprobe) => new Date(b.datum).toLocaleDateString('de-DE'),
    },
    { key: 'labor' as const, label: 'Labor' },
    { key: 'n' as const, label: 'N', render: (b: Bodenprobe) => b.n > 0 ? `${b.n} mg` : '-' },
    { key: 'p' as const, label: 'P', render: (b: Bodenprobe) => b.p > 0 ? `${b.p} mg` : '-' },
    { key: 'k' as const, label: 'K', render: (b: Bodenprobe) => b.k > 0 ? `${b.k} mg` : '-' },
    { key: 'ph' as const, label: 'pH', render: (b: Bodenprobe) => b.ph > 0 ? b.ph.toFixed(1) : '-' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (b: Bodenprobe) => (
        <Badge variant={b.status === 'analysiert' || b.status === 'abgeschlossen' ? 'outline' : 'default'}>
          {b.status === 'beauftragt' ? 'Beauftragt' : b.status === 'analysiert' ? 'Analysiert' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Bodenproben</h1>
          <p className="text-muted-foreground">Nährstoff-Analysen suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/bodenprobe/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Bodenprobe
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Proben Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Beaker className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{proben.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Analysiert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{analysierteProben.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{offeneProben.length}</span>
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
              <Input
                aria-label="Suche Bodenproben"
                placeholder="Schlag, Labor oder Status suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={handleExport}
              disabled={exporting}
            >
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {!isTouch ? (
      <Card>
        <CardHeader>
          <CardTitle>Labor- und Beratungsfolge</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button
            variant="outline"
            className="min-h-touch touch-manipulation"
            onClick={() => offeneProben[0] && navigate(`/agrar/bodenprobe/${offeneProben[0].id}`)}
            disabled={offeneProben.length === 0}
          >
            Offene Probe öffnen
          </Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate('/agrar/psm/beratung')}>Beratung</Button>
          <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate('/dokumente/ablage')}>Dokumente</Button>
        </CardContent>
      </Card>
      ) : null}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredProben} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
