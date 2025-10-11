import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, CheckCircle, Search, Upload, XCircle } from 'lucide-react'

type Zahlungseingang = {
  id: string
  datum: string
  betrag: number
  verwendungszweck: string
  kontoinhaber: string
  status: 'zugeordnet' | 'offen' | 'differenz' | 'fehler'
  rechnungsNr?: string
  differenz?: number
}

const mockZahlungseingaenge: Zahlungseingang[] = [
  {
    id: '1',
    datum: '2025-10-11',
    betrag: 8750.5,
    verwendungszweck: 'RE-2025-0002 Rechnung Oktober',
    kontoinhaber: 'Agrar-Zentrum Süd',
    status: 'zugeordnet',
    rechnungsNr: 'RE-2025-0002',
  },
  {
    id: '2',
    datum: '2025-10-11',
    betrag: 12450.0,
    verwendungszweck: 'Rechnung SO-2025-0001',
    kontoinhaber: 'Landhandel Nord GmbH',
    status: 'differenz',
    rechnungsNr: 'RE-2025-0001',
    differenz: -50.0,
  },
  {
    id: '3',
    datum: '2025-10-10',
    betrag: 2500.0,
    verwendungszweck: 'Überweisung',
    kontoinhaber: 'Max Mustermann',
    status: 'offen',
  },
  {
    id: '4',
    datum: '2025-10-10',
    betrag: 15600.0,
    verwendungszweck: 'RE-2025-0010',
    kontoinhaber: 'Agrar-Genossenschaft West',
    status: 'zugeordnet',
    rechnungsNr: 'RE-2025-0010',
  },
]

const statusVariantMap: Record<
  Zahlungseingang['status'],
  'default' | 'outline' | 'secondary' | 'destructive'
> = {
  zugeordnet: 'outline',
  offen: 'default',
  differenz: 'secondary',
  fehler: 'destructive',
}

const statusLabelMap: Record<Zahlungseingang['status'], string> = {
  zugeordnet: 'Zugeordnet',
  offen: 'Offen',
  differenz: 'Differenz',
  fehler: 'Fehler',
}

const statusIconMap: Record<Zahlungseingang['status'], JSX.Element> = {
  zugeordnet: <CheckCircle className="h-4 w-4 text-green-600" />,
  offen: <AlertTriangle className="h-4 w-4 text-orange-600" />,
  differenz: <AlertTriangle className="h-4 w-4 text-yellow-600" />,
  fehler: <XCircle className="h-4 w-4 text-red-600" />,
}

export default function ZahlungseingangsPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Zahlungseingang['status'] | 'alle'>('alle')

  const filteredZahlungen = mockZahlungseingaenge.filter((zahlung) => {
    const matchesSearch =
      zahlung.verwendungszweck.toLowerCase().includes(searchTerm.toLowerCase()) ||
      zahlung.kontoinhaber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (zahlung.rechnungsNr && zahlung.rechnungsNr.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesStatus = statusFilter === 'alle' || zahlung.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const offeneZahlungen = mockZahlungseingaenge.filter((z) => z.status === 'offen').length
  const gesamtBetrag = filteredZahlungen.reduce((sum, z) => sum + z.betrag, 0)

  const columns = [
    {
      key: 'status' as const,
      label: '',
      render: (zahlung: Zahlungseingang) => statusIconMap[zahlung.status],
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (zahlung: Zahlungseingang) => new Date(zahlung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kontoinhaber' as const,
      label: 'Kontoinhaber',
      render: (zahlung: Zahlungseingang) => (
        <div>
          <div className="font-medium">{zahlung.kontoinhaber}</div>
          <div className="text-sm text-muted-foreground">{zahlung.verwendungszweck}</div>
        </div>
      ),
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (zahlung: Zahlungseingang) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(zahlung.betrag)}
        </span>
      ),
    },
    {
      key: 'rechnungsNr' as const,
      label: 'Rechnung',
      render: (zahlung: Zahlungseingang) =>
        zahlung.rechnungsNr ? (
          <span className="text-sm text-blue-600">{zahlung.rechnungsNr}</span>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'differenz' as const,
      label: 'Differenz',
      render: (zahlung: Zahlungseingang) =>
        zahlung.differenz ? (
          <span className="font-medium text-orange-600">
            {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
              zahlung.differenz
            )}
          </span>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'statusBadge' as const,
      label: 'Status',
      render: (zahlung: Zahlungseingang) => (
        <Badge variant={statusVariantMap[zahlung.status]}>{statusLabelMap[zahlung.status]}</Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (zahlung: Zahlungseingang) => (
        <div className="flex gap-2">
          {zahlung.status === 'offen' && (
            <Button size="sm" variant="outline">
              Zuordnen
            </Button>
          )}
          {zahlung.status === 'differenz' && (
            <Button size="sm" variant="outline">
              Klären
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Zahlungseingänge</h1>
          <p className="text-muted-foreground">Bank-Import & Auto-Matching</p>
        </div>
        <Button className="gap-2">
          <Upload className="h-4 w-4" />
          Bank-Import
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Zuordnungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{offeneZahlungen}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt (gefiltert)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auto-Match-Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">75%</span>
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
                placeholder="Suche nach Verwendungszweck, Kontoinhaber oder Rechnung..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Zahlungseingang['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="zugeordnet">Zugeordnet</option>
              <option value="offen">Offen</option>
              <option value="differenz">Differenz</option>
              <option value="fehler">Fehler</option>
            </select>
            <Button variant="outline">Auto-Match starten</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredZahlungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredZahlungen.length} von {mockZahlungseingaenge.length} Zahlung(en) angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
