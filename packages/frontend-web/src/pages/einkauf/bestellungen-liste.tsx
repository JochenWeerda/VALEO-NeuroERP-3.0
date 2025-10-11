import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, Plus, Search } from 'lucide-react'

type Bestellung = {
  id: string
  nummer: string
  datum: string
  lieferant: string
  betrag: number
  liefertermin: string
  status: 'offen' | 'bestaetigt' | 'teilgeliefert' | 'geliefert' | 'storniert'
}

const mockBestellungen: Bestellung[] = [
  {
    id: '1',
    nummer: 'PO-2025-0001',
    datum: '2025-10-08',
    lieferant: 'Saatgut AG',
    betrag: 25000.0,
    liefertermin: '2025-10-20',
    status: 'bestaetigt',
  },
  {
    id: '2',
    nummer: 'PO-2025-0002',
    datum: '2025-10-09',
    lieferant: 'Dünger GmbH',
    betrag: 18500.5,
    liefertermin: '2025-10-15',
    status: 'teilgeliefert',
  },
  {
    id: '3',
    nummer: 'PO-2025-0003',
    datum: '2025-10-10',
    lieferant: 'Agrar-Handel Nord',
    betrag: 12200.0,
    liefertermin: '2025-10-25',
    status: 'offen',
  },
]

const statusVariantMap: Record<Bestellung['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  bestaetigt: 'secondary',
  teilgeliefert: 'secondary',
  geliefert: 'outline',
  storniert: 'destructive',
}

const statusLabelMap: Record<Bestellung['status'], string> = {
  offen: 'Offen',
  bestaetigt: 'Bestätigt',
  teilgeliefert: 'Teilgeliefert',
  geliefert: 'Geliefert',
  storniert: 'Storniert',
}

export default function BestellungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Bestellung['status'] | 'alle'>('alle')

  const filteredBestellungen = mockBestellungen.filter((bestellung) => {
    const matchesSearch =
      bestellung.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bestellung.lieferant.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || bestellung.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Bestellnummer',
      render: (bestellung: Bestellung) => (
        <button
          onClick={() => navigate(`/einkauf/bestellung/${bestellung.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {bestellung.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Bestelldatum',
      render: (bestellung: Bestellung) => new Date(bestellung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'lieferant' as const,
      label: 'Lieferant',
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (bestellung: Bestellung) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(bestellung.betrag),
    },
    {
      key: 'liefertermin' as const,
      label: 'Liefertermin',
      render: (bestellung: Bestellung) => new Date(bestellung.liefertermin).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (bestellung: Bestellung) => (
        <Badge variant={statusVariantMap[bestellung.status]}>{statusLabelMap[bestellung.status]}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bestellungen</h1>
          <p className="text-muted-foreground">Übersicht aller Einkaufsbestellungen</p>
        </div>
        <Button onClick={() => navigate('/einkauf/bestellung-anlegen')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Bestellung
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter & Suche</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Nummer oder Lieferant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Bestellung['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="offen">Offen</option>
              <option value="bestaetigt">Bestätigt</option>
              <option value="teilgeliefert">Teilgeliefert</option>
              <option value="geliefert">Geliefert</option>
              <option value="storniert">Storniert</option>
            </select>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredBestellungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredBestellungen.length} von {mockBestellungen.length} Bestellung(en) angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
