import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type Benutzer = {
  id: string
  name: string
  email: string
  rolle: string
  status: 'aktiv' | 'inaktiv'
  letzteAnmeldung: string
}

const mockBenutzer: Benutzer[] = [
  { id: '1', name: 'Admin User', email: 'admin@valeo.de', rolle: 'Administrator', status: 'aktiv', letzteAnmeldung: '2025-10-11' },
  { id: '2', name: 'Sales User', email: 'sales@valeo.de', rolle: 'Vertrieb', status: 'aktiv', letzteAnmeldung: '2025-10-10' },
]

export default function BenutzerListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (b: Benutzer) => (
        <button onClick={() => navigate(`/admin/benutzer/${b.id}`)} className="font-medium text-blue-600 hover:underline">
          {b.name}
        </button>
      ),
    },
    { key: 'email' as const, label: 'E-Mail' },
    { key: 'rolle' as const, label: 'Rolle', render: (b: Benutzer) => <Badge variant="outline">{b.rolle}</Badge> },
    {
      key: 'status' as const,
      label: 'Status',
      render: (b: Benutzer) => <Badge variant={b.status === 'aktiv' ? 'outline' : 'secondary'}>{b.status === 'aktiv' ? 'Aktiv' : 'Inaktiv'}</Badge>,
    },
    {
      key: 'letzteAnmeldung' as const,
      label: 'Letzte Anmeldung',
      render: (b: Benutzer) => new Date(b.letzteAnmeldung).toLocaleDateString('de-DE'),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Benutzerverwaltung</h1>
          <p className="text-muted-foreground">Benutzer & Berechtigungen</p>
        </div>
        <Button onClick={() => navigate('/admin/benutzer/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Benutzer
        </Button>
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
          <DataTable data={mockBenutzer} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
