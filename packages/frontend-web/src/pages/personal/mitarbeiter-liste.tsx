import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Edit, FileDown, Plus, Search, Users } from 'lucide-react'
import { useMitarbeiter, type Mitarbeiter } from '@/lib/api/personal'

export default function MitarbeiterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: mitarbeiter, isLoading } = useMitarbeiter(
    searchTerm ? { search: searchTerm } : undefined
  )

  const list = useMemo(() => mitarbeiter ?? [], [mitarbeiter])

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
    { key: 'email' as const, label: 'E-Mail' },
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
    {
      key: 'id' as const,
      label: 'Aktionen',
      render: (m: Mitarbeiter) => (
        <Button size="sm" variant="outline" onClick={() => navigate(`/personal/mitarbeiter/${m.id}`)} className="gap-1">
          <Edit className="h-3 w-3" />
          Bearbeiten
        </Button>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
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
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{list.filter((m) => m.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.filter((m) => m.status === 'urlaub').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Krank</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{list.filter((m) => m.status === 'krank').length}</span>
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
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
