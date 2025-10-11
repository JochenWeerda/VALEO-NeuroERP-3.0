import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Clock, Truck } from 'lucide-react'

type LKWEintrag = {
  id: string
  position: number
  kennzeichen: string
  lieferant: string
  artikel: string
  ankunft: string
  wartezeit: number
  status: 'wartend' | 'in-bearbeitung' | 'abgeschlossen'
}

const mockWarteschlange: LKWEintrag[] = [
  { id: '1', position: 1, kennzeichen: 'AB-CD 1234', lieferant: 'Landwirt Schmidt', artikel: 'Weizen', ankunft: '08:30', wartezeit: 15, status: 'in-bearbeitung' },
  { id: '2', position: 2, kennzeichen: 'EF-GH 5678', lieferant: 'Müller Agrar', artikel: 'Raps', ankunft: '08:45', wartezeit: 30, status: 'wartend' },
]

export default function WarteschlangePagePage(): JSX.Element {
  const [_searchTerm, _setSearchTerm] = useState('')

  const columns = [
    { key: 'position' as const, label: '#', render: (l: LKWEintrag) => <span className="text-lg font-bold">#{l.position}</span> },
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (l: LKWEintrag) => (
        <div>
          <div className="font-mono font-bold">{l.kennzeichen}</div>
          <div className="text-sm text-muted-foreground">{l.lieferant}</div>
        </div>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'ankunft' as const, label: 'Ankunft' },
    {
      key: 'wartezeit' as const,
      label: 'Wartezeit',
      render: (l: LKWEintrag) => (
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{l.wartezeit} min</span>
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: LKWEintrag) => (
        <Badge variant={l.status === 'abgeschlossen' ? 'outline' : l.status === 'in-bearbeitung' ? 'secondary' : 'default'}>
          {l.status === 'wartend' ? 'Wartend' : l.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Abgeschlossen'}
        </Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: () => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline">Bearbeiten</Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Annahme-Warteschlange</h1>
          <p className="text-muted-foreground">LKW-Abfertigung</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Warteschlange</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockWarteschlange.filter((l) => l.status === 'wartend').length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockWarteschlange.filter((l) => l.status === 'in-bearbeitung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Wartezeit</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              <span className="text-2xl font-bold">22 min</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Heute abgefertigt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockWarteschlange.filter((l) => l.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockWarteschlange} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
