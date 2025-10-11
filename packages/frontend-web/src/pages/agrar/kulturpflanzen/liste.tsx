import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Sprout } from 'lucide-react'

type Kultur = {
  id: string
  name: string
  kategorie: string
  flaeche: number
  ertrag: number
  preis: number
  deckungsbeitrag: number
}

const mockKulturen: Kultur[] = [
  { id: '1', name: 'Weizen (Winterweizen)', kategorie: 'Getreide', flaeche: 65.5, ertrag: 7.8, preis: 220, deckungsbeitrag: 850 },
  { id: '2', name: 'Raps (Winterraps)', kategorie: 'Ölsaaten', flaeche: 28.0, ertrag: 4.2, preis: 450, deckungsbeitrag: 720 },
  { id: '3', name: 'Mais (Körnermais)', kategorie: 'Getreide', flaeche: 32.0, ertrag: 9.5, preis: 190, deckungsbeitrag: 680 },
]

export default function KulturpflanzenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Kulturpflanze',
      render: (k: Kultur) => (
        <button onClick={() => navigate(`/agrar/kulturpflanzen/${k.id}`)} className="font-medium text-blue-600 hover:underline">
          {k.name}
        </button>
      ),
    },
    { key: 'kategorie' as const, label: 'Kategorie', render: (k: Kultur) => <Badge variant="outline">{k.kategorie}</Badge> },
    { key: 'flaeche' as const, label: 'Fläche (ha)', render: (k: Kultur) => `${k.flaeche} ha` },
    { key: 'ertrag' as const, label: 'Ertrag (t/ha)', render: (k: Kultur) => `${k.ertrag} t/ha` },
    {
      key: 'preis' as const,
      label: 'Preis (€/t)',
      render: (k: Kultur) => `${new Intl.NumberFormat('de-DE').format(k.preis)} €`,
    },
    {
      key: 'deckungsbeitrag' as const,
      label: 'DB (€/ha)',
      render: (k: Kultur) => <span className="font-bold">{new Intl.NumberFormat('de-DE').format(k.deckungsbeitrag)} €</span>,
    },
  ]

  const gesamtFlaeche = mockKulturen.reduce((sum, k) => sum + k.flaeche, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kulturpflanzen</h1>
          <p className="text-muted-foreground">Anbau-Übersicht & Deckungsbeiträge</p>
        </div>
        <Button onClick={() => navigate('/agrar/kulturpflanzen/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Kultur
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kulturen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{mockKulturen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Fläche</CardTitle>
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
            <span className="text-2xl font-bold text-green-600">
              {(mockKulturen.reduce((sum, k) => sum + k.deckungsbeitrag, 0) / mockKulturen.length).toFixed(0)} € / ha
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
          <DataTable data={mockKulturen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
