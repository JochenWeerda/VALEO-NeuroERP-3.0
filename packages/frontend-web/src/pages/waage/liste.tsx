import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Scale, Search } from 'lucide-react'

type Waage = {
  id: string
  standort: string
  typ: string
  maxKapazitaet: number
  letzteEichung: string
  naechsteEichung: string
  status: 'aktiv' | 'wartung' | 'defekt'
}

const mockWaagen: Waage[] = [
  { id: 'W-001', standort: 'Annahme 1', typ: 'LKW-Waage', maxKapazitaet: 60, letzteEichung: '2024-08-15', naechsteEichung: '2025-08-15', status: 'aktiv' },
  { id: 'W-002', standort: 'Annahme 2', typ: 'LKW-Waage', maxKapazitaet: 60, letzteEichung: '2024-09-01', naechsteEichung: '2025-09-01', status: 'aktiv' },
]

export default function WaageListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'standort' as const,
      label: 'Standort',
      render: (w: Waage) => (
        <div>
          <div className="font-medium">{w.standort}</div>
          <div className="text-sm text-muted-foreground">{w.id}</div>
        </div>
      ),
    },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'maxKapazitaet' as const, label: 'Max. Kapazität (t)' },
    {
      key: 'naechsteEichung' as const,
      label: 'Nächste Eichung',
      render: (w: Waage) => new Date(w.naechsteEichung).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (w: Waage) => (
        <Badge variant={w.status === 'aktiv' ? 'outline' : w.status === 'wartung' ? 'secondary' : 'destructive'}>
          {w.status === 'aktiv' ? 'Aktiv' : w.status === 'wartung' ? 'Wartung' : 'Defekt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Waagen</h1>
          <p className="text-muted-foreground">Waagen-Management</p>
        </div>
        <Button onClick={() => navigate('/waage/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Waage
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Waagen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockWaagen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockWaagen.filter((w) => w.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eichung fällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">0</span>
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
          <DataTable data={mockWaagen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
