import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search } from 'lucide-react'

type Schaden = {
  id: string
  nummer: string
  art: string
  datum: string
  ort: string
  schadenhoehe: number
  status: 'gemeldet' | 'in-bearbeitung' | 'reguliert' | 'abgelehnt'
}

const mockSchaeden: Schaden[] = [
  { id: '1', nummer: 'SCH-2025-001', art: 'Hagelschaden', datum: '2025-07-15', ort: 'Schlag S-001', schadenhoehe: 12500, status: 'reguliert' },
  { id: '2', nummer: 'SCH-2025-002', art: 'Fahrzeugunfall', datum: '2025-09-20', ort: 'Hofeinfahrt', schadenhoehe: 3200, status: 'in-bearbeitung' },
]

export default function SchaedenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Schadennummer',
      render: (s: Schaden) => (
        <button onClick={() => navigate(`/schaeden/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.nummer}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Schadenart', render: (s: Schaden) => <Badge variant="outline">{s.art}</Badge> },
    { key: 'datum' as const, label: 'Datum', render: (s: Schaden) => new Date(s.datum).toLocaleDateString('de-DE') },
    { key: 'ort' as const, label: 'Ort' },
    {
      key: 'schadenhoehe' as const,
      label: 'Schadenhöhe',
      render: (s: Schaden) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.schadenhoehe),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schaden) => (
        <Badge variant={s.status === 'reguliert' ? 'outline' : s.status === 'abgelehnt' ? 'destructive' : 'secondary'}>
          {s.status === 'gemeldet' ? 'Gemeldet' : s.status === 'in-bearbeitung' ? 'In Bearbeitung' : s.status === 'reguliert' ? 'Reguliert' : 'Abgelehnt'}
        </Badge>
      ),
    },
  ]

  const gesamtSchaden = mockSchaeden.reduce((sum, s) => sum + s.schadenhoehe, 0)
  const reguliert = mockSchaeden.filter((s) => s.status === 'reguliert').length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schäden</h1>
          <p className="text-muted-foreground">Schaden-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/schaeden/meldung')} className="gap-2">
          <Plus className="h-4 w-4" />
          Schaden melden
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schäden Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{mockSchaeden.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Schadenhöhe</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtSchaden)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reguliert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{reguliert}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockSchaeden.filter((s) => s.status === 'in-bearbeitung').length}</span>
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
          <DataTable data={mockSchaeden} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
