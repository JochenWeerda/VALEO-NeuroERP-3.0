import { useCrossCompliance, type ComplianceItem } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import { AlertTriangle, CheckCircle, ClipboardCheck } from 'lucide-react'

export default function CrossCompliancePage(): JSX.Element {
  const { data: compliance = [], isLoading, refetch } = useCrossCompliance()

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
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

  const columns = [
    { key: 'bereich' as const, label: 'Bereich', render: (c: ComplianceItem) => <Badge variant="outline">{c.bereich}</Badge> },
    { key: 'anforderung' as const, label: 'Anforderung' },
    {
      key: 'erfuellt' as const,
      label: 'Erfuellt',
      render: (c: ComplianceItem) => (
        c.erfuellt ? (
          <CheckCircle className="h-5 w-5 text-status-success" />
        ) : (
          <AlertTriangle className="h-5 w-5 text-status-error" />
        )
      ),
    },
    { key: 'nachweis' as const, label: 'Nachweis' },
    {
      key: 'frist' as const,
      label: 'Frist',
      render: (c: ComplianceItem) => new Date(c.frist).toLocaleDateString('de-DE'),
    },
  ]

  const erfuellt = compliance.filter((c) => c.erfuellt).length
  const offen = compliance.filter((c) => !c.erfuellt).length

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Cross-Compliance</h1>
        <p className="text-muted-foreground">Foerder-Voraussetzungen</p>
      </div>
      <AgentProcessPanel domain="compliance" />

      {offen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Anforderung(en) NICHT erfuellt!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anforderungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{compliance.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfuellt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold text-status-success">{erfuellt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{offen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={compliance} columns={columns} />
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}


