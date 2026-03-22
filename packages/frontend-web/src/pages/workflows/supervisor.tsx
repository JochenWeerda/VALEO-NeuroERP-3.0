/**
 * Process Supervisor — Agentic Workflow Übersicht
 *
 * Zeigt alle laufenden und abgeschlossenen Agent-Runs.
 * Pending-Approval-Runs können direkt hier freigegeben oder abgelehnt werden.
 * SSE-Panel zeigt Echtzeit-Aktivität.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel, AgentUxPanel } from '@/components/agent'
import { useListRuns, useApproveWorkflow, type RunListItem } from '@/lib/api/workflows'
import { getCapabilityByKey } from '@/lib/agentCapabilities'
import {
  Sparkles,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  ShieldCheck,
  Activity,
} from 'lucide-react'

function statusBadge(status: RunListItem['status']) {
  switch (status) {
    case 'completed':
      return <Badge variant="outline" className="text-green-700 border-green-300">Abgeschlossen</Badge>
    case 'pending_approval':
      return <Badge className="bg-amber-500">Freigabe ausstehend</Badge>
    case 'rejected':
      return <Badge variant="outline" className="text-red-600 border-red-300">Abgelehnt</Badge>
    case 'running':
      return <Badge variant="outline" className="text-violet-700 border-violet-300 animate-pulse">Läuft</Badge>
    case 'failed':
      return <Badge variant="destructive">Fehlgeschlagen</Badge>
    default:
      return <Badge variant="secondary">{status}</Badge>
  }
}

function statusIcon(status: RunListItem['status']) {
  switch (status) {
    case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />
    case 'pending_approval': return <Clock className="h-5 w-5 text-amber-500" />
    case 'rejected': return <XCircle className="h-5 w-5 text-red-500" />
    case 'running': return <Sparkles className="h-5 w-5 text-violet-500 animate-pulse" />
    case 'failed': return <XCircle className="h-5 w-5 text-red-600" />
    default: return <Activity className="h-5 w-5 text-slate-400" />
  }
}

export default function SupervisorPage(): JSX.Element {
  const navigate = useNavigate()
  const [rejectionInput, setRejectionInput] = useState<Record<string, string>>({})
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const runsQuery = useListRuns()
  const approveMutation = useApproveWorkflow()

  const runs = runsQuery.data ?? []
  const pendingRuns = runs.filter((r) => r.status === 'pending_approval')
  const activeRuns = runs.filter((r) => r.status === 'running')
  const doneRuns = runs.filter((r) => r.status === 'completed' || r.status === 'rejected' || r.status === 'failed')

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void runsQuery.refetch() },
    onCancel: () => navigate('/'),
  })
  useKeyboardShortcuts(shortcuts)

  const handleApprove = async (runId: string): Promise<void> => {
    await approveMutation.mutateAsync({ workflowId: runId, approved: true })
    void runsQuery.refetch()
  }

  const handleReject = async (runId: string): Promise<void> => {
    await approveMutation.mutateAsync({
      workflowId: runId,
      approved: false,
      rejection_reason: rejectionInput[runId] ?? '',
    })
    setRejectionInput((prev) => ({ ...prev, [runId]: '' }))
    void runsQuery.refetch()
  }

  return (
    <div className="flex flex-col">
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Prozess-Supervisor</h1>
            <p className="text-muted-foreground">Agentic Workflows — Übersicht und Freigaben</p>
          </div>
          <Button
            variant="outline"
            onClick={() => { void runsQuery.refetch() }}
            disabled={runsQuery.isFetching}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${runsQuery.isFetching ? 'animate-spin' : ''}`} />
            Aktualisieren
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Freigabe ausstehend</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-amber-600">{pendingRuns.length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Aktive Runs</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-violet-600">{activeRuns.length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-green-600">
                {runs.filter((r) => r.status === 'completed').length}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{runs.length}</span>
            </CardContent>
          </Card>
        </div>

        {/* Real-time panel */}
        <AgentProcessPanel domain="" className="max-w-2xl" />

        {/* Pending approvals */}
        {pendingRuns.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-amber-500" />
              Freigaben erforderlich
            </h2>
            <div className="space-y-3">
              {pendingRuns.map((run) => {
                const capability = getCapabilityByKey(run.capability_key)
                const isExpanded = expanded[run.run_id] ?? false
                return (
                  <Card key={run.run_id} className="border-amber-200 bg-amber-50/40">
                    <CardContent className="pt-4 pb-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-3">
                          {statusIcon(run.status)}
                          <div>
                            <div className="font-semibold">
                              {capability?.title ?? run.capability_key}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(run.started_at).toLocaleString('de-DE')} · {run.run_id.slice(0, 8)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {statusBadge(run.status)}
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs"
                            onClick={() => setExpanded((prev) => ({ ...prev, [run.run_id]: !isExpanded }))}
                          >
                            {isExpanded ? 'Weniger' : 'Details'}
                          </Button>
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="mt-3 space-y-2">
                          <div className="rounded-md bg-white border p-3 text-xs font-mono overflow-auto max-h-40">
                            {JSON.stringify(run.result, null, 2)}
                          </div>
                          <div className="flex items-center gap-2">
                            <input
                              className="flex-1 rounded-md border px-3 py-1.5 text-sm h-9"
                              placeholder="Ablehnungsgrund (optional)"
                              value={rejectionInput[run.run_id] ?? ''}
                              onChange={(e) =>
                                setRejectionInput((prev) => ({
                                  ...prev,
                                  [run.run_id]: e.target.value,
                                }))
                              }
                            />
                            <Button
                              size="sm"
                              className="gap-1 bg-green-600 hover:bg-green-700"
                              disabled={approveMutation.isPending}
                              onClick={() => { void handleApprove(run.run_id) }}
                            >
                              <CheckCircle className="h-3.5 w-3.5" />
                              Freigeben
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="gap-1 text-red-600 border-red-300 hover:bg-red-50"
                              disabled={approveMutation.isPending}
                              onClick={() => { void handleReject(run.run_id) }}
                            >
                              <XCircle className="h-3.5 w-3.5" />
                              Ablehnen
                            </Button>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        )}

        {/* Gap 029 — Agent UX Panel: Confidence + Quellen */}
        {runs.length > 0 && (
          <AgentUxPanel
            title="Agent Confidence"
            summary="Vertrauensscore aus laufenden Runs, Idempotenz-Abdeckung und Capability-Bereitschaft."
            confidence={
              runs.length > 0
                ? Math.round((runs.filter((r) => r.status === 'completed').length / runs.length) * 100)
                : 0
            }
            confidenceLabel="Erfolgsrate"
            sources={[
              { label: 'Capability-Registry', href: '/api/v1/agents/neuroassist/capabilities', description: 'Registrierte Agent-Capabilities und Bereitschaftsstatus' },
              { label: 'Workflow-Runs API', href: '/api/v1/agents/neuroassist/runs', description: 'Alle gestarteten Agent-Runs dieses Tenants' },
              { label: 'Idempotency-Store', href: '/api/v1/admin/idempotency-overview', description: 'Replay-Schutz und Command-Abdeckung' },
            ]}
            action={{
              label: 'Command Monitor öffnen',
              href: '/admin/command-monitor',
              description: 'Idempotenz-Überwachung und Replay-Nachweis für alle Business Commands',
            }}
          />
        )}

        {/* All runs table */}
        <div>
          <h2 className="text-lg font-semibold mb-3">Alle Runs</h2>
          {runsQuery.isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : runs.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
              <Sparkles className="h-8 w-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Noch keine Agent-Runs vorhanden.</p>
              <p className="text-xs mt-1">Agents werden aktiv, sobald Kernfluss-Seiten geöffnet werden.</p>
            </div>
          ) : (
            <div className="rounded-md border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-2 font-medium">Capability</th>
                    <th className="text-left px-4 py-2 font-medium">Status</th>
                    <th className="text-left px-4 py-2 font-medium">Gestartet</th>
                    <th className="text-left px-4 py-2 font-medium">Run-ID</th>
                    <th className="px-4 py-2" />
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => {
                    const capability = getCapabilityByKey(run.capability_key)
                    return (
                      <tr key={run.run_id} className="border-t hover:bg-muted/20 transition-colors">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {statusIcon(run.status)}
                            <div>
                              <div className="font-medium">
                                {capability?.title ?? run.capability_key}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {capability?.domain ?? ''}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">{statusBadge(run.status)}</td>
                        <td className="px-4 py-3 text-muted-foreground tabular-nums">
                          {new Date(run.started_at).toLocaleString('de-DE')}
                        </td>
                        <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                          {run.run_id.slice(0, 12)}…
                        </td>
                        <td className="px-4 py-3">
                          {run.status === 'pending_approval' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                navigate(`/workflows/approval/${run.run_id}`)
                              }
                            >
                              Freigabe
                            </Button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
