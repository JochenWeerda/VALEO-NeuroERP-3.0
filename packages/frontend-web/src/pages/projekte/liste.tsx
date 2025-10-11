import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, FolderKanban, Plus, Search } from 'lucide-react'

type Projekt = {
  id: string
  name: string
  kunde: string
  startdatum: string
  enddatum: string
  fortschritt: number
  budget: number
  status: 'geplant' | 'aktiv' | 'abgeschlossen'
}

const mockProjekte: Projekt[] = [
  { id: '1', name: 'Silo-Neubau', kunde: 'Eigenbau', startdatum: '2025-09-01', enddatum: '2025-12-31', fortschritt: 45, budget: 250000, status: 'aktiv' },
  { id: '2', name: 'Lagerhallen-Sanierung', kunde: 'Eigenbau', startdatum: '2026-01-01', enddatum: '2026-03-31', fortschritt: 0, budget: 85000, status: 'geplant' },
]

export default function ProjekteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Projekt',
      render: (p: Projekt) => (
        <button onClick={() => navigate(`/projekte/${p.id}`)} className="font-medium text-blue-600 hover:underline">
          {p.name}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Auftraggeber' },
    {
      key: 'startdatum' as const,
      label: 'Zeitraum',
      render: (p: Projekt) => (
        <span className="text-sm">
          {new Date(p.startdatum).toLocaleDateString('de-DE')} - {new Date(p.enddatum).toLocaleDateString('de-DE')}
        </span>
      ),
    },
    {
      key: 'fortschritt' as const,
      label: 'Fortschritt',
      render: (p: Projekt) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden max-w-24">
            <div className="h-full bg-blue-600" style={{ width: `${p.fortschritt}%` }} />
          </div>
          <span className="text-sm font-semibold">{p.fortschritt}%</span>
        </div>
      ),
    },
    {
      key: 'budget' as const,
      label: 'Budget',
      render: (p: Projekt) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(p.budget),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (p: Projekt) => (
        <Badge variant={p.status === 'aktiv' ? 'default' : p.status === 'abgeschlossen' ? 'outline' : 'secondary'}>
          {p.status === 'geplant' ? 'Geplant' : p.status === 'aktiv' ? 'Aktiv' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projekte</h1>
          <p className="text-muted-foreground">Projektmanagement</p>
        </div>
        <Button onClick={() => navigate('/projekte/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Projekt
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Projekte Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FolderKanban className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockProjekte.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockProjekte.filter((p) => p.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockProjekte.filter((p) => p.status === 'geplant').length}</span>
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
          <DataTable data={mockProjekte} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
