import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useSorten, type Sorte } from '@/lib/api/agrar'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { FileDown, Plus, Search } from 'lucide-react'

export default function SortenregisterPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [exporting, setExporting] = useState(false)
  const { data, isLoading, isError, error, refetch } = useSorten()

  const sorten: Sorte[] = data ?? []

  const filteredData = useMemo(
    () => sorten.filter((s) =>
      [s.name, s.art, s.zuechter].some((v) => (v ?? '').toLowerCase().includes(searchTerm.toLowerCase()))
    ),
    [sorten, searchTerm]
  )

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

  function persistExport(): void {
    const header = 'Sorte;Art;Zuechter;Zulassung;Eigenschaften;Status\n'
    const rows = filteredData.map((s) =>
      [s.name, s.art ?? '', s.zuechter ?? '', s.zulassung ?? '', (s.eigenschaft ?? []).join(';'), s.status ?? ''].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Sortenregister_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleExport(): void {
    if (exporting) return
    setExporting(true)
    try {
      persistExport()
      toast({ title: 'Export', description: `${filteredData.length} Sorten exportiert.` })
    } catch {
      toast({ variant: 'destructive', title: 'Export fehlgeschlagen' })
    } finally {
      setExporting(false)
    }
  }

  const columns = [
    {
      key: 'name' as const,
      label: 'Sorte',
      render: (s: Sorte) => (
        <button
          type="button"
          onClick={() => navigate(`/agrar/saatgut/sorte/${s.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {s.name}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Art' },
    { key: 'zuechter' as const, label: 'Züchter' },
    { key: 'zulassung' as const, label: 'Zulassung' },
    {
      key: 'eigenschaft' as const,
      label: 'Eigenschaften',
      render: (s: Sorte) => (
        <div className="flex flex-wrap gap-1">
          {s.eigenschaft.slice(0, 2).map((e, i) => (
            <Badge key={i} variant="outline">{e}</Badge>
          ))}
          {s.eigenschaft.length > 2 && <Badge variant="secondary">+{s.eigenschaft.length - 2}</Badge>}
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Sorte) => (
        <Badge variant={s.status === 'aktiv' ? 'outline' : 'secondary'}>
          {s.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Sortenregister</h1>
          <p className="text-muted-foreground">Saatgut-Sorten suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/saatgut/sorte/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Sorte
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Sorten"
                placeholder="Sorte, Art oder Züchter suchen"
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

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredData} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
