import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Plus, Search } from 'lucide-react'

type Angebot = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: 'offen' | 'angenommen' | 'abgelehnt' | 'abgelaufen'
  gueltigBis: string
}

const mockAngebote: Angebot[] = [
  {
    id: '1',
    nummer: 'ANG-2025-001',
    datum: '2025-10-08',
    kunde: 'Landhandel Nord GmbH',
    betrag: 12500.0,
    status: 'offen',
    gueltigBis: '2025-11-07',
  },
  {
    id: '2',
    nummer: 'ANG-2025-002',
    datum: '2025-10-09',
    kunde: 'Agrar-Zentrum Süd',
    betrag: 8750.5,
    status: 'angenommen',
    gueltigBis: '2025-11-08',
  },
  {
    id: '3',
    nummer: 'ANG-2025-003',
    datum: '2025-10-10',
    kunde: 'Müller Landwirtschaft',
    betrag: 5200.0,
    status: 'offen',
    gueltigBis: '2025-11-09',
  },
]

const statusVariantMap: Record<Angebot['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  angenommen: 'outline',
  abgelehnt: 'destructive',
  abgelaufen: 'secondary',
}

const statusLabelMap: Record<Angebot['status'], string> = {
  offen: 'Offen',
  angenommen: 'Angenommen',
  abgelehnt: 'Abgelehnt',
  abgelaufen: 'Abgelaufen',
}

export default function AngeboteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Angebot['status'] | 'alle'>('alle')

  const filteredAngebote = mockAngebote.filter((angebot) => {
    const matchesSearch =
      angebot.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      angebot.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || angebot.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Angebotsnummer',
      render: (angebot: Angebot) => (
        <button
          onClick={() => navigate(`/sales/angebot/${angebot.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {angebot.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (angebot: Angebot) => new Date(angebot.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (angebot: Angebot) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(angebot.betrag),
    },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (angebot: Angebot) => new Date(angebot.gueltigBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (angebot: Angebot) => (
        <Badge variant={statusVariantMap[angebot.status]}>{statusLabelMap[angebot.status]}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Angebote</h1>
          <p className="text-muted-foreground">Übersicht aller Verkaufsangebote</p>
        </div>
        <Button onClick={() => navigate('/sales/angebot/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Angebot
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
              onChange={(e) => setStatusFilter(e.target.value as Angebot['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="offen">Offen</option>
              <option value="angenommen">Angenommen</option>
              <option value="abgelehnt">Abgelehnt</option>
              <option value="abgelaufen">Abgelaufen</option>
            </select>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" className="gap-2">
              <FileText className="h-4 w-4" />
              Drucken
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredAngebote} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredAngebote.length} von {mockAngebote.length} Angebote(n) angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
