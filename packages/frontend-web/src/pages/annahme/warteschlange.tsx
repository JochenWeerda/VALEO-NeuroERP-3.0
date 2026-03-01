import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { Clock, Truck } from 'lucide-react'
import { useWarteschlange } from '@/lib/api/inventory'
import type { LKWEintrag } from '@/lib/api/inventory'

export default function WarteschlangePage(): JSX.Element {
  const navigate = useNavigate()
  const { data, isLoading } = useWarteschlange()
  const warteschlange = data?.items ?? []

  const columns = [
    { key: 'position' as const, label: '#', render: (l: LKWEintrag) => <span className="text-lg font-bold">#{l.position}</span> },
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (l: LKWEintrag) => (
        <div>
          <div className="font-mono font-bold">{l.kennzeichen}</div>
          <div className="text-sm text-muted-foreground">{l.lieferant}</div>
        </div>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'ankunft' as const, label: 'Ankunft' },
    {
      key: 'wartezeit' as const,
      label: 'Wartezeit',
      render: (l: LKWEintrag) => (
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{l.wartezeit} min</span>
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: LKWEintrag) => (
        <Badge variant={l.status === 'abgeschlossen' ? 'outline' : l.status === 'in-bearbeitung' ? 'secondary' : 'default'}>
          {l.status === 'wartend' ? 'Wartend' : l.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Abgeschlossen'}
        </Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (l: LKWEintrag) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => navigate('/annahme/qualitaets-check', { state: { eintragId: l.id } })}>
            Bearbeiten
          </Button>
        </div>
      ),
    },
  ]

  const wartend = warteschlange.filter(l => l.status === 'wartend').length
  const inBearbeitung = warteschlange.filter(l => l.status === 'in-bearbeitung').length
  const abgeschlossen = warteschlange.filter(l => l.status === 'abgeschlossen').length
  const avgWartezeit = warteschlange.length > 0
    ? Math.round(warteschlange.reduce((sum, l) => sum + l.wartezeit, 0) / warteschlange.length)
    : 0

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-4 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Annahme-Warteschlange</h1>
          <p className="text-muted-foreground">LKW-Abfertigung</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Warteschlange</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{wartend}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{inBearbeitung}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg. Wartezeit</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              <span className="text-2xl font-bold">{avgWartezeit} min</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Heute abgefertigt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{abgeschlossen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={warteschlange} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
