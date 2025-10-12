import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Percent, Plus, Search } from 'lucide-react'

type Rabatt = {
  id: string
  name: string
  typ: 'prozent' | 'absolut' | 'mengenrabatt'
  wert: number
  bedingung: string
  gueltigVon: string
  gueltigBis: string
  kundengruppe?: string
  artikel?: string
  minBestellwert?: number
  status: 'aktiv' | 'inaktiv' | 'abgelaufen'
}

const mockRabatte: Rabatt[] = [
  {
    id: '1',
    name: 'Herbst-Aktion 2025',
    typ: 'prozent',
    wert: 15,
    bedingung: 'Alle Saatgut-Artikel',
    gueltigVon: '2025-10-01',
    gueltigBis: '2025-10-31',
    status: 'aktiv',
  },
  {
    id: '2',
    name: 'Treue-Rabatt Gold',
    typ: 'prozent',
    wert: 10,
    bedingung: 'Kundengruppe: Gold',
    gueltigVon: '2025-01-01',
    gueltigBis: '2025-12-31',
    kundengruppe: 'Gold',
    status: 'aktiv',
  },
  {
    id: '3',
    name: 'Mengenrabatt Dünger',
    typ: 'mengenrabatt',
    wert: 20,
    bedingung: 'Ab 10 Sack',
    gueltigVon: '2025-01-01',
    gueltigBis: '2025-12-31',
    artikel: 'Dünger',
    status: 'aktiv',
  },
  {
    id: '4',
    name: 'Sommer-Aktion',
    typ: 'absolut',
    wert: 5,
    bedingung: 'Ab 50 € Bestellwert',
    gueltigVon: '2025-06-01',
    gueltigBis: '2025-08-31',
    minBestellwert: 50,
    status: 'abgelaufen',
  },
]

export default function RabattePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Rabatt-Name',
      render: (r: Rabatt) => (
        <button onClick={() => navigate(`/pos/rabatt/${r.id}`)} className="font-medium text-blue-600 hover:underline">
          {r.name}
        </button>
      ),
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (r: Rabatt) => (
        <Badge variant="outline">
          {r.typ === 'prozent' ? 'Prozent' : r.typ === 'absolut' ? 'Absolut' : 'Mengenrabatt'}
        </Badge>
      ),
    },
    {
      key: 'wert' as const,
      label: 'Wert',
      render: (r: Rabatt) => (
        <span className="font-bold text-lg">
          {r.typ === 'prozent' ? `${r.wert}%` : r.typ === 'absolut' ? `${r.wert} €` : `${r.wert}%`}
        </span>
      ),
    },
    { key: 'bedingung' as const, label: 'Bedingung' },
    {
      key: 'gueltigVon' as const,
      label: 'Gültig von',
      render: (r: Rabatt) => new Date(r.gueltigVon).toLocaleDateString('de-DE'),
    },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (r: Rabatt) => {
        const ablauf = new Date(r.gueltigBis)
        const abgelaufen = ablauf < new Date()
        return (
          <span className={abgelaufen ? 'text-muted-foreground line-through' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (r: Rabatt) => (
        <Badge variant={r.status === 'aktiv' ? 'outline' : r.status === 'inaktiv' ? 'secondary' : 'default'}>
          {r.status === 'aktiv' ? 'Aktiv' : r.status === 'inaktiv' ? 'Inaktiv' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  const aktiv = mockRabatte.filter((r) => r.status === 'aktiv').length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Percent className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Rabatte & Aktionen</h1>
            <p className="text-muted-foreground">Automatische Rabatte im POS-System</p>
          </div>
        </div>
        <Button onClick={() => navigate('/pos/rabatt-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Rabatt
        </Button>
      </div>

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <div className="flex items-center gap-2">
          <Percent className="h-4 w-4" />
          <p className="font-semibold">Automatische Rabatt-Anwendung</p>
        </div>
        <p className="mt-1">
          <strong>Prozent:</strong> 15% auf Saatgut • <strong>Absolut:</strong> 5 € ab 50 € • 
          <strong>Mengenrabatt:</strong> 20% ab 10 Stück • <strong>Kundengruppe:</strong> Gold 10%
        </p>
        <p className="mt-1 text-xs">Rabatte werden im POS automatisch angewendet wenn Bedingungen erfüllt sind</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rabatte Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockRabatte.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{aktiv}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgelaufen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-gray-400">{mockRabatte.filter((r) => r.status === 'abgelaufen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rabatt-Typen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Set(mockRabatte.map((r) => r.typ)).size}</span>
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
              <Input placeholder="Suche Rabatt-Name..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline">Nur Aktive</Button>
            <Button variant="outline">Nur Prozent-Rabatte</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockRabatte} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
