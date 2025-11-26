import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, FileDown, Search } from 'lucide-react'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

type Verbindlichkeit = {
  id: string
  rechnungsNr: string
  lieferant: string
  rechnungsDatum: string
  faelligAm: string
  betrag: number
  offen: number
  status: 'offen' | 'teilbezahlt' | 'bezahlt' | 'skontofähig'
}

const mockVerbindlichkeiten: Verbindlichkeit[] = [
  {
    id: '1',
    rechnungsNr: 'ER-2025-0001',
    lieferant: 'Saatgut AG',
    rechnungsDatum: '2025-10-08',
    faelligAm: '2025-11-07',
    betrag: 25000.0,
    offen: 25000.0,
    status: 'skontofähig',
  },
  {
    id: '2',
    rechnungsNr: 'ER-2025-0002',
    lieferant: 'Dünger GmbH',
    rechnungsDatum: '2025-10-09',
    faelligAm: '2025-11-08',
    betrag: 18500.5,
    offen: 9250.25,
    status: 'teilbezahlt',
  },
  {
    id: '3',
    rechnungsNr: 'ER-2025-0003',
    lieferant: 'Agrar-Handel Nord',
    rechnungsDatum: '2025-10-10',
    faelligAm: '2025-11-09',
    betrag: 12200.0,
    offen: 12200.0,
    status: 'offen',
  },
]

const statusVariantMap: Record<Verbindlichkeit['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  teilbezahlt: 'secondary',
  bezahlt: 'outline',
  skontofähig: 'default',
}

export default function VerbindlichkeitenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Verbindlichkeit['status'] | 'alle'>('alle')

  const filteredVerbindlichkeiten = mockVerbindlichkeiten.filter((verb) => {
    const matchesSearch =
      verb.rechnungsNr.toLowerCase().includes(searchTerm.toLowerCase()) ||
      verb.lieferant.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || verb.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const gesamtOffen = filteredVerbindlichkeiten.reduce((sum, v) => sum + v.offen, 0)
  const skontofähig = filteredVerbindlichkeiten.filter((v) => v.status === 'skontofähig')

  const columns = [
    {
      key: 'rechnungsNr' as const,
      label: 'Rechnung',
      render: (verb: Verbindlichkeit) => (
        <button
          onClick={() => navigate(`/fibu/verbindlichkeit/${verb.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {verb.rechnungsNr}
        </button>
      ),
    },
    {
      key: 'lieferant' as const,
      label: 'Lieferant',
    },
    {
      key: 'rechnungsDatum' as const,
      label: 'Rechnungsdatum',
      render: (verb: Verbindlichkeit) => new Date(verb.rechnungsDatum).toLocaleDateString('de-DE'),
    },
    {
      key: 'faelligAm' as const,
      label: 'Fällig am',
      render: (verb: Verbindlichkeit) => new Date(verb.faelligAm).toLocaleDateString('de-DE'),
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (verb: Verbindlichkeit) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(verb.betrag),
    },
    {
      key: 'offen' as const,
      label: 'Offener Betrag',
      render: (verb: Verbindlichkeit) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(verb.offen)}
        </span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (verb: Verbindlichkeit) => (
        <Badge variant={statusVariantMap[verb.status]}>{getStatusLabel(t, verb.status, verb.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Verbindlichkeiten</h1>
          <p className="text-muted-foreground">Übersicht aller offenen Lieferantenrechnungen</p>
        </div>
        <Button variant="outline">Zahlungslauf planen</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtOffen)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Skontofähig</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{skontofähig.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Skontovolumen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                skontofähig.reduce((sum, v) => sum + v.offen, 0) * 0.02
              )}
            </div>
          </CardContent>
        </Card>
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
                placeholder="Suche nach Rechnung oder Lieferant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Verbindlichkeit['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="offen">Offen</option>
              <option value="teilbezahlt">Teilbezahlt</option>
              <option value="bezahlt">Bezahlt</option>
              <option value="skontofähig">Skontofähig</option>
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
          <DataTable data={filteredVerbindlichkeiten} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredVerbindlichkeiten.length} von {mockVerbindlichkeiten.length} Verbindlichkeit(en) angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
