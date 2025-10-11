import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Clock } from 'lucide-react'

type ZeitEintrag = {
  id: string
  mitarbeiter: string
  datum: string
  kommen: string
  gehen: string
  stunden: number
  typ: 'Arbeit' | 'Überstunden' | 'Urlaub'
}

const mockZeiten: ZeitEintrag[] = [
  { id: '1', mitarbeiter: 'Max Schmidt', datum: '2025-10-11', kommen: '07:00', gehen: '16:30', stunden: 9.5, typ: 'Arbeit' },
  { id: '2', mitarbeiter: 'Anna Müller', datum: '2025-10-11', kommen: '08:00', gehen: '17:00', stunden: 9.0, typ: 'Arbeit' },
  { id: '3', mitarbeiter: 'Tom Weber', datum: '2025-10-11', kommen: '-', gehen: '-', stunden: 8.0, typ: 'Urlaub' },
]

export default function ZeiterfassungPage(): JSX.Element {
  const [_searchTerm, _setSearchTerm] = useState('')

  const columns = [
    {
      key: 'mitarbeiter' as const,
      label: 'Mitarbeiter',
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (z: ZeitEintrag) => new Date(z.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kommen' as const,
      label: 'Kommen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.kommen}</span>,
    },
    {
      key: 'gehen' as const,
      label: 'Gehen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.gehen}</span>,
    },
    {
      key: 'stunden' as const,
      label: 'Stunden',
      render: (z: ZeitEintrag) => <span className="font-semibold">{z.stunden} h</span>,
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (z: ZeitEintrag) => (
        <Badge variant={z.typ === 'Überstunden' ? 'destructive' : z.typ === 'Urlaub' ? 'secondary' : 'outline'}>
          {z.typ}
        </Badge>
      ),
    },
  ]

  const gesamtStunden = mockZeiten.reduce((sum, z) => sum + z.stunden, 0)

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Zeiterfassung</h1>
        <p className="text-muted-foreground">Arbeitszeitdokumentation</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Anwesend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockZeiten.filter((z) => z.typ === 'Arbeit').length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stunden Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtStunden.toFixed(1)} h</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockZeiten.filter((z) => z.typ === 'Urlaub').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockZeiten} columns={columns} />
          <div className="mt-6 flex justify-between border-t pt-4 font-bold">
            <span>Gesamt-Stunden Heute:</span>
            <span>{gesamtStunden.toFixed(1)} h</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
