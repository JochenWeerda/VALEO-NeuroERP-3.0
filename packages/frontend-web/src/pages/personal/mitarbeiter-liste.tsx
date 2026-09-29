import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, Plus, Search, Users } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { useMitarbeiter, type Mitarbeiter } from '@/lib/api/personal'

export default function MitarbeiterListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
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
        <button type="button" onClick={() => navigate(`/personal/mitarbeiter/${m.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
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
        <Button className="min-h-touch touch-manipulation" variant="outline" onClick={() => navigate(`/personal/mitarbeiter/${m.id}`)}>
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
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Mitarbeiter</h1>
          <p className="text-muted-foreground">Personal suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/personal/mitarbeiter/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neuer Mitarbeiter
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{list.filter((m) => m.status === 'aktiv').length}</span>
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
            <span className="text-2xl font-bold text-status-error">{list.filter((m) => m.status === 'krank').length}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input aria-label="Suche Mitarbeiter" placeholder="Name, Abteilung, Position" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation">
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
