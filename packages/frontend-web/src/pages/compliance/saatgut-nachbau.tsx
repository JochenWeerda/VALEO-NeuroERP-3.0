import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type SaatgutNachbau = {
  id: string
  betrieb: string
  sorte: string
  kultur: string
  flaeche: number
  erntejahr: number
  gebuehr: number
  status: 'erfasst' | 'gemeldet' | 'bezahlt'
}

const mockNachbau: SaatgutNachbau[] = [
  { id: '1', betrieb: 'Landwirtschaft Müller', sorte: 'Weichweizen Eltan', kultur: 'Weichweizen', flaeche: 45.5, erntejahr: 2024, gebuehr: 682.5, status: 'bezahlt' },
  { id: '2', betrieb: 'Hofgut Weber', sorte: 'Wintergerste KWS Orbit', kultur: 'Wintergerste', flaeche: 32.0, erntejahr: 2024, gebuehr: 480.0, status: 'gemeldet' },
  { id: '3', betrieb: 'Agrar Schmidt GmbH', sorte: 'Winterraps Mentor', kultur: 'Winterraps', flaeche: 28.3, erntejahr: 2024, gebuehr: 424.5, status: 'erfasst' },
]

export default function SaatgutNachbauPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'betrieb' as const,
      label: 'Betrieb',
      render: (n: SaatgutNachbau) => (
        <button onClick={() => navigate(`/crm/betrieb/${n.id}`)} className="font-medium text-blue-600 hover:underline">
          {n.betrieb}
        </button>
      ),
    },
    { key: 'sorte' as const, label: 'Sorte' },
    { key: 'kultur' as const, label: 'Kultur', render: (n: SaatgutNachbau) => <Badge variant="outline">{n.kultur}</Badge> },
    {
      key: 'flaeche' as const,
      label: 'Fläche (ha)',
      render: (n: SaatgutNachbau) => <span className="font-mono">{n.flaeche.toLocaleString('de-DE', { minimumFractionDigits: 1 })}</span>,
    },
    { key: 'erntejahr' as const, label: 'Erntejahr' },
    {
      key: 'gebuehr' as const,
      label: 'Nachbaugebühr',
      render: (n: SaatgutNachbau) => (
        <span className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n.gebuehr)}</span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (n: SaatgutNachbau) => (
        <Badge variant={n.status === 'bezahlt' ? 'outline' : n.status === 'gemeldet' ? 'secondary' : 'default'}>
          {n.status === 'bezahlt' ? 'Bezahlt' : n.status === 'gemeldet' ? 'Gemeldet' : 'Erfasst'}
        </Badge>
      ),
    },
  ]

  const gesamtFlaeche = mockNachbau.reduce((sum, n) => sum + n.flaeche, 0)
  const gesamtGebuehr = mockNachbau.reduce((sum, n) => sum + n.gebuehr, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Saatgut-Nachbau Meldungen</h1>
          <p className="text-muted-foreground">Saatgut-Treuhandverwaltung (STV)</p>
        </div>
        <Button onClick={() => navigate('/compliance/saatgut-nachbau-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Nachbau erfassen
        </Button>
      </div>

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">🌾 Saatgut-Treuhand (STV)</p>
        <p className="mt-1">
          Nachbaugebühr bei Eigennachbau geschützter Sorten • Meldung an STV bis 30.06. • Berechnung: Fläche × Sorte × Gebührensatz
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Meldungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockNachbau.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fläche Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtFlaeche.toLocaleString('de-DE', { minimumFractionDigits: 1 })} ha</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gebühr Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtGebuehr)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bezahlt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockNachbau.filter((n) => n.status === 'bezahlt').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Betrieb oder Sorte..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              STV-Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockNachbau} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
