import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Package, Plus, Search } from 'lucide-react'

type Artikel = {
  id: string
  artikelnr: string
  bezeichnung: string
  warengruppe: string
  vkPreis: number
  bestand: number
  status: 'aktiv' | 'auslaufend'
}

const mockArtikel: Artikel[] = [
  { id: '1', artikelnr: '10001', bezeichnung: 'Weizen Premium', warengruppe: 'Getreide', vkPreis: 220.5, bestand: 450, status: 'aktiv' },
  { id: '2', artikelnr: '20005', bezeichnung: 'Sojaschrot 44%', warengruppe: 'Futtermittel', vkPreis: 520.0, bestand: 280, status: 'aktiv' },
  { id: '3', artikelnr: '30012', bezeichnung: 'NPK-Dünger 15-15-15', warengruppe: 'Düngemittel', vkPreis: 380.0, bestand: 220, status: 'aktiv' },
]

export default function ArtikelListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'artikelnr' as const,
      label: 'Artikelnr.',
      render: (a: Artikel) => <span className="font-mono">{a.artikelnr}</span>,
    },
    {
      key: 'bezeichnung' as const,
      label: 'Bezeichnung',
      render: (a: Artikel) => (
        <button onClick={() => navigate(`/artikel/${a.id}`)} className="font-medium text-blue-600 hover:underline">
          {a.bezeichnung}
        </button>
      ),
    },
    { key: 'warengruppe' as const, label: 'Warengruppe', render: (a: Artikel) => <Badge variant="outline">{a.warengruppe}</Badge> },
    {
      key: 'vkPreis' as const,
      label: 'VK-Preis',
      render: (a: Artikel) => `${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(a.vkPreis)} / t`,
    },
    { key: 'bestand' as const, label: 'Bestand (t)', render: (a: Artikel) => `${a.bestand} t` },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Artikel) => (
        <Badge variant={a.status === 'aktiv' ? 'outline' : 'secondary'}>
          {a.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Artikel</h1>
          <p className="text-muted-foreground">Artikelstamm</p>
        </div>
        <Button onClick={() => navigate('/artikel/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Artikel
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockArtikel.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockArtikel.filter((a) => a.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lagerwert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(220000)}
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
          <DataTable data={mockArtikel} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
