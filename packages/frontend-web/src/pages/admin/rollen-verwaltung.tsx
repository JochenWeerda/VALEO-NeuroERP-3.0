import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Plus, Search, Shield } from 'lucide-react'

type Rolle = {
  id: string
  name: string
  beschreibung: string
  benutzer: number
  rechte: number
}

const mockRollen: Rolle[] = [
  { id: '1', name: 'Administrator', beschreibung: 'Vollzugriff', benutzer: 2, rechte: 150 },
  { id: '2', name: 'Vertrieb', beschreibung: 'Verkaufsprozesse', benutzer: 8, rechte: 45 },
  { id: '3', name: 'Einkauf', beschreibung: 'Beschaffung', benutzer: 5, rechte: 38 },
  { id: '4', name: 'Lager', beschreibung: 'Lagerverwaltung', benutzer: 12, rechte: 25 },
]

export default function RollenVerwaltungPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Rolle',
      render: (r: Rolle) => (
        <button onClick={() => navigate(`/admin/rolle/${r.id}`)} className="font-medium text-blue-600 hover:underline">
          {r.name}
        </button>
      ),
    },
    { key: 'beschreibung' as const, label: 'Beschreibung' },
    { key: 'benutzer' as const, label: 'Benutzer', render: (r: Rolle) => `${r.benutzer} Benutzer` },
    { key: 'rechte' as const, label: 'Rechte', render: (r: Rolle) => <Badge variant="outline">{r.rechte} Rechte</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Rollen-Verwaltung</h1>
          <p className="text-muted-foreground">Berechtigungen & Rollen</p>
        </div>
        <Button onClick={() => navigate('/admin/rolle/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Rolle
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rollen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockRollen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Benutzer Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockRollen.reduce((sum, r) => sum + r.benutzer, 0)}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockRollen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
