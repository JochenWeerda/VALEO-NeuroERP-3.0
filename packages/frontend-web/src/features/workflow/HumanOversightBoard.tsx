import { startTransition, useDeferredValue, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import type { RunListItem } from '@/lib/api/workflows'
import { getCapabilityByKey } from '@/lib/agentCapabilities'
import { Activity, CheckCircle, Clock, Search, ShieldCheck, XCircle } from 'lucide-react'

type HumanOversightBoardProps = {
  runs: RunListItem[]
  isRefreshing?: boolean
  canActOnRun?: (_run: RunListItem) => boolean
  rejectionInput: Record<string, string>
  onRejectionInputChange: (_runId: string, _value: string) => void
  onRefresh: () => void
  onApprove: (_runId: string) => void
  onReject: (_runId: string) => void
}

function statusBadge(status: RunListItem['status']) {
  switch (status) {
    case 'completed':
      return <Badge variant="success">Abgeschlossen</Badge>
    case 'pending_approval':
      return <Badge variant="warning">Freigabe ausstehend</Badge>
    case 'rejected':
      return <Badge variant="destructive">Abgelehnt</Badge>
    case 'running':
      return <Badge variant="info">Laeuft</Badge>
    case 'failed':
      return <Badge variant="destructive">Fehlgeschlagen</Badge>
    default:
      return <Badge variant="secondary">{status}</Badge>
  }
}

function statusIcon(status: RunListItem['status']) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-[hsl(var(--color-semantic-success-600-hsl))]" />
    case 'pending_approval':
      return <Clock className="h-4 w-4 text-[hsl(var(--color-semantic-warning-600-hsl))]" />
    case 'rejected':
      return <XCircle className="h-4 w-4 text-destructive" />
    default:
      return <Activity className="h-4 w-4 text-muted-foreground" />
  }
}

export function HumanOversightBoard({
  runs,
  isRefreshing = false,
  canActOnRun = (run) => run.capability_key === 'bestellvorschlag_assistant',
  rejectionInput,
  onRejectionInputChange,
  onRefresh,
  onApprove,
  onReject,
}: HumanOversightBoardProps): JSX.Element {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(runs[0]?.run_id ?? null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | RunListItem['status']>('all')
  const deferredSearch = useDeferredValue(search.trim().toLowerCase())

  const filteredRuns = runs.filter((run) => {
    if (statusFilter !== 'all' && run.status !== statusFilter) {
      return false
    }
    if (deferredSearch.length === 0) {
      return true
    }
    const capability = getCapabilityByKey(run.capability_key)
    const haystack = [
      run.run_id,
      run.capability_key,
      capability?.title ?? '',
      JSON.stringify(run.result ?? {}),
    ]
      .join(' ')
      .toLowerCase()
    return haystack.includes(deferredSearch)
  })

  const selectedRun =
    filteredRuns.find((run) => run.run_id === selectedRunId) ??
    filteredRuns[0] ??
    null

  const pendingRuns = runs.filter((run) => run.status === 'pending_approval').length
  const completedRuns = runs.filter((run) => run.status === 'completed').length

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <Card>
        <CardHeader className="border-b bg-muted/40">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary" />
                Human Oversight Cases
              </CardTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                Pending Runs, Freigaben und Abschlussfaelle in einer Arbeitsoberflaeche.
              </p>
            </div>
            <Button variant="outline" onClick={onRefresh} disabled={isRefreshing}>
              {isRefreshing ? 'Aktualisiere ...' : 'Aktualisieren'}
            </Button>
          </div>
          <div className="grid gap-3 md:grid-cols-4">
            <div className="rounded-xl border bg-card p-3">
              <div className="text-xs uppercase text-muted-foreground">Gesamt</div>
              <div className="mt-1 text-2xl font-semibold">{runs.length}</div>
            </div>
            <div className="rounded-xl border border-[hsl(var(--color-semantic-warning-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-warning-50-hsl))] p-3">
              <div className="text-xs uppercase text-[hsl(var(--color-semantic-warning-700-hsl))]">Freigabe ausstehend</div>
              <div className="mt-1 text-2xl font-semibold text-[hsl(var(--color-semantic-warning-700-hsl))]">{pendingRuns}</div>
            </div>
            <div className="rounded-xl border border-[hsl(var(--color-semantic-success-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-success-50-hsl))] p-3">
              <div className="text-xs uppercase text-[hsl(var(--color-semantic-success-700-hsl))]">Abgeschlossen</div>
              <div className="mt-1 text-2xl font-semibold text-[hsl(var(--color-semantic-success-700-hsl))]">{completedRuns}</div>
            </div>
            <div className="rounded-xl border bg-muted p-3">
              <div className="text-xs uppercase text-muted-foreground">Capabilitys</div>
              <div className="mt-1 text-2xl font-semibold">{new Set(runs.map((run) => run.capability_key)).size}</div>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-[1fr_auto]">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="pl-9"
                placeholder="Run-ID, Capability oder Ergebnis durchsuchen"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {(['all', 'pending_approval', 'completed', 'rejected'] as const).map((status) => (
                <Button
                  key={status}
                  variant={statusFilter === status ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter(status)}
                >
                  {status === 'all' ? 'Alle' : status}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {filteredRuns.length === 0 ? (
              <div className="p-6 text-sm text-muted-foreground">Keine Runs fuer den aktuellen Filter.</div>
            ) : (
              filteredRuns.map((run) => {
                const capability = getCapabilityByKey(run.capability_key)
                const isSelected = selectedRun?.run_id === run.run_id
                return (
                  <button
                    key={run.run_id}
                    type="button"
                    className={`flex w-full items-start justify-between gap-4 px-4 py-4 text-left transition-colors ${
                      isSelected ? 'bg-muted' : 'hover:bg-muted/60'
                    }`}
                    onClick={() => {
                      startTransition(() => setSelectedRunId(run.run_id))
                    }}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        {statusIcon(run.status)}
                        <span className="font-medium">{capability?.title ?? run.capability_key}</span>
                        {statusBadge(run.status)}
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {new Date(run.started_at).toLocaleString('de-DE')} · {run.run_id}
                      </div>
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      {(run.result?.current_stage_key as string | undefined) ?? 'closure'}
                    </div>
                  </button>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="border-b bg-card">
          <CardTitle>Case-Detail</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 p-4">
          {selectedRun === null ? (
            <div className="text-sm text-muted-foreground">Kein Run ausgewaehlt.</div>
          ) : (
            <>
              <div className="space-y-2 rounded-xl border bg-muted/50 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm text-muted-foreground">Capability</div>
                    <div className="font-semibold">
                      {getCapabilityByKey(selectedRun.capability_key)?.title ?? selectedRun.capability_key}
                    </div>
                  </div>
                  {statusBadge(selectedRun.status)}
                </div>
                <div className="grid gap-3 text-sm md:grid-cols-2">
                  <div>
                    <div className="text-muted-foreground">Run-ID</div>
                    <div className="font-mono text-xs">{selectedRun.run_id}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Gestartet</div>
                    <div>{new Date(selectedRun.started_at).toLocaleString('de-DE')}</div>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Gate- und Ergebnisdaten</div>
                <pre className="max-h-72 overflow-auto rounded-xl border bg-foreground p-3 text-xs text-background">
                  {JSON.stringify(selectedRun.result, null, 2)}
                </pre>
              </div>

              {selectedRun.status === 'pending_approval' ? (
                <>
                  {canActOnRun(selectedRun) ? (
                    <div className="space-y-3 rounded-xl border border-[hsl(var(--color-semantic-warning-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-warning-50-hsl))] p-4">
                      <div className="text-sm font-medium text-[hsl(var(--color-semantic-warning-800-hsl))]">Manuelle Entscheidung</div>
                      <Input
                        value={rejectionInput[selectedRun.run_id] ?? ''}
                        onChange={(event) => onRejectionInputChange(selectedRun.run_id, event.target.value)}
                        placeholder="Ablehnungsgrund"
                      />
                      <div className="flex gap-2">
                        <Button className="flex-1" onClick={() => onApprove(selectedRun.run_id)}>
                          Freigeben
                        </Button>
                        <Button variant="destructive" className="flex-1" onClick={() => onReject(selectedRun.run_id)}>
                          Ablehnen
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-dashed p-4 text-sm text-muted-foreground">
                      Dieser Run ist sichtbar und eskalierbar, nutzt aber noch keinen generischen UI-Gate-Handler.
                    </div>
                  )}
                </>
              ) : null}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
