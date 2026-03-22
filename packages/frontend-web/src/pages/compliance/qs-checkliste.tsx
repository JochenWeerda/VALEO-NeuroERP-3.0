import { useQSCheckliste, type QSItem } from '@/lib/api/betrieb'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import { AlertTriangle, CheckCircle, ClipboardCheck } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function QSChecklistePage(): JSX.Element {
  const { data: qs = [], isError, error, refetch } = useQSCheckliste()

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    { key: 'bereich' as const, label: 'Bereich' },
    { key: 'pruefpunkt' as const, label: 'Pruefpunkt' },
    {
      key: 'erfuellt' as const,
      label: 'Status',
      render: (q: QSItem) => (
        q.erfuellt ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-semibold text-green-600">Erfuellt</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <span className="font-semibold text-red-600">Offen</span>
          </div>
        )
      ),
    },
    { key: 'bemerkung' as const, label: 'Bemerkung' },
    {
      key: 'geprueftAm' as const,
      label: 'Geprueft am',
      render: (q: QSItem) => q.geprueftAm ? new Date(q.geprueftAm).toLocaleDateString('de-DE') : '-',
    },
  ]

  const erfuellt = qs.filter((q) => q.erfuellt).length
  const offen = qs.filter((q) => !q.erfuellt).length

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">QS-Checkliste</h1>
          <p className="text-muted-foreground">Quality & Safety</p>
        </div>
        <Button>Audit starten</Button>
      </div>
      <AgentProcessPanel domain="compliance" />

      {offen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Pruefpunkt(e) NICHT erfuellt!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pruefpunkte Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{qs.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfuellt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{erfuellt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{offen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={qs} columns={columns} />
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}


