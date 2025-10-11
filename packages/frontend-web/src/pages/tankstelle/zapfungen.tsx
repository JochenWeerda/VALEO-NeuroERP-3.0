import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Fuel, Search } from 'lucide-react'

type Zapfung = {
  id: string
  fahrzeug: string
  fahrer: string
  kraftstoff: 'Diesel' | 'Benzin' | 'AdBlue'
  menge: number
  zeitpunkt: string
  kilometerstand: number
}

const mockZapfungen: Zapfung[] = [
  { id: '1', fahrzeug: 'LKW-01', fahrer: 'Schmidt', kraftstoff: 'Diesel', menge: 120.5, zeitpunkt: '2025-10-11 08:15', kilometerstand: 125000 },
  { id: '2', fahrzeug: 'LKW-02', fahrer: 'Müller', kraftstoff: 'Diesel', menge: 98.3, zeitpunkt: '2025-10-11 09:45', kilometerstand: 98000 },
]

export default function ZapfungenPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    { key: 'zeitpunkt' as const, label: 'Zeitpunkt', render: (z: Zapfung) => <span className="font-mono text-sm">{z.zeitpunkt}</span> },
    { key: 'fahrzeug' as const, label: 'Fahrzeug', render: (z: Zapfung) => <span className="font-mono font-bold">{z.fahrzeug}</span> },
    { key: 'fahrer' as const, label: 'Fahrer' },
    { key: 'kraftstoff' as const, label: 'Kraftstoff', render: (z: Zapfung) => <Badge variant="outline">{z.kraftstoff}</Badge> },
    { key: 'menge' as const, label: 'Menge (l)', render: (z: Zapfung) => `${z.menge} l` },
    { key: 'kilometerstand' as const, label: 'km-Stand', render: (z: Zapfung) => z.kilometerstand.toLocaleString('de-DE') },
  ]

  const gesamtMenge = mockZapfungen.reduce((sum, z) => sum + z.menge, 0)

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Tankstellen-Zapfungen</h1>
        <p className="text-muted-foreground">Betriebstankstelle</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zapfungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Fuel className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockZapfungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Menge</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtMenge.toFixed(1)} l</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Durchschnitt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{(gesamtMenge / mockZapfungen.length).toFixed(1)} l</span>
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
          <DataTable data={mockZapfungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
