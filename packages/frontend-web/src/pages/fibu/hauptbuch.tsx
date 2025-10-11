import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { BookOpen, FileDown, Search } from 'lucide-react'

type Buchung = {
  id: string
  datum: string
  belegnummer: string
  konto: string
  text: string
  soll: number
  haben: number
}

const mockBuchungen: Buchung[] = [
  { id: '1', datum: '2025-10-11', belegnummer: 'RE-2025-042', konto: '8400', text: 'Warenverkauf Weizen', soll: 0, haben: 5500 },
  { id: '2', datum: '2025-10-11', belegnummer: 'RE-2025-042', konto: '1200', text: 'Forderung aus LuL', soll: 6545, haben: 0 },
  { id: '3', datum: '2025-10-10', belegnummer: 'ER-2025-015', konto: '3400', text: 'Wareneinkauf Saatgut', soll: 12000, haben: 0 },
]

export default function HauptbuchPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (b: Buchung) => new Date(b.datum).toLocaleDateString('de-DE'),
    },
    { key: 'belegnummer' as const, label: 'Beleg', render: (b: Buchung) => <span className="font-mono">{b.belegnummer}</span> },
    { key: 'konto' as const, label: 'Konto', render: (b: Buchung) => <Badge variant="outline">{b.konto}</Badge> },
    { key: 'text' as const, label: 'Buchungstext' },
    {
      key: 'soll' as const,
      label: 'Soll',
      render: (b: Buchung) => (
        <span className="font-semibold">
          {b.soll > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.soll) : '-'}
        </span>
      ),
    },
    {
      key: 'haben' as const,
      label: 'Haben',
      render: (b: Buchung) => (
        <span className="font-semibold">
          {b.haben > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.haben) : '-'}
        </span>
      ),
    },
  ]

  const summen = {
    soll: mockBuchungen.reduce((sum, b) => sum + b.soll, 0),
    haben: mockBuchungen.reduce((sum, b) => sum + b.haben, 0),
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Hauptbuch</h1>
          <p className="text-muted-foreground">Buchungsjournal</p>
        </div>
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
            <CardTitle className="text-sm font-medium">Soll Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(summen.soll)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Haben Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(summen.haben)}
            </span>
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
          <DataTable data={mockBuchungen} columns={columns} />
          <div className="mt-6 flex justify-between border-t pt-4 font-bold">
            <span>Summen:</span>
            <div className="flex gap-12">
              <span>
                Soll: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.soll)}
              </span>
              <span>
                Haben: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.haben)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
