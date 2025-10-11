import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Scale, Search } from 'lucide-react'

type Wiegung = {
  id: string
  kennzeichen: string
  artikel: string
  brutto: number
  tara: number
  netto: number
  zeitstempel: string
  waage: string
}

const mockWiegungen: Wiegung[] = [
  { id: '1', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', brutto: 48.5, tara: 23.5, netto: 25.0, zeitstempel: '2025-10-11 14:32', waage: 'W-001' },
  { id: '2', kennzeichen: 'EF-GH 5678', artikel: 'Raps', brutto: 42.0, tara: 23.5, netto: 18.5, zeitstempel: '2025-10-11 13:15', waage: 'W-001' },
]

export default function WiegungenPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'zeitstempel' as const,
      label: 'Zeitstempel',
      render: (w: Wiegung) => <span className="font-mono text-sm">{w.zeitstempel}</span>,
    },
    { key: 'kennzeichen' as const, label: 'Kennzeichen', render: (w: Wiegung) => <span className="font-mono font-bold">{w.kennzeichen}</span> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'brutto' as const, label: 'Brutto (t)', render: (w: Wiegung) => `${w.brutto} t` },
    { key: 'tara' as const, label: 'Tara (t)', render: (w: Wiegung) => `${w.tara} t` },
    {
      key: 'netto' as const,
      label: 'Netto (t)',
      render: (w: Wiegung) => <span className="font-bold">{w.netto} t</span>,
    },
    { key: 'waage' as const, label: 'Waage', render: (w: Wiegung) => <Badge variant="outline">{w.waage}</Badge> },
  ]

  const gesamtNetto = mockWiegungen.reduce((sum, w) => sum + w.netto, 0)

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wiegungen</h1>
        <p className="text-muted-foreground">Wiegehistorie</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Wiegungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockWiegungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Netto</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtNetto.toFixed(1)} t</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Durchschnitt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{(gesamtNetto / mockWiegungen.length).toFixed(1)} t</span>
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
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockWiegungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
