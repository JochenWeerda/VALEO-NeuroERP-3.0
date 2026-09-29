import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useKulturen, type Kultur } from '@/lib/api/agrar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import { FileDown, Plus, Search, Sprout } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function KulturpflanzenListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, isError, error, refetch } = useKulturen()

  const kulturen: Kultur[] = data ?? []

  const filteredKulturen = useMemo(
    () => kulturen.filter((k) => k.name.toLowerCase().includes(searchTerm.toLowerCase())),
    [kulturen, searchTerm]
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

  const handleExport = (): void => {
    const header = 'Kulturpflanze;Kategorie;Flaeche_ha;Ertrag_t_ha;Preis_EUR_t;DB_EUR_ha\n'
    const rows = filteredKulturen.map((k) =>
      [k.name, k.kategorie, k.flaeche, k.ertrag, k.preis, k.deckungsbeitrag].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Kulturpflanzen_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredKulturen.length} Einträge exportiert.` })
  }

  const columns = [
    {
      key: 'name' as const,
      label: 'Kulturpflanze',
      render: (k: Kultur) => (
        <button
          type="button"
          onClick={() => navigate(`/agrar/kulturpflanzen/${k.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {k.name}
        </button>
      ),
    },
    { key: 'kategorie' as const, label: 'Kategorie', render: (k: Kultur) => <Badge variant="outline">{k.kategorie}</Badge> },
    { key: 'flaeche' as const, label: 'Fläche (ha)', render: (k: Kultur) => `${k.flaeche} ha` },
    { key: 'ertrag' as const, label: 'Ertrag (t/ha)', render: (k: Kultur) => `${k.ertrag} t/ha` },
    {
      key: 'preis' as const,
      label: 'Preis (EUR/t)',
      render: (k: Kultur) => `${new Intl.NumberFormat('de-DE').format(k.preis)} EUR`,
    },
    {
      key: 'deckungsbeitrag' as const,
      label: 'DB (EUR/ha)',
      render: (k: Kultur) => <span className="font-bold">{new Intl.NumberFormat('de-DE').format(k.deckungsbeitrag)} EUR</span>,
    },
  ]

  const gesamtFlaeche = kulturen.reduce((sum, k) => sum + k.flaeche, 0)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Kulturpflanzen</h1>
          <p className="text-muted-foreground">Kulturen suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/kulturpflanzen/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Kultur
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kulturen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold">{kulturen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtfläche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtFlaeche.toFixed(1)} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Deckungsbeitrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">
              {(kulturen.reduce((sum, k) => sum + k.deckungsbeitrag, 0) / Math.max(kulturen.length, 1)).toFixed(0)} EUR / ha
            </span>
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
                aria-label="Suche Kulturpflanzen"
                placeholder="Kultur suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
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
          <DataTable data={filteredKulturen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
