import { useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, CheckCircle, Clock, RefreshCw, RotateCcw, XCircle, Zap } from 'lucide-react'
import {
  useWfSummary,
  useWfProcesses,
  useWfProcess,
  useWfReplayRequest,
  wfStatusLabel,
  wfStatusVariant,
  type WfProcess,
  type WfProcessStatus,
} from '@/lib/api/workflow-cockpit'

const STATUS_OPTIONS: Array<{ value: string; label: string }> = [
  { value: '', label: 'Alle Status' },
  { value: 'pending', label: 'Ausstehend' },
  { value: 'running', label: 'Läuft' },
  { value: 'blocked_external_gate', label: 'Ext. Gate blockiert' },
  { value: 'failed', label: 'Fehlgeschlagen' },
  { value: 'completed', label: 'Abgeschlossen' },
  { value: 'compensated', label: 'Kompensiert' },
]

function StatusIcon({ status }: { status: string }) {
  if (status === 'completed') return <CheckCircle className="h-4 w-4 text-green-600" />
  if (status === 'failed') return <XCircle className="h-4 w-4 text-red-600" />
  if (status === 'blocked_external_gate') return <AlertTriangle className="h-4 w-4 text-orange-500" />
  if (status === 'running') return <Zap className="h-4 w-4 text-blue-600" />
  if (status === 'compensated') return <RotateCcw className="h-4 w-4 text-gray-500" />
  return <Clock className="h-4 w-4 text-yellow-600" />
}

function ProcessDetail({ processInstanceId, onClose }: { processInstanceId: string; onClose: () => void }) {
  const { data: process, isLoading } = useWfProcess(processInstanceId)
  const replay = useWfReplayRequest()
  const { toast } = useToast()
  const [replayReason, setReplayReason] = useState('')
  const [showReplayForm, setShowReplayForm] = useState(false)

  async function handleReplay() {
    if (!replayReason.trim()) return
    try {
      await replay.mutateAsync({
        processInstanceId,
        requestedBy: 'current-user',
        reason: replayReason,
      })
      toast({ title: 'Replay-Anforderung registriert' })
      setShowReplayForm(false)
      setReplayReason('')
    } catch {
      toast({ title: 'Replay fehlgeschlagen', variant: 'destructive' })
    }
  }

  if (isLoading || !process) return <div className="p-4 text-sm text-muted-foreground">Lädt…</div>

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div><span className="text-muted-foreground">Prozess-Key:</span> <strong>{process.process_key}</strong></div>
        <div><span className="text-muted-foreground">Status:</span> <Badge variant={wfStatusVariant(process.status)}>{wfStatusLabel(process.status)}</Badge></div>
        <div><span className="text-muted-foreground">Correlation-ID:</span> <code className="text-xs">{process.correlation_id}</code></div>
        <div><span className="text-muted-foreground">Aktueller Schritt:</span> {process.current_step ?? '—'}</div>
        {process.business_object_ref && (
          <div className="col-span-2"><span className="text-muted-foreground">Objekt-Ref:</span> {process.business_object_ref}</div>
        )}
      </div>

      {process.blockers.filter(b => !b.resolved).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-orange-600 mb-2">Aktive Blocker</h4>
          <div className="space-y-2">
            {process.blockers.filter(b => !b.resolved).map(blocker => (
              <div key={blocker.blocker_id} className="rounded border border-orange-200 bg-orange-50 p-2 text-sm">
                <div className="font-medium">{blocker.message}</div>
                {blocker.external_system && <div className="text-muted-foreground text-xs">System: {blocker.external_system}</div>}
                <div className="text-xs text-muted-foreground">Seit: {new Date(blocker.since).toLocaleString('de-DE')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h4 className="text-sm font-semibold mb-2">Event-Kette ({process.events.length})</h4>
        <div className="max-h-56 overflow-y-auto space-y-1 border rounded p-2">
          {process.events.length === 0 && <div className="text-xs text-muted-foreground">Keine Events</div>}
          {process.events.map(evt => (
            <div key={evt.event_id} className="flex items-start gap-2 text-xs py-1 border-b last:border-0">
              <span className="text-muted-foreground w-32 shrink-0">{new Date(evt.occurred_at).toLocaleString('de-DE')}</span>
              <span className="font-mono text-blue-700 w-28 shrink-0">{evt.kind}</span>
              <span>{evt.message}</span>
            </div>
          ))}
        </div>
      </div>

      {process.replayable && (
        <div className="border-t pt-3">
          {!showReplayForm ? (
            <Button size="sm" variant="outline" onClick={() => setShowReplayForm(true)}>
              <RotateCcw className="mr-2 h-3 w-3" />
              Replay anfordern
            </Button>
          ) : (
            <div className="space-y-2">
              <input
                className="w-full rounded border px-2 py-1 text-sm"
                placeholder="Begründung (Pflicht)"
                value={replayReason}
                onChange={e => setReplayReason(e.target.value)}
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  disabled={!replayReason.trim() || replay.isPending}
                  onClick={() => { void handleReplay() }}
                >
                  {replay.isPending ? 'Wird gesendet…' : 'Replay bestätigen'}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setShowReplayForm(false)}>Abbrechen</Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function WorkflowLeitstandPage(): JSX.Element {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data: summary } = useWfSummary()
  const { data: processes = [], isLoading, refetch } = useWfProcesses(statusFilter || undefined)

  const columns = [
    {
      header: 'Status',
      accessorKey: 'status',
      cell: ({ row }: { row: { original: WfProcess } }) => (
        <div className="flex items-center gap-2">
          <StatusIcon status={row.original.status} />
          <Badge variant={wfStatusVariant(row.original.status)} className="text-xs">
            {wfStatusLabel(row.original.status)}
          </Badge>
        </div>
      ),
    },
    { header: 'Prozess-Key', accessorKey: 'process_key' },
    {
      header: 'Objekt-Ref',
      accessorKey: 'business_object_ref',
      cell: ({ row }: { row: { original: WfProcess } }) => row.original.business_object_ref ?? '—',
    },
    {
      header: 'Schritt',
      accessorKey: 'current_step',
      cell: ({ row }: { row: { original: WfProcess } }) => row.original.current_step ?? '—',
    },
    {
      header: 'Blocker',
      accessorKey: 'active_blocker_count',
      cell: ({ row }: { row: { original: WfProcess } }) =>
        row.original.active_blocker_count > 0 ? (
          <Badge variant="destructive">{row.original.active_blocker_count}</Badge>
        ) : '—',
    },
    {
      header: 'Replay',
      accessorKey: 'replayable',
      cell: ({ row }: { row: { original: WfProcess } }) =>
        row.original.replayable ? <Badge variant="outline">Ja</Badge> : '—',
    },
    {
      header: 'Aktualisiert',
      accessorKey: 'updated_at',
      cell: ({ row }: { row: { original: WfProcess } }) =>
        new Date(row.original.updated_at).toLocaleString('de-DE'),
    },
    {
      header: '',
      accessorKey: 'process_instance_id',
      cell: ({ row }: { row: { original: WfProcess } }) => (
        <Button size="sm" variant="ghost" onClick={() => setSelectedId(row.original.process_instance_id)}>
          Detail
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Workflow-Prozessleitstand</h1>
          <p className="text-sm text-muted-foreground">
            Operative Sicht auf Prozessinstanzen, externe Gate-Blocker und Replay-Anforderungen
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => { void refetch() }}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Aktualisieren
        </Button>
      </div>

      {summary && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Card>
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Gesamt</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold">{summary.total_processes}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Läuft</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold text-blue-600">{summary.by_status.running ?? 0}</div>
            </CardContent>
          </Card>
          <Card className="border-orange-200">
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Ext. Gate blockiert</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold text-orange-600">{summary.blocked_external_gate}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Replay möglich</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold text-yellow-600">{summary.replayable}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="flex items-center gap-3">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-52">
            <SelectValue placeholder="Status filtern" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map(opt => (
              <SelectItem key={opt.value || 'all'} value={opt.value || 'all'}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {isLoading ? 'Lädt…' : `${processes.length} Prozess${processes.length !== 1 ? 'e' : ''}`}
        </span>
      </div>

      <DataTable
        columns={columns}
        data={processes}
        onRowFocus={(row: WfProcess) => setSelectedId(row.process_instance_id)}
      />

      <Dialog open={Boolean(selectedId)} onOpenChange={open => { if (!open) setSelectedId(null) }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Prozessinstanz-Detail</DialogTitle>
          </DialogHeader>
          {selectedId && (
            <ProcessDetail processInstanceId={selectedId} onClose={() => setSelectedId(null)} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
