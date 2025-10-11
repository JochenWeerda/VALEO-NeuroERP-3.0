import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertCircle, FileDown, Plus, Search } from 'lucide-react'

type Reklamation = {
  id: string
  nummer: string
  kunde: string
  artikel: string
  grund: string
  datum: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
  status: 'neu' | 'in-bearbeitung' | 'geloest' | 'abgelehnt'
}

const mockReklamationen: Reklamation[] = [
  { id: '1', nummer: 'REK-2025-001', kunde: 'Landhandel Nord', artikel: 'Weizen', grund: 'Feuchtigkeit zu hoch', datum: '2025-10-11', prioritaet: 'hoch', status: 'neu' },
  { id: '2', nummer: 'REK-2025-002', kunde: 'Müller GmbH', artikel: 'Sojaschrot', grund: 'Falsche Menge', datum: '2025-10-10', prioritaet: 'normal', status: 'in-bearbeitung' },
]

export default function ReklamationenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const neu = mockReklamationen.filter((r) => r.status === 'neu').length

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Reklamations-Nr.',
      render: (r: Reklamation) => (
        <button onClick={() => navigate(`/qualitaet/reklamation/${r.id}`)} className="font-medium text-blue-600 hover:underline">
          {r.nummer}
        </button>
      ),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (r: Reklamation) => (
        <div>
          <div className="font-medium">{r.kunde}</div>
          <div className="text-sm text-muted-foreground">{r.artikel}</div>
        </div>
      ),
    },
    { key: 'grund' as const, label: 'Grund' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (r: Reklamation) => new Date(r.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (r: Reklamation) => (
        <Badge variant={r.prioritaet === 'hoch' ? 'destructive' : r.prioritaet === 'normal' ? 'secondary' : 'outline'}>
          {r.prioritaet === 'hoch' ? 'Hoch' : r.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (r: Reklamation) => (
        <Badge variant={r.status === 'geloest' ? 'outline' : r.status === 'abgelehnt' ? 'destructive' : 'default'}>
          {r.status === 'neu' ? 'Neu' : r.status === 'in-bearbeitung' ? 'In Bearbeitung' : r.status === 'geloest' ? 'Gelöst' : 'Abgelehnt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reklamationen</h1>
          <p className="text-muted-foreground">Qualitäts-Beschwerden</p>
        </div>
        <Button onClick={() => navigate('/qualitaet/reklamation/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Reklamation
        </Button>
      </div>

      {neu > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertCircle className="h-5 w-5" />
              <span className="font-semibold">{neu} neue Reklamation(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reklamationen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockReklamationen.length}</span>
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
            <span className="text-2xl font-bold text-orange-600">{mockReklamationen.filter((r) => r.status === 'in-bearbeitung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gelöst</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockReklamationen.filter((r) => r.status === 'geloest').length}</span>
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
          <DataTable data={mockReklamationen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
