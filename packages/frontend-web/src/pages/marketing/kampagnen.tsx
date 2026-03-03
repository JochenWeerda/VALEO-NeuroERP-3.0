import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMarketingKampagnen, type Kampagne } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Megaphone, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function KampagnenPage(): JSX.Element {
  const navigate = useNavigate()
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
        <button onClick={() => navigate(`/marketing/kampagne/${k.id}`)} className="font-medium text-blue-600 hover:underline">
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
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Marketing-Kampagnen</h1>
          <p className="text-muted-foreground">Uebersicht</p>
        </div>
        <Button onClick={() => navigate('/marketing/kampagne/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Kampagne
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kampagnen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{kampagnen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{kampagnen.filter((k) => k.status === 'aktiv').length}</span>
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

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
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
