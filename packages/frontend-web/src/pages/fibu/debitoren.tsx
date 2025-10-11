import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Euro, FileDown, Search } from 'lucide-react'

type OffenerPosten = {
  id: string
  rechnungsnr: string
  kunde: string
  kundennr: string
  datum: string
  faelligkeit: string
  betrag: number
  offen: number
  ueberfaellig: boolean
  mahnStufe: number
}

const mockDebitoren: OffenerPosten[] = [
  { id: '1', rechnungsnr: 'RE-2025-0123', kunde: 'Agrar Schmidt GmbH', kundennr: 'K-10001', datum: '2025-09-15', faelligkeit: '2025-10-15', betrag: 12500, offen: 12500, ueberfaellig: false, mahnStufe: 0 },
  { id: '2', rechnungsnr: 'RE-2025-0098', kunde: 'Landwirtschaft Müller', kundennr: 'K-10023', datum: '2025-08-20', faelligkeit: '2025-09-20', betrag: 8750, offen: 8750, ueberfaellig: true, mahnStufe: 1 },
  { id: '3', rechnungsnr: 'RE-2025-0145', kunde: 'Hofgut Weber', kundennr: 'K-10045', datum: '2025-10-01', faelligkeit: '2025-11-01', betrag: 15200, offen: 15200, ueberfaellig: false, mahnStufe: 0 },
]

export default function DebitorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'rechnungsnr' as const,
      label: 'Rechnung',
      render: (op: OffenerPosten) => (
        <button onClick={() => navigate(`/sales/invoice/${op.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {op.rechnungsnr}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Kunde' },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (op: OffenerPosten) => <span className="font-mono text-sm">{op.kundennr}</span> },
    { key: 'datum' as const, label: 'Re-Datum', render: (op: OffenerPosten) => new Date(op.datum).toLocaleDateString('de-DE') },
    {
      key: 'faelligkeit' as const,
      label: 'Fälligkeit',
      render: (op: OffenerPosten) => {
        const faellig = new Date(op.faelligkeit)
        const ueberfaellig = faellig < new Date()
        return (
          <span className={ueberfaellig ? 'font-semibold text-red-600' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (op: OffenerPosten) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.betrag),
    },
    {
      key: 'offen' as const,
      label: 'Offen',
      render: (op: OffenerPosten) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.offen)}
        </span>
      ),
    },
    {
      key: 'mahnStufe' as const,
      label: 'Status',
      render: (op: OffenerPosten) => {
        if (op.mahnStufe > 0) {
          return <Badge variant="destructive">Mahnstufe {op.mahnStufe}</Badge>
        }
        if (op.ueberfaellig) {
          return <Badge variant="secondary">Überfällig</Badge>
        }
        return <Badge variant="outline">Offen</Badge>
      },
    },
  ]

  const gesamtOffen = mockDebitoren.reduce((sum, op) => sum + op.offen, 0)
  const ueberfaellig = mockDebitoren.filter((op) => op.ueberfaellig).length
  const mahnungen = mockDebitoren.filter((op) => op.mahnStufe > 0).length

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Debitorenbuchhaltung</h1>
        <p className="text-muted-foreground">Offene Posten Kunden</p>
      </div>

      {ueberfaellig > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ueberfaellig} überfällige Rechnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockDebitoren.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtOffen)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Mahnung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mahnungen}</span>
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
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockDebitoren} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
