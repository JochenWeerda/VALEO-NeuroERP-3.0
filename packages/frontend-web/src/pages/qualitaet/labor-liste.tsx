import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Beaker, FileDown, Plus, Search } from 'lucide-react'

type LaborAuftrag = {
  id: string
  chargenId: string
  labor: string
  analysen: number
  auftragsdatum: string
  status: 'offen' | 'in-bearbeitung' | 'abgeschlossen'
}

const mockAuftraege: LaborAuftrag[] = [
  { id: 'LA-001', chargenId: '251011-WEI-001', labor: 'Labor Nord', analysen: 4, auftragsdatum: '2025-10-11', status: 'in-bearbeitung' },
  { id: 'LA-002', chargenId: '251010-RAP-002', labor: 'Labor Süd', analysen: 6, auftragsdatum: '2025-10-10', status: 'abgeschlossen' },
]

export default function LaborListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'id' as const,
      label: 'Auftrag',
      render: (l: LaborAuftrag) => (
        <button onClick={() => navigate(`/qualitaet/labor/${l.id}`)} className="font-medium text-blue-600 hover:underline">
          {l.id}
        </button>
      ),
    },
    { key: 'chargenId' as const, label: 'Charge', render: (l: LaborAuftrag) => <span className="font-mono">{l.chargenId}</span> },
    { key: 'labor' as const, label: 'Labor' },
    { key: 'analysen' as const, label: 'Analysen', render: (l: LaborAuftrag) => `${l.analysen} Analysen` },
    {
      key: 'auftragsdatum' as const,
      label: 'Datum',
      render: (l: LaborAuftrag) => new Date(l.auftragsdatum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: LaborAuftrag) => (
        <Badge variant={l.status === 'abgeschlossen' ? 'outline' : l.status === 'in-bearbeitung' ? 'secondary' : 'default'}>
          {l.status === 'offen' ? 'Offen' : l.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Labor-Aufträge</h1>
          <p className="text-muted-foreground">Qualitätsanalysen</p>
        </div>
        <Button onClick={() => navigate('/qualitaet/labor-auftrag')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Auftrag
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufträge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Beaker className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockAuftraege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockAuftraege.filter((a) => a.status === 'in-bearbeitung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockAuftraege.filter((a) => a.status === 'abgeschlossen').length}</span>
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
          <DataTable data={mockAuftraege} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
