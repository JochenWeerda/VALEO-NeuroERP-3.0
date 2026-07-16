import { useCallback, useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  acceptImportJob,
  listImportJobs,
  rejectImportJob,
  type ImportJob,
} from '@/lib/api/feeding-import-monitor'
import { getAxiosErrorMessage } from '@/lib/api-client'

const STATUS_LABEL: Record<string, string> = {
  validated: 'Validiert',
  quarantined: 'Quarantäne',
  accepted: 'Übernommen',
  rejected: 'Verworfen',
}

const STATUS_BADGE: Record<string, 'default' | 'secondary' | 'destructive'> = {
  validated: 'default',
  quarantined: 'destructive',
  accepted: 'secondary',
  rejected: 'secondary',
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' })
}

/** Integrationsmonitor (FEED-INT-034): Importaufträge mit Validierungsbefunden,
 * kontrollierter Übernahme und Verwerfen mit Pflicht-Begründung. */
export function ImportMonitor(): JSX.Element {
  const [jobs, setJobs] = useState<ImportJob[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [pending, setPending] = useState<Set<string>>(new Set())
  const [message, setMessage] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [rejectingId, setRejectingId] = useState<string | null>(null)
  const [reason, setReason] = useState('')

  const load = useCallback(async (): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      setJobs(await listImportJobs())
    } catch (loadError) {
      setError(getAxiosErrorMessage(loadError))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void load() }, [load])

  async function withPending(jobId: string, run: () => Promise<void>): Promise<void> {
    if (pending.has(jobId)) return
    setPending((current) => new Set(current).add(jobId))
    setActionError(null)
    setMessage(null)
    try {
      await run()
      await load()
    } catch (runError) {
      setActionError(getAxiosErrorMessage(runError))
    } finally {
      setPending((current) => {
        const next = new Set(current)
        next.delete(jobId)
        return next
      })
    }
  }

  function accept(jobId: string): void {
    void withPending(jobId, async () => {
      await acceptImportJob(jobId)
      setMessage('Import übernommen.')
    })
  }

  function confirmReject(): void {
    const jobId = rejectingId
    if (!jobId || reason.trim().length < 3) return
    void withPending(jobId, async () => {
      await rejectImportJob(jobId, reason.trim())
      setMessage('Import verworfen.')
      setRejectingId(null)
      setReason('')
    })
  }

  if (loading) {
    return <div className="h-64 animate-pulse rounded-lg bg-muted/40" aria-hidden />
  }

  if (error) {
    return (
      <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
        <p className="font-medium text-status-error">Der Integrationsmonitor konnte nicht geladen werden.</p>
        <p className="mt-1 text-muted-foreground">{error}</p>
        <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => { void load() }}>
          Erneut laden
        </Button>
      </div>
    )
  }

  return (
    <section className="space-y-4" data-testid="import-monitor">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">Integrationsmonitor</h1>
          <p className="text-sm text-muted-foreground">
            Importaufträge aus Labor, Mischtechnik und Herdenmanagement — Übernahme nur nach Validierung.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {message ? <p className="text-sm text-status-success" role="status">{message}</p> : null}
          {actionError ? <p className="text-sm text-status-error" role="alert">{actionError}</p> : null}
        </div>
      </header>

      {jobs.length === 0 ? (
        <div className="rounded-lg border bg-muted/30 p-6 text-sm text-muted-foreground" role="status">
          Keine Importaufträge vorhanden — eingehende Provider-Daten erscheinen hier zur Prüfung.
        </div>
      ) : (
        <ul className="space-y-2">
          {jobs.map((job) => {
            const externalId = String(job.mapped_excerpt?.external_id ?? '—')
            const isPending = pending.has(job.id)
            return (
              <li key={job.id} className="rounded-lg border bg-card p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Badge variant={STATUS_BADGE[job.status] ?? 'secondary'}>
                      {STATUS_LABEL[job.status] ?? job.status}
                    </Badge>
                    <span className="font-medium">{job.adapter}</span>
                    <span className="font-mono text-muted-foreground">{externalId}</span>
                    <span className="text-muted-foreground">{formatDateTime(job.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {job.status === 'validated' ? (
                      <Button type="button" size="sm" disabled={isPending} onClick={() => accept(job.id)}>
                        {isPending ? 'Übernimmt…' : 'Übernehmen'}
                      </Button>
                    ) : null}
                    {(job.status === 'validated' || job.status === 'quarantined') ? (
                      <Button type="button" size="sm" variant="outline" disabled={isPending}
                              onClick={() => { setRejectingId(job.id); setReason('') }}>
                        Verwerfen
                      </Button>
                    ) : null}
                  </div>
                </div>
                {job.findings.length > 0 ? (
                  <ul className="mt-2 space-y-1">
                    {job.findings.map((finding, index) => (
                      <li key={index} className="text-sm text-muted-foreground">
                        <Badge variant="destructive" className="mr-1.5">{finding.severity}</Badge>
                        {finding.message}
                      </li>
                    ))}
                  </ul>
                ) : null}
                {job.decision_reason ? (
                  <p className="mt-2 text-sm text-muted-foreground">
                    <span className="font-medium">Begründung: </span>{job.decision_reason}
                  </p>
                ) : null}
                {rejectingId === job.id ? (
                  <div className="mt-3 flex flex-wrap items-end gap-2 border-t pt-3">
                    <div className="grid flex-1 gap-1.5">
                      <Label htmlFor={`reject-reason-${job.id}`}>Begründung</Label>
                      <Input
                        id={`reject-reason-${job.id}`}
                        value={reason}
                        onChange={(event) => setReason(event.target.value)}
                        placeholder="Warum wird dieser Import verworfen?"
                      />
                    </div>
                    <Button type="button" variant="destructive" size="sm"
                            disabled={isPending || reason.trim().length < 3}
                            onClick={confirmReject}>
                      Verwerfen bestätigen
                    </Button>
                    <Button type="button" variant="ghost" size="sm"
                            onClick={() => { setRejectingId(null); setReason('') }}>
                      Abbrechen
                    </Button>
                  </div>
                ) : null}
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}
