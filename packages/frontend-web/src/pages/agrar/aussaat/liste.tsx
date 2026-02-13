import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAussaaten, type Aussaat } from '@/lib/api/agrar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { Calendar, FileDown, Plus, Search } from 'lucide-react'

export default function AussaatListePage(): JSX.Element {
  const navigate = useNavigate()
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
        <button onClick={() => navigate(`/agrar/aussaat/${a.id}`)} className="font-medium text-blue-600 hover:underline">
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

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Aussaat-Planung</h1>
          <p className="text-muted-foreground">Herbst 2025</p>
        </div>
        <Button onClick={() => navigate('/agrar/aussaat/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Aussaat
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schlaege Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
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
          <DataTable data={aussaaten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
