import { useNavigate } from '@/app/routing/typed-router'
import { useDisposition, type DispoPosition } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import { AlertTriangle, BarChart3, CheckCircle } from 'lucide-react'

export default function DispositionPage(): JSX.Element {
  const navigate = useNavigate()
  const { data: dispo = [], isLoading, refetch } = useDisposition()

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/einkauf/bestellvorschlaege'),
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-2" />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          <Card><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
        </div>
        <Card><CardContent className="pt-4"><Skeleton className="h-64 w-full" /></CardContent></Card>
      </div>
    )
  }

  const unterMindest = dispo.filter((d) => d.bestand < d.mindestbestand).length

  const columns = [
    { key: 'artikel' as const, label: 'Artikel' },
    {
      key: 'bestand' as const,
      label: 'Bestand',
      render: (d: DispoPosition) => (
        <span className={d.bestand < d.mindestbestand ? 'font-semibold text-status-error' : ''}>
          {d.bestand} t
        </span>
      ),
    },
    { key: 'mindestbestand' as const, label: 'Mindest', render: (d: DispoPosition) => `${d.mindestbestand} t` },
    { key: 'bedarf' as const, label: 'Bedarf', render: (d: DispoPosition) => d.bedarf > 0 ? `${d.bedarf} t` : '-' },
    {
      key: 'empfehlung' as const,
      label: 'Empfehlung',
      render: (d: DispoPosition) => (
        <div className="flex items-center gap-2">
          {d.bedarf > 0 ? (
            <AlertTriangle className="h-4 w-4 text-status-warning" />
          ) : (
            <CheckCircle className="h-4 w-4 text-status-success" />
          )}
          <span>{d.empfehlung}</span>
        </div>
      ),
    },
    {
      key: 'prioritaet' as const,
      label: 'Prioritaet',
      render: (d: DispoPosition) => (
        <Badge variant={d.prioritaet === 'hoch' ? 'destructive' : 'outline'}>
          {d.prioritaet === 'hoch' ? 'Hoch' : d.prioritaet === 'mittel' ? 'Mittel' : 'Niedrig'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Disposition</h1>
          <p className="text-muted-foreground">Bedarfsplanung</p>
        </div>
        <Button onClick={() => navigate('/einkauf/bestellvorschlaege')}>Zu Bestellvorschlaegen</Button>
      </div>
      <AgentProcessPanel domain="einkauf" />

      {unterMindest > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{unterMindest} Artikel unter Mindestbestand!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel in Dispo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{dispo.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unter Mindestbestand</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{unterMindest}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hohe Prioritaet</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{dispo.filter((d) => d.prioritaet === 'hoch').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Bedarf</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{dispo.reduce((sum, d) => sum + d.bedarf, 0)} t</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={dispo} columns={columns} />
        </CardContent>
      </Card>
    </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
