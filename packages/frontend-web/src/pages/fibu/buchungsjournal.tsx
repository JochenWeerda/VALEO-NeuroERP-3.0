import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { BookOpen, FileDown, Search } from 'lucide-react'

type Buchung = {
  id: string
  belegnr: string
  datum: string
  sollKonto: string
  habenKonto: string
  betrag: number
  text: string
  belegart: string
}

const mockBuchungen: Buchung[] = [
  { id: '1', belegnr: 'RE-2025-0123', datum: '2025-10-11', sollKonto: '1200', habenKonto: '8400', betrag: 12500, text: 'Agrar Schmidt GmbH', belegart: 'ER' },
  { id: '2', belegnr: 'EB-2025-0098', datum: '2025-10-11', sollKonto: '4200', habenKonto: '1600', betrag: 18500, text: 'Saatgut Nord GmbH', belegart: 'EB' },
  { id: '3', belegnr: 'ZE-2025-0045', datum: '2025-10-10', sollKonto: '1800', habenKonto: '1200', betrag: 8750, text: 'Zahlung Kunde K-10023', belegart: 'ZE' },
]

export default function BuchungsjournalPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    { key: 'datum' as const, label: 'Datum', render: (b: Buchung) => new Date(b.datum).toLocaleDateString('de-DE') },
    { key: 'belegnr' as const, label: 'Belegnummer', render: (b: Buchung) => <span className="font-mono font-bold">{b.belegnr}</span> },
    {
      key: 'belegart' as const,
      label: 'Art',
      render: (b: Buchung) => (
        <Badge variant="outline">
          {b.belegart === 'ER' ? 'Erlös' : b.belegart === 'EB' ? 'Eingang' : b.belegart === 'ZE' ? 'Zahlung' : b.belegart}
        </Badge>
      ),
    },
    { key: 'sollKonto' as const, label: 'Soll', render: (b: Buchung) => <span className="font-mono">{b.sollKonto}</span> },
    { key: 'habenKonto' as const, label: 'Haben', render: (b: Buchung) => <span className="font-mono">{b.habenKonto}</span> },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (b: Buchung) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.betrag)}
        </span>
      ),
    },
    { key: 'text' as const, label: 'Buchungstext' },
  ]

  const gesamtBetrag = mockBuchungen.reduce((sum, b) => sum + b.betrag, 0)

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Buchungsjournal</h1>
        <p className="text-muted-foreground">Alle Buchungssätze</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Buchungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockBuchungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Summe Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBetrag)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Periode</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">10/2025</span>
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
              <Input placeholder="Suche Belegnummer, Konto, Text..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
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
          <DataTable data={mockBuchungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
