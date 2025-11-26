import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Euro, FileDown, Search } from 'lucide-react'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

type OffenerPosten = {
  id: string
  rechnungsNr: string
  kunde: string
  rechnungsDatum: string
  faelligAm: string
  betrag: number
  offen: number
  tageUeberfaellig: number
  mahnstufe: 0 | 1 | 2 | 3
  status: 'faellig' | 'ueberfaellig' | 'mahnung1' | 'mahnung2' | 'mahnung3' | 'inkasso'
}

const mockOffenePosten: OffenerPosten[] = [
  {
    id: '1',
    rechnungsNr: 'RE-2025-0001',
    kunde: 'Landhandel Nord GmbH',
    rechnungsDatum: '2025-10-11',
    faelligAm: '2025-11-10',
    betrag: 12500.0,
    offen: 12500.0,
    tageUeberfaellig: 0,
    mahnstufe: 0,
    status: 'faellig',
  },
  {
    id: '2',
    rechnungsNr: 'RE-2025-0003',
    kunde: 'Müller Landwirtschaft',
    rechnungsDatum: '2025-09-15',
    faelligAm: '2025-10-15',
    betrag: 5200.0,
    offen: 5200.0,
    tageUeberfaellig: 26,
    mahnstufe: 2,
    status: 'mahnung2',
  },
  {
    id: '3',
    rechnungsNr: 'RE-2024-0890',
    kunde: 'Schmidt Agrar KG',
    rechnungsDatum: '2024-08-20',
    faelligAm: '2024-09-19',
    betrag: 8900.0,
    offen: 8900.0,
    tageUeberfaellig: 52,
    mahnstufe: 3,
    status: 'inkasso',
  },
  {
    id: '4',
    rechnungsNr: 'RE-2025-0010',
    kunde: 'Agrar-Genossenschaft West',
    rechnungsDatum: '2025-10-01',
    faelligAm: '2025-10-31',
    betrag: 15600.0,
    offen: 15600.0,
    tageUeberfaellig: 0,
    mahnstufe: 0,
    status: 'faellig',
  },
]

const statusVariantMap: Record<
  OffenerPosten['status'],
  'default' | 'outline' | 'secondary' | 'destructive'
> = {
  faellig: 'default',
  ueberfaellig: 'secondary',
  mahnung1: 'secondary',
  mahnung2: 'destructive',
  mahnung3: 'destructive',
  inkasso: 'destructive',
}


export default function OffenePostenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<OffenerPosten['status'] | 'alle'>('alle')

  const filteredPosten = mockOffenePosten.filter((posten) => {
    const matchesSearch =
      posten.rechnungsNr.toLowerCase().includes(searchTerm.toLowerCase()) ||
      posten.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || posten.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const gesamtOffen = filteredPosten.reduce((sum, p) => sum + p.offen, 0)
  const ueberfaellig = filteredPosten.filter((p) => p.tageUeberfaellig > 0)

  const columns = [
    {
      key: 'rechnungsNr' as const,
      label: 'Rechnung',
      render: (posten: OffenerPosten) => (
        <button
          onClick={() => navigate(`/sales/invoice-editor?id=${posten.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {posten.rechnungsNr}
        </button>
      ),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
    },
    {
      key: 'rechnungsDatum' as const,
      label: 'Rechnungsdatum',
      render: (posten: OffenerPosten) => new Date(posten.rechnungsDatum).toLocaleDateString('de-DE'),
    },
    {
      key: 'faelligAm' as const,
      label: 'Fällig am',
      render: (posten: OffenerPosten) => {
        const faellig = new Date(posten.faelligAm)
        const heute = new Date()
        const isUeberfaellig = faellig < heute
        return (
          <span className={isUeberfaellig ? 'font-semibold text-red-600' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'offen' as const,
      label: 'Offener Betrag',
      render: (posten: OffenerPosten) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(posten.offen)}
        </span>
      ),
    },
    {
      key: 'tageUeberfaellig' as const,
      label: 'Tage überfällig',
      render: (posten: OffenerPosten) =>
        posten.tageUeberfaellig > 0 ? (
          <span className="flex items-center gap-1 text-red-600">
            <AlertCircle className="h-4 w-4" />
            {posten.tageUeberfaellig} Tage
          </span>
        ) : (
          <span className="text-muted-foreground">-</span>
        ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (posten: OffenerPosten) => (
        <Badge variant={statusVariantMap[posten.status]}>{getStatusLabel(t, posten.status, posten.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Offene Posten</h1>
          <p className="text-muted-foreground">Forderungsmanagement & Mahnwesen</p>
        </div>
        <Button variant="outline" className="gap-2">
          <FileDown className="h-4 w-4" />
          Mahnlauf starten
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                  gesamtOffen
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällige Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <span className="text-2xl font-bold text-red-600">{ueberfaellig.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {ueberfaellig.length > 0
                ? Math.round(
                    ueberfaellig.reduce((sum, p) => sum + p.tageUeberfaellig, 0) / ueberfaellig.length
                  )
                : 0}{' '}
              Tage
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
                placeholder="Suche nach Rechnung oder Kunde..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as OffenerPosten['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="faellig">Fällig</option>
              <option value="ueberfaellig">Überfällig</option>
              <option value="mahnung1">Mahnung 1</option>
              <option value="mahnung2">Mahnung 2</option>
              <option value="mahnung3">Mahnung 3</option>
              <option value="inkasso">Inkasso</option>
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
          <DataTable data={filteredPosten} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredPosten.length} von {mockOffenePosten.length} offene(n) Posten angezeigt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
