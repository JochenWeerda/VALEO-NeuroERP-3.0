import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react'

type WorkflowExecution = {
  id: string
  ruleId: string
  triggerEntity: string
  triggerAction: string
  targetEntity: string
  targetAction: string
  status: 'SUCCESS' | 'FAILED' | 'PENDING' | 'RUNNING'
  startedAt: string
  completedAt?: string
  errorMessage?: string
  actorId: string
}

const mockExecutions: WorkflowExecution[] = [
  {
    id: '1',
    ruleId: '2',
    triggerEntity: 'Angebot',
    triggerAction: 'GENEHMIGT',
    targetEntity: 'Bestellung',
    targetAction: 'CREATE_FROM_ANGEBOT',
    status: 'SUCCESS',
    startedAt: '2025-10-15T10:30:00Z',
    completedAt: '2025-10-15T10:30:05Z',
    actorId: 'user123'
  },
  {
    id: '2',
    ruleId: '3',
    triggerEntity: 'Bestellung',
    triggerAction: 'FREIGEGEBEN',
    targetEntity: 'Auftragsbestaetigung',
    targetAction: 'CREATE_FROM_BESTELLUNG',
    status: 'RUNNING',
    startedAt: '2025-10-15T11:15:00Z',
    actorId: 'user456'
  },
  {
    id: '3',
    ruleId: '5',
    triggerEntity: 'Wareneingang',
    triggerAction: 'GEBUCHT',
    targetEntity: 'Rechnungseingang',
    targetAction: 'CREATE_FROM_WE',
    status: 'FAILED',
    startedAt: '2025-10-15T09:45:00Z',
    completedAt: '2025-10-15T09:45:02Z',
    errorMessage: 'Rechnungseingang bereits vorhanden',
    actorId: 'user789'
  }
]

export default function WorkflowMonitoringPage(): JSX.Element {
  const [executions] = useState<WorkflowExecution[]>(mockExecutions)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'FAILED':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'RUNNING':
        return <Clock className="h-4 w-4 text-blue-600" />
      case 'PENDING':
        return <Clock className="h-4 w-4 text-yellow-600" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      SUCCESS: 'outline' as const,
      FAILED: 'destructive' as const,
      RUNNING: 'secondary' as const,
      PENDING: 'secondary' as const
    }
    return <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>{status}</Badge>
  }

  const columns = [
    {
      key: 'startedAt' as const,
      label: 'Gestartet',
      render: (exec: WorkflowExecution) => new Date(exec.startedAt).toLocaleString('de-DE')
    },
    {
      key: 'triggerEntity' as const,
      label: 'Auslöser',
      render: (exec: WorkflowExecution) => (
        <div>
          <div className="font-medium">{exec.triggerEntity}</div>
          <div className="text-sm text-muted-foreground">{exec.triggerAction}</div>
        </div>
      )
    },
    {
      key: 'targetEntity' as const,
      label: 'Ziel',
      render: (exec: WorkflowExecution) => (
        <div>
          <div className="font-medium">{exec.targetEntity}</div>
          <div className="text-sm text-muted-foreground">{exec.targetAction}</div>
        </div>
      )
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (exec: WorkflowExecution) => (
        <div className="flex items-center gap-2">
          {getStatusIcon(exec.status)}
          {getStatusBadge(exec.status)}
        </div>
      )
    },
    {
      key: 'duration' as const,
      label: 'Dauer',
      render: (exec: WorkflowExecution) => {
        const start = new Date(exec.startedAt)
        const end = exec.completedAt ? new Date(exec.completedAt) : new Date()
        const duration = end.getTime() - start.getTime()
        const seconds = Math.floor(duration / 1000)
        return `${seconds}s`
      }
    },
    {
      key: 'errorMessage' as const,
      label: 'Fehler',
      render: (exec: WorkflowExecution) => exec.errorMessage ? (
        <div className="text-red-600 text-sm max-w-xs truncate" title={exec.errorMessage}>
          {exec.errorMessage}
        </div>
      ) : '-'
    }
  ]

  const stats = {
    total: executions.length,
    success: executions.filter(e => e.status === 'SUCCESS').length,
    failed: executions.filter(e => e.status === 'FAILED').length,
    running: executions.filter(e => e.status === 'RUNNING').length,
    pending: executions.filter(e => e.status === 'PENDING').length
  }

  const successRate = stats.total > 0 ? (stats.success / stats.total) * 100 : 0

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Workflow-Monitoring</h1>
        <p className="text-muted-foreground">Überwachung der automatischen Belegübergänge</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Ausführungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfolgsrate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{successRate.toFixed(1)}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${successRate}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Laufende Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.running}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fehlgeschlagen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          </CardContent>
        </Card>
      </div>

      {stats.failed > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{stats.failed} Workflow(s) sind fehlgeschlagen!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Workflow-Ausführungen</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable data={executions} columns={columns} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Workflow-Kette Übersicht</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-blue-600">1</span>
                </div>
                <div>
                  <div className="font-medium">Anfrage freigeben</div>
                  <div className="text-sm text-muted-foreground">Anfrage → Angebotsphase</div>
                </div>
              </div>
              <Badge variant="outline">Automatisch</Badge>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-green-600">2</span>
                </div>
                <div>
                  <div className="font-medium">Angebot genehmigen</div>
                  <div className="text-sm text-muted-foreground">Angebot → Bestellung erstellen</div>
                </div>
              </div>
              <Badge variant="outline">Automatisch</Badge>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-purple-600">3</span>
                </div>
                <div>
                  <div className="font-medium">Bestellung freigeben</div>
                  <div className="text-sm text-muted-foreground">Bestellung → AB + Avis erstellen</div>
                </div>
              </div>
              <Badge variant="outline">Automatisch</Badge>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-orange-600">4</span>
                </div>
                <div>
                  <div className="font-medium">Wareneingang buchen</div>
                  <div className="text-sm text-muted-foreground">Wareneingang → Rechnung erstellen</div>
                </div>
              </div>
              <Badge variant="outline">Automatisch</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}