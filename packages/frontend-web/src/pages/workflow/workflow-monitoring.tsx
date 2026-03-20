import { useTranslation } from 'react-i18next'
import { useWorkflowExecutions, type WorkflowExecution as ApiWorkflowExecution } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { ErrorState } from '@/components/ErrorState'

type WorkflowExecution = ApiWorkflowExecution & { status: 'SUCCESS' | 'FAILED' | 'PENDING' | 'RUNNING'; errorMessage?: string }

export default function WorkflowMonitoringPage(): JSX.Element {
  const { t } = useTranslation()
  const { data: apiExecutions = [], isError, error, refetch } = useWorkflowExecutions()
  const executions: WorkflowExecution[] = apiExecutions.map((e) => ({ ...e, status: e.status as WorkflowExecution['status'] }))

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'FAILED': return <XCircle className="h-4 w-4 text-red-600" />
      case 'RUNNING': return <Clock className="h-4 w-4 text-blue-600" />
      default: return <Clock className="h-4 w-4 text-yellow-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      SUCCESS: 'outline' as const,
      FAILED: 'destructive' as const,
      RUNNING: 'secondary' as const,
      PENDING: 'secondary' as const,
    }
    return <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>{getStatusLabel(t, status.toLowerCase(), status)}</Badge>
  }

  const columns = [
    { key: 'startedAt' as const, label: 'Gestartet', render: (exec: WorkflowExecution) => new Date(exec.startedAt).toLocaleString('de-DE') },
    { key: 'triggerEntity' as const, label: 'Ausloeser', render: (exec: WorkflowExecution) => <div><div className="font-medium">{exec.triggerEntity}</div><div className="text-sm text-muted-foreground">{exec.triggerAction}</div></div> },
    { key: 'targetEntity' as const, label: 'Ziel', render: (exec: WorkflowExecution) => <div><div className="font-medium">{exec.targetEntity}</div><div className="text-sm text-muted-foreground">{exec.targetAction}</div></div> },
    { key: 'status' as const, label: 'Status', render: (exec: WorkflowExecution) => <div className="flex items-center gap-2">{getStatusIcon(exec.status)}{getStatusBadge(exec.status)}</div> },
    {
      key: 'duration' as const,
      label: 'Dauer',
      render: (exec: WorkflowExecution) => {
        const start = new Date(exec.startedAt)
        const end = exec.completedAt ? new Date(exec.completedAt) : new Date()
        return `${Math.floor((end.getTime() - start.getTime()) / 1000)}s`
      },
    },
    { key: 'errorMessage' as const, label: 'Fehler', render: (exec: WorkflowExecution) => exec.errorMessage ? <div className="text-red-600 text-sm max-w-xs truncate" title={exec.errorMessage}>{exec.errorMessage}</div> : '-' },
  ]

  const stats = {
    total: executions.length,
    success: executions.filter((e) => e.status === 'SUCCESS').length,
    failed: executions.filter((e) => e.status === 'FAILED').length,
    running: executions.filter((e) => {
      const status = e.status as string
      return status === 'RUNNING' || status === 'PENDING'
    }).length,
  }
  const successRate = stats.total > 0 ? (stats.success / stats.total) * 100 : 0

  return (
    <div className="space-y-6 p-6">
      <div><h1 className="text-3xl font-bold">Workflow-Monitoring</h1><p className="text-muted-foreground">Ueberwachung der automatischen Beleguebergaenge</p></div>
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Ausfuehrungen</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{stats.total}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Erfolgsrate</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-green-600">{successRate.toFixed(1)}%</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Laufende Workflows</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-blue-600">{stats.running}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Fehlgeschlagen</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-red-600">{stats.failed}</div></CardContent></Card>
      </div>
      {stats.failed > 0 && <Card className="border-red-500 bg-red-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-red-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{stats.failed} Workflow(s) sind fehlgeschlagen!</span></div></CardContent></Card>}
      <Card><CardHeader><CardTitle>Workflow-Ausfuehrungen</CardTitle></CardHeader><CardContent><DataTable data={executions} columns={columns} /></CardContent></Card>
    </div>
  )
}
