import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useMarketingKampagnen, type Kampagne } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Megaphone, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'

export default function KampagnenPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: kampagnen = [], isError, error, refetch } = useMarketingKampagnen()

  const filteredData = useMemo(
    () => kampagnen.filter((k) =>
      [k.name, k.typ, k.zielgruppe].some((v) => v.toLowerCase().includes(searchTerm.toLowerCase()))
    ),
    [kampagnen, searchTerm]
  )

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'name' as const,
      label: 'Kampagne',
      render: (k: Kampagne) => (
        <button type="button" onClick={() => navigate(`/marketing/kampagne/${k.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
          {k.name}
        </button>
      ),
    },
    { key: 'typ' as const, label: 'Typ', render: (k: Kampagne) => <Badge variant="outline">{k.typ}</Badge> },
    { key: 'zielgruppe' as const, label: 'Zielgruppe' },
    {
      key: 'startdatum' as const,
      label: 'Zeitraum',
      render: (k: Kampagne) => (
        <span className="text-sm">
          {new Date(k.startdatum).toLocaleDateString('de-DE')} - {new Date(k.enddatum).toLocaleDateString('de-DE')}
        </span>
      ),
    },
    {
      key: 'budget' as const,
      label: 'Budget',
      render: (k: Kampagne) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.budget),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (k: Kampagne) => (
        <Badge variant={k.status === 'aktiv' ? 'default' : k.status === 'geplant' ? 'outline' : 'secondary'}>
          {k.status === 'aktiv' ? 'Aktiv' : k.status === 'geplant' ? 'Geplant' : 'Beendet'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Marketing-Kampagnen</h1>
          <p className="text-muted-foreground">Kampagnen suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/marketing/kampagne/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neue Kampagne
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kampagnen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{kampagnen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{kampagnen.filter((k) => k.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{kampagnen.filter((k) => k.status === 'geplant').length}</span>
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
              <Input aria-label="Suche Kampagnen" placeholder="Name, Typ, Zielgruppe" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={() => {
                if (filteredData.length === 0) {
                  toast({ title: 'Kein Export', description: 'Keine Kampagnen in der aktuellen Sicht.', variant: 'destructive' })
                  return
                }
                exportToCSV(
                  filteredData.map((k) => ({
                    name: k.name,
                    typ: k.typ,
                    zielgruppe: k.zielgruppe,
                    startdatum: k.startdatum,
                    enddatum: k.enddatum,
                    budget: k.budget,
                    status: k.status,
                  })),
                  `kampagnen-${new Date().toISOString().slice(0, 10)}.csv`,
                  [
                    { key: 'name', label: 'Kampagne' },
                    { key: 'typ', label: 'Typ' },
                    { key: 'zielgruppe', label: 'Zielgruppe' },
                    { key: 'startdatum', label: 'Start' },
                    { key: 'enddatum', label: 'Ende' },
                    { key: 'budget', label: 'Budget' },
                    { key: 'status', label: 'Status' },
                  ],
                )
              }}
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
