import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Beaker, FileDown, Plus, Search } from 'lucide-react'

type Probe = {
  id: string
  probennummer: string
  typ: string
  artikel: string
  datum: string
  labor: string
  status: 'eingang' | 'analyse' | 'abgeschlossen'
}

const mockProben: Probe[] = [
  { id: '1', probennummer: 'LB-2025-001', typ: 'Qualitätsprüfung', artikel: 'Weizen Premium', datum: '2025-10-10', labor: 'Lufa Nord-West', status: 'abgeschlossen' },
  { id: '2', probennummer: 'LB-2025-002', typ: 'Mykotoxin-Test', artikel: 'Mais', datum: '2025-10-11', labor: 'Agroisolab', status: 'analyse' },
]

export default function LaborProbenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'probennummer' as const,
      label: 'Probennummer',
      render: (p: Probe) => (
        <button onClick={() => navigate(`/labor/probe/${p.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {p.probennummer}
        </button>
      ),
    },
    { key: 'typ' as const, label: 'Typ', render: (p: Probe) => <Badge variant="outline">{p.typ}</Badge> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'datum' as const, label: 'Datum', render: (p: Probe) => new Date(p.datum).toLocaleDateString('de-DE') },
    { key: 'labor' as const, label: 'Labor' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (p: Probe) => (
        <Badge variant={p.status === 'abgeschlossen' ? 'outline' : p.status === 'analyse' ? 'secondary' : 'default'}>
          {p.status === 'eingang' ? 'Eingang' : p.status === 'analyse' ? 'In Analyse' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Laborproben</h1>
          <p className="text-muted-foreground">Proben-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/labor/probe/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Probe
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Proben Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Beaker className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockProben.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Analyse</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockProben.filter((p) => p.status === 'analyse').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockProben.filter((p) => p.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eingang</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockProben.filter((p) => p.status === 'eingang').length}</span>
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
          <DataTable data={mockProben} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
