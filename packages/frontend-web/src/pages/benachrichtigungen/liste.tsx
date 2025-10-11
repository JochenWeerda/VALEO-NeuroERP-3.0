import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Bell, CheckCircle } from 'lucide-react'

type Benachrichtigung = {
  id: string
  titel: string
  nachricht: string
  typ: 'info' | 'warnung' | 'fehler'
  zeitstempel: string
  gelesen: boolean
}

const mockBenachrichtigungen: Benachrichtigung[] = [
  { id: '1', titel: 'Neue Bestellung eingegangen', nachricht: 'PO-2025-042 von Saatgut AG', typ: 'info', zeitstempel: '2025-10-11 14:32', gelesen: false },
  { id: '2', titel: 'Qualitätsprüfung erforderlich', nachricht: 'Charge 251011-WEI-001', typ: 'warnung', zeitstempel: '2025-10-11 13:15', gelesen: false },
  { id: '3', titel: 'Rechnung überfällig', nachricht: 'RE-2025-038 seit 5 Tagen', typ: 'fehler', zeitstempel: '2025-10-11 10:20', gelesen: true },
]

export default function BenachrichtigungenPage(): JSX.Element {
  const [_searchTerm, _setSearchTerm] = useState('')

  const columns = [
    {
      key: 'titel' as const,
      label: 'Titel',
      render: (b: Benachrichtigung) => (
        <div>
          <div className={`font-medium ${!b.gelesen ? 'font-bold' : ''}`}>{b.titel}</div>
          <div className="text-sm text-muted-foreground">{b.nachricht}</div>
        </div>
      ),
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (b: Benachrichtigung) => (
        <Badge variant={b.typ === 'fehler' ? 'destructive' : b.typ === 'warnung' ? 'secondary' : 'outline'}>
          {b.typ === 'info' ? 'Info' : b.typ === 'warnung' ? 'Warnung' : 'Fehler'}
        </Badge>
      ),
    },
    {
      key: 'zeitstempel' as const,
      label: 'Zeit',
      render: (b: Benachrichtigung) => <span className="font-mono text-sm">{b.zeitstempel}</span>,
    },
    {
      key: 'gelesen' as const,
      label: 'Status',
      render: (b: Benachrichtigung) => (
        b.gelesen ? (
          <Badge variant="outline">
            <CheckCircle className="h-3 w-3 mr-1 inline" />
            Gelesen
          </Badge>
        ) : (
          <Badge variant="default">Neu</Badge>
        )
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (b: Benachrichtigung) => (
        <Button size="sm" variant="ghost" disabled={b.gelesen}>
          Als gelesen markieren
        </Button>
      ),
    },
  ]

  const ungelesen = mockBenachrichtigungen.filter((b) => !b.gelesen).length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Benachrichtigungen</h1>
          <p className="text-muted-foreground">System-Nachrichten</p>
        </div>
        <Button variant="outline" disabled={ungelesen === 0}>
          Alle als gelesen markieren
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockBenachrichtigungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ungelesen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{ungelesen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Warnungen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockBenachrichtigungen.filter((b) => b.typ === 'warnung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fehler</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mockBenachrichtigungen.filter((b) => b.typ === 'fehler').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockBenachrichtigungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
