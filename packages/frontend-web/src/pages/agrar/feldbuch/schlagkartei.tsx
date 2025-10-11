import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, MapPin, Plus, Search } from 'lucide-react'

type Schlag = {
  id: string
  name: string
  flaeche: number
  kultur: string
  landwirt: string
  gemeinde: string
}

const mockSchlaege: Schlag[] = [
  { id: '1', name: 'Nordfeld 1', flaeche: 12.5, kultur: 'Weizen', landwirt: 'Schmidt', gemeinde: 'Nordhausen' },
  { id: '2', name: 'Südacker', flaeche: 8.3, kultur: 'Raps', landwirt: 'Müller', gemeinde: 'Südhausen' },
  { id: '3', name: 'Wiesengrund', flaeche: 15.2, kultur: 'Mais', landwirt: 'Schmidt', gemeinde: 'Nordhausen' },
]

export default function SchlagkarteiPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Schlag',
      render: (s: Schlag) => (
        <button onClick={() => navigate(`/agrar/feldbuch/schlag/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.name}
        </button>
      ),
    },
    { key: 'flaeche' as const, label: 'Fläche (ha)', render: (s: Schlag) => `${s.flaeche} ha` },
    { key: 'kultur' as const, label: 'Kultur', render: (s: Schlag) => <Badge variant="outline">{s.kultur}</Badge> },
    { key: 'landwirt' as const, label: 'Landwirt' },
    { key: 'gemeinde' as const, label: 'Gemeinde' },
  ]

  const gesamtflaeche = mockSchlaege.reduce((sum, s) => sum + s.flaeche, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schlagkartei</h1>
          <p className="text-muted-foreground">Anbauflächen</p>
        </div>
        <Button onClick={() => navigate('/agrar/feldbuch/schlag/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Schlag
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockSchlaege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtfläche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtflaeche.toFixed(1)} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Landwirte</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Set(mockSchlaege.map((s) => s.landwirt)).size}</span>
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
          <DataTable data={mockSchlaege} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
