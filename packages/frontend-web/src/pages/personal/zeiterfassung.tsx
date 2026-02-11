import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { Clock } from 'lucide-react'
import { useZeiterfassung, type ZeitEintrag } from '@/lib/api/personal'

export default function ZeiterfassungPage(): JSX.Element {
  const today = new Date().toISOString().split('T')[0]
  const { data: zeiten, isLoading } = useZeiterfassung(today)
  const list = useMemo(() => zeiten ?? [], [zeiten])

  const columns = [
    { key: 'mitarbeiter' as const, label: 'Mitarbeiter' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (z: ZeitEintrag) => new Date(z.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kommen' as const,
      label: 'Kommen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.kommen}</span>,
    },
    {
      key: 'gehen' as const,
      label: 'Gehen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.gehen}</span>,
    },
    {
      key: 'stunden' as const,
      label: 'Stunden',
      render: (z: ZeitEintrag) => <span className="font-semibold">{z.stunden} h</span>,
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (z: ZeitEintrag) => (
        <Badge variant={z.typ === 'Überstunden' ? 'destructive' : z.typ === 'Urlaub' ? 'secondary' : 'outline'}>
          {z.typ}
        </Badge>
      ),
    },
  ]

  const gesamtStunden = list.reduce((sum, z) => sum + z.stunden, 0)

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Zeiterfassung</h1>
        <p className="text-muted-foreground">Arbeitszeitdokumentation</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Anwesend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.filter((z) => z.typ === 'Arbeit').length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stunden Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtStunden.toFixed(1)} h</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.filter((z) => z.typ === 'Urlaub').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
          <div className="mt-6 flex justify-between border-t pt-4 font-bold">
            <span>Gesamt-Stunden Heute:</span>
            <span>{gesamtStunden.toFixed(1)} h</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
