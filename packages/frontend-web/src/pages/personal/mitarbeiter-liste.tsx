import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Users } from 'lucide-react'

type Mitarbeiter = {
  id: string
  name: string
  abteilung: string
  position: string
  eintrittsdatum: string
  status: 'aktiv' | 'urlaub' | 'krank'
}

const mockMitarbeiter: Mitarbeiter[] = [
  { id: '1', name: 'Max Schmidt', abteilung: 'Lager', position: 'Lagerleiter', eintrittsdatum: '2018-03-15', status: 'aktiv' },
  { id: '2', name: 'Anna Müller', abteilung: 'Vertrieb', position: 'Verkaufsleiter', eintrittsdatum: '2019-08-01', status: 'aktiv' },
  { id: '3', name: 'Tom Weber', abteilung: 'Annahme', position: 'Schichtleiter', eintrittsdatum: '2020-01-10', status: 'urlaub' },
]

export default function MitarbeiterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (m: Mitarbeiter) => (
        <button onClick={() => navigate(`/personal/mitarbeiter/${m.id}`)} className="font-medium text-blue-600 hover:underline">
          {m.name}
        </button>
      ),
    },
    { key: 'abteilung' as const, label: 'Abteilung', render: (m: Mitarbeiter) => <Badge variant="outline">{m.abteilung}</Badge> },
    { key: 'position' as const, label: 'Position' },
    {
      key: 'eintrittsdatum' as const,
      label: 'Eintritt',
      render: (m: Mitarbeiter) => new Date(m.eintrittsdatum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (m: Mitarbeiter) => (
        <Badge variant={m.status === 'aktiv' ? 'outline' : m.status === 'urlaub' ? 'secondary' : 'destructive'}>
          {m.status === 'aktiv' ? 'Aktiv' : m.status === 'urlaub' ? 'Urlaub' : 'Krank'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mitarbeiter</h1>
          <p className="text-muted-foreground">Personalverwaltung</p>
        </div>
        <Button onClick={() => navigate('/personal/mitarbeiter/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Mitarbeiter
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockMitarbeiter.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockMitarbeiter.filter((m) => m.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockMitarbeiter.filter((m) => m.status === 'urlaub').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Krank</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mockMitarbeiter.filter((m) => m.status === 'krank').length}</span>
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
          <DataTable data={mockMitarbeiter} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
