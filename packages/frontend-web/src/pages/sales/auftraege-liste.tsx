import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, Plus, Search } from 'lucide-react'

type Auftrag = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: 'offen' | 'teilgeliefert' | 'geliefert' | 'fakturiert' | 'storniert'
  liefertermin: string
}

const mockAuftraege: Auftrag[] = [
  {
    id: '1',
    nummer: 'SO-2025-0001',
    datum: '2025-10-08',
    kunde: 'Landhandel Nord GmbH',
    betrag: 12500.0,
    status: 'teilgeliefert',
    liefertermin: '2025-10-15',
  },
  {
    id: '2',
    nummer: 'SO-2025-0002',
    datum: '2025-10-09',
    kunde: 'Agrar-Zentrum Süd',
    betrag: 8750.5,
    status: 'geliefert',
    liefertermin: '2025-10-12',
  },
  {
    id: '3',
    nummer: 'SO-2025-0003',
    datum: '2025-10-10',
    kunde: 'Müller Landwirtschaft',
    betrag: 5200.0,
    status: 'offen',
    liefertermin: '2025-10-20',
  },
]

const statusVariantMap: Record<Auftrag['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  teilgeliefert: 'secondary',
  geliefert: 'outline',
  fakturiert: 'outline',
  storniert: 'destructive',
}

const statusLabelMap: Record<Auftrag['status'], string> = {
  offen: 'Offen',
  teilgeliefert: 'Teilgeliefert',
  geliefert: 'Geliefert',
  fakturiert: 'Fakturiert',
  storniert: 'Storniert',
}

export default function AuftraegeListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Auftrag['status'] | 'alle'>('alle')

  const filteredAuftraege = mockAuftraege.filter((auftrag) => {
    const matchesSearch =
      auftrag.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      auftrag.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || auftrag.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Auftragsnummer',
      render: (auftrag: Auftrag) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${auftrag.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {auftrag.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Auftragsdatum',
      render: (auftrag: Auftrag) => new Date(auftrag.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (auftrag: Auftrag) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(auftrag.betrag),
    },
    {
      key: 'liefertermin' as const,
      label: 'Liefertermin',
      render: (auftrag: Auftrag) => new Date(auftrag.liefertermin).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (auftrag: Auftrag) => (
        <Badge variant={statusVariantMap[auftrag.status]}>{statusLabelMap[auftrag.status]}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Aufträge</h1>
          <p className="text-muted-foreground">Übersicht aller Verkaufsaufträge</p>
        </div>
        <Button onClick={() => navigate('/sales/order-editor')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Auftrag
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
                placeholder="Suche nach Nummer oder Kunde..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Auftrag['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="offen">Offen</option>
              <option value="teilgeliefert">Teilgeliefert</option>
              <option value="geliefert">Geliefert</option>
              <option value="fakturiert">Fakturiert</option>
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
          <DataTable data={filteredAuftraege} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredAuftraege.length} von {mockAuftraege.length} Auftrag/Aufträge angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
