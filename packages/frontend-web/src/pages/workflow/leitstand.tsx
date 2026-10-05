import { useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { Callout } from '@/components/ui/callout'
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
  if (status === 'completed') return <CheckCircle className="h-4 w-4 text-status-success" />
  if (status === 'failed') return <XCircle className="h-4 w-4 text-status-error" />
  if (status === 'blocked_external_gate') return <AlertTriangle className="h-4 w-4 text-status-warning" />
  if (status === 'running') return <Zap className="h-4 w-4 text-muted-foreground" />
  if (status === 'compensated') return <RotateCcw className="h-4 w-4 text-muted-foreground" />
  return <Clock className="h-4 w-4 text-status-warning" />
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
      <div className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
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
          <h4 className="text-sm font-semibold text-status-warning mb-2">Aktive Blocker</h4>
          <div className="space-y-2">
            {process.blockers.filter(b => !b.resolved).map(blocker => (
              <Callout key={blocker.blocker_id} variant="warning" className="rounded border p-2 text-sm">
                <div className="font-medium">{blocker.message}</div>
                {blocker.external_system && <div className="text-muted-foreground text-xs">System: {blocker.external_system}</div>}
                <div className="text-xs text-muted-foreground">Seit: {new Date(blocker.since).toLocaleString('de-DE')}</div>
              </Callout>
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
              <span className="font-mono text-primary w-28 shrink-0">{evt.kind}</span>
              <span>{evt.message}</span>
            </div>
          ))}
        </div>
      </div>

      {process.replayable && (
        <div className="border-t pt-3">
          {!showReplayForm ? (
            <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => setShowReplayForm(true)}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Replay anfordern
            </Button>
          ) : (
            <div className="space-y-2">
              <input
                className="min-h-touch w-full rounded border px-3 text-sm"
                placeholder="Begründung (Pflicht)"
                value={replayReason}
                onChange={e => setReplayReason(e.target.value)}
                aria-label="Begründung für Replay"
              />
              <div className="flex flex-wrap gap-2">
                <Button
                  className="min-h-touch touch-manipulation"
                  disabled={!replayReason.trim() || replay.isPending}
                  onClick={() => { void handleReplay() }}
                >
                  {replay.isPending ? 'Wird gesendet…' : 'Replay bestätigen'}
                </Button>
                <Button className="min-h-touch touch-manipulation" variant="ghost" onClick={() => setShowReplayForm(false)}>Abbrechen</Button>
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
        <Button className="min-h-11 touch-manipulation" variant="ghost" onClick={() => setSelectedId(row.original.process_instance_id)}>
          Detail
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Prozessleitstand</h1>
          <p className="text-sm text-muted-foreground">
            Welche Instanzen laufen, welche hängen am Gate, welche brauchen Replay.
          </p>
        </div>
        <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => { void refetch() }}>
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
              <div className="text-2xl font-bold text-primary">{summary.by_status.running ?? 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Ext. Gate blockiert</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold text-status-warning">{summary.blocked_external_gate}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-1 pt-3 px-4">
              <CardTitle className="text-xs text-muted-foreground">Replay möglich</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl font-bold text-status-warning">{summary.replayable}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Select value={statusFilter || 'all'} onValueChange={(value) => setStatusFilter(value === 'all' ? '' : value)}>
          <SelectTrigger className="min-h-touch w-full touch-manipulation sm:w-52" aria-label="Status filtern">
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

      <div className="overflow-x-auto">
      <DataTable
        columns={columns}
        data={processes}
        onRowFocus={(row: WfProcess) => setSelectedId(row.process_instance_id)}
      />
      </div>

      <Dialog open={Boolean(selectedId)} onOpenChange={open => { if (!open) setSelectedId(null) }}>
        <DialogContent className="max-h-[90vh] w-[calc(100vw-1.5rem)] max-w-2xl overflow-y-auto">
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
