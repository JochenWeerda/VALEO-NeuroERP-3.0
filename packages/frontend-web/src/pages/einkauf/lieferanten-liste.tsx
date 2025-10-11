import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Building2, FileDown, Plus, Search } from 'lucide-react'

type Lieferant = {
  id: string
  name: string
  typ: string
  ort: string
  bewertung: number
  status: 'aktiv' | 'gesperrt'
}

const mockLieferanten: Lieferant[] = [
  { id: '1', name: 'Saatgut AG', typ: 'Saatgut', ort: 'Südhausen', bewertung: 4.5, status: 'aktiv' },
  { id: '2', name: 'Dünger GmbH', typ: 'Düngemittel', ort: 'Nordhausen', bewertung: 4.2, status: 'aktiv' },
  { id: '3', name: 'Technik GmbH', typ: 'Landtechnik', ort: 'Osthausen', bewertung: 3.8, status: 'aktiv' },
]

export default function LieferantenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Lieferant',
      render: (l: Lieferant) => (
        <button onClick={() => navigate(`/einkauf/lieferant/${l.id}`)} className="font-medium text-blue-600 hover:underline">
          {l.name}
        </button>
      ),
    },
    { key: 'typ' as const, label: 'Typ', render: (l: Lieferant) => <Badge variant="outline">{l.typ}</Badge> },
    { key: 'ort' as const, label: 'Ort' },
    {
      key: 'bewertung' as const,
      label: 'Bewertung',
      render: (l: Lieferant) => (
        <div className="flex items-center gap-1">
          <span className="font-bold">{l.bewertung}</span>
          <span className="text-sm text-muted-foreground">/ 5</span>
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: Lieferant) => (
        <Badge variant={l.status === 'aktiv' ? 'outline' : 'destructive'}>
          {l.status === 'aktiv' ? 'Aktiv' : 'Gesperrt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Lieferanten</h1>
          <p className="text-muted-foreground">Lieferantenverwaltung</p>
        </div>
        <Button onClick={() => navigate('/einkauf/lieferant/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Lieferant
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferanten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockLieferanten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockLieferanten.filter((l) => l.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Bewertung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {(mockLieferanten.reduce((sum, l) => sum + l.bewertung, 0) / mockLieferanten.length).toFixed(1)} / 5
            </span>
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
          <DataTable data={mockLieferanten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
