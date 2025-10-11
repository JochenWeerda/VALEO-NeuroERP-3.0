import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, HeadphonesIcon, Plus, Search } from 'lucide-react'

type Anfrage = {
  id: string
  nummer: string
  kunde: string
  betreff: string
  datum: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
  status: 'neu' | 'in-bearbeitung' | 'geschlossen'
}

const mockAnfragen: Anfrage[] = [
  { id: '1', nummer: 'SR-2025-001', kunde: 'Landhandel Nord', betreff: 'Lieferverzögerung', datum: '2025-10-11', prioritaet: 'hoch', status: 'neu' },
  { id: '2', nummer: 'SR-2025-002', kunde: 'Müller GmbH', betreff: 'Preisanfrage Weizen', datum: '2025-10-10', prioritaet: 'normal', status: 'in-bearbeitung' },
]

export default function ServiceAnfragenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const neu = mockAnfragen.filter((a) => a.status === 'neu').length

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Ticket-Nr.',
      render: (a: Anfrage) => (
        <button onClick={() => navigate(`/service/anfrage/${a.id}`)} className="font-medium text-blue-600 hover:underline">
          {a.nummer}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Kunde' },
    { key: 'betreff' as const, label: 'Betreff' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (a: Anfrage) => new Date(a.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (a: Anfrage) => (
        <Badge variant={a.prioritaet === 'hoch' ? 'destructive' : a.prioritaet === 'normal' ? 'secondary' : 'outline'}>
          {a.prioritaet === 'hoch' ? 'Hoch' : a.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Anfrage) => (
        <Badge variant={a.status === 'geschlossen' ? 'outline' : a.status === 'in-bearbeitung' ? 'secondary' : 'default'}>
          {a.status === 'neu' ? 'Neu' : a.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Geschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Service-Anfragen</h1>
          <p className="text-muted-foreground">Kundenservice & Support</p>
        </div>
        <Button onClick={() => navigate('/service/anfrage/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Anfrage
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anfragen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <HeadphonesIcon className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockAnfragen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Neu</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{neu}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockAnfragen.filter((a) => a.status === 'in-bearbeitung').length}</span>
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
          <DataTable data={mockAnfragen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
