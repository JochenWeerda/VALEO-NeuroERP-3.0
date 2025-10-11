import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Calendar, FileDown, Plus, Search } from 'lucide-react'

type Ernte = {
  id: string
  schlag: string
  kultur: string
  datum: string
  menge: number
  ertrag: number
  status: 'geplant' | 'laufend' | 'abgeschlossen'
}

const mockErnten: Ernte[] = [
  { id: '1', schlag: 'Nordfeld 1', kultur: 'Weizen', datum: '2025-08-15', menge: 150, ertrag: 12.0, status: 'abgeschlossen' },
  { id: '2', schlag: 'Südacker', kultur: 'Raps', datum: '2025-07-20', menge: 66.4, ertrag: 8.0, status: 'abgeschlossen' },
  { id: '3', schlag: 'Wiesengrund', kultur: 'Mais', datum: '2025-10-25', menge: 0, ertrag: 0, status: 'geplant' },
]

export default function ErnteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'schlag' as const,
      label: 'Schlag',
      render: (e: Ernte) => (
        <button onClick={() => navigate(`/agrar/ernte/${e.id}`)} className="font-medium text-blue-600 hover:underline">
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

  const gesamtMenge = mockErnten.reduce((sum, e) => sum + e.menge, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Ernte-Übersicht</h1>
          <p className="text-muted-foreground">Erntesaison 2025</p>
        </div>
        <Button onClick={() => navigate('/agrar/ernte/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Ernte
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockErnten.length}</span>
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
            <span className="text-2xl font-bold text-green-600">{mockErnten.filter((e) => e.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockErnten.filter((e) => e.status === 'geplant').length}</span>
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
          <DataTable data={mockErnten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
