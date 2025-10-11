import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Layers, Plus, Search } from 'lucide-react'

type Warengruppe = {
  id: string
  name: string
  kategorie: string
  artikel: number
  umsatz: number
}

const mockWarengruppen: Warengruppe[] = [
  { id: '1', name: 'Getreide', kategorie: 'Agrar', artikel: 15, umsatz: 450000 },
  { id: '2', name: 'Saatgut', kategorie: 'Agrar', artikel: 25, umsatz: 280000 },
  { id: '3', name: 'Düngemittel', kategorie: 'Betriebsmittel', artikel: 18, umsatz: 320000 },
  { id: '4', name: 'Futtermittel', kategorie: 'Futter', artikel: 32, umsatz: 380000 },
]

export default function WarengruppenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Warengruppe',
      render: (w: Warengruppe) => (
        <button onClick={() => navigate(`/einkauf/warengruppe/${w.id}`)} className="font-medium text-blue-600 hover:underline">
          {w.name}
        </button>
      ),
    },
    { key: 'kategorie' as const, label: 'Kategorie', render: (w: Warengruppe) => <Badge variant="outline">{w.kategorie}</Badge> },
    { key: 'artikel' as const, label: 'Artikel', render: (w: Warengruppe) => `${w.artikel} Artikel` },
    {
      key: 'umsatz' as const,
      label: 'Jahresumsatz',
      render: (w: Warengruppe) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(w.umsatz),
    },
  ]

  const gesamtUmsatz = mockWarengruppen.reduce((sum, w) => sum + w.umsatz, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Warengruppen</h1>
          <p className="text-muted-foreground">Sortimentsverwaltung</p>
        </div>
        <Button onClick={() => navigate('/einkauf/warengruppe/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Warengruppe
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Warengruppen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockWarengruppen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockWarengruppen.reduce((sum, w) => sum + w.artikel, 0)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Jahresumsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtUmsatz)}
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
          <DataTable data={mockWarengruppen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
