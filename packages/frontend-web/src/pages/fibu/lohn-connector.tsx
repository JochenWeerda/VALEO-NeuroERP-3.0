/**
 * Lohn-Connector – Lohn-Import-Läufe (LEXWARE / externe Lohnbuchhaltung).
 * Import-Wizard (Datei-Upload → Validieren → Buchen) + Legacy: Import per Periode auslösen, Läufe-Liste.
 */

import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Building2, Play, RefreshCw, Trash2, Upload, FileUp, CheckCircle2, BookOpen, Undo2 } from 'lucide-react'
import { apiClient } from '@/lib/axios'
import { useToast } from '@/hooks/use-toast'

const CONNECTOR_BASE = '/api/v1/finance/connectors'

type ConnectorRunSummary = {
  id: string
  status: string
  counts?: { lines_total?: number; lines_ok?: number; lines_err?: number; journal_entries_created?: number }
  totals?: { debit?: string; credit?: string }
  error_summary?: string | null
  created_at: string
}

type ConnectorRunItem = {
  id: string
  line_no: number
  status: string
  validation_errors?: unknown[]
}

type LohnRun = {
  id: string
  tenant_id: string
  period: string
  source: string
  status: string
  journal_entry_count: number
  total_debit?: number
  total_credit?: number
  message?: string
  created_at: string
  updated_at: string
  created_by?: string
}

function useLohnRuns() {
  return useQuery({
    queryKey: ['finance', 'lohn-connector', 'runs'],
    queryFn: async () => {
      return await apiClient.get<LohnRun[]>('/api/v1/finance/lohn-connector/runs')
    },
  })
}

function useTriggerLohnImport() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ period, dry_run }: { period: string; dry_run: boolean }) => {
      return await apiClient.post<{ run_id: string; period: string; status: string; message: string }>(
        '/api/v1/finance/lohn-connector/runs/trigger',
        { period, dry_run }
      )
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'lohn-connector', 'runs'] })
    },
  })
}

function useDeleteLohnRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (runId: string) => {
      await apiClient.delete(`/api/v1/finance/lohn-connector/runs/${runId}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'lohn-connector', 'runs'] })
    },
  })
}

export default function LohnConnectorPage(): JSX.Element {
  const { toast } = useToast()
  const qc = useQueryClient()
  const [period, setPeriod] = useState(() => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  })
  const [dryRun, setDryRun] = useState(true)
  const { data: runs = [], isLoading, refetch } = useLohnRuns()
  const trigger = useTriggerLohnImport()
  const deleteRun = useDeleteLohnRun()

  const handleTrigger = () => {
    trigger.mutate(
      { period, dry_run: dryRun },
      {
        onSuccess: (data) => {
          toast({ title: 'Lohn-Import', description: data.message })
        },
        onError: (e: Error) => {
          toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
        },
      }
    )
  }

  const handleDelete = (id: string) => {
    if (!confirm('Diesen Lohn-Import-Lauf wirklich löschen?')) return
    deleteRun.mutate(id, {
      onSuccess: () => toast({ title: 'Gelöscht', description: 'Lauf entfernt.' }),
      onError: (e: Error) => toast({ title: 'Fehler', description: e.message, variant: 'destructive' }),
    })
  }

  // ---------- Import-Wizard (FIBU Connector API PAYROLL) ----------
  const [importRunId, setImportRunId] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: importRun, refetch: refetchRun } = useQuery({
    queryKey: ['finance', 'connectors', 'imports', importRunId],
    queryFn: async () => {
      return await apiClient.get<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}`)
    },
    enabled: !!importRunId,
  })

  const { data: runItems } = useQuery({
    queryKey: ['finance', 'connectors', 'imports', importRunId, 'items'],
    queryFn: async () => {
      return await apiClient.get<ConnectorRunItem[]>(`${CONNECTOR_BASE}/imports/${importRunId}/items`, {
        params: { only_errors: true, limit: 50 },
      })
    },
    enabled: !!importRunId,
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      return await apiClient.post<{ run_id: string; status: string; message: string }>(
        `${CONNECTOR_BASE}/PAYROLL/imports`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    },
    onSuccess: (data) => {
      setImportRunId(data.run_id)
      qc.invalidateQueries({ queryKey: ['finance', 'connectors', 'imports', data.run_id] })
      toast({ title: 'Upload', description: data.message })
    },
    onError: (e: Error) => {
      toast({ title: 'Upload fehlgeschlagen', description: e.message, variant: 'destructive' })
    },
  })

  const validateMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/validate`)
      refetchRun()
    },
    onSuccess: () => toast({ title: 'Validierung', description: 'Lauf wurde validiert.' }),
    onError: (e: Error) => toast({ title: 'Validierung fehlgeschlagen', description: e.message, variant: 'destructive' }),
  })

  const postMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/post`)
      refetchRun()
    },
    onSuccess: () => toast({ title: 'Buchung', description: 'Buchungen wurden ins Journal übernommen.' }),
    onError: (e: Error) => toast({ title: 'Buchung fehlgeschlagen', description: e.message, variant: 'destructive' }),
  })

  const cancelMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/cancel`)
      refetchRun()
    },
    onSuccess: () => toast({ title: 'Abgebrochen', description: 'Import-Lauf wurde abgebrochen.' }),
    onError: (e: Error) => toast({ title: 'Fehler', description: e.message, variant: 'destructive' }),
  })

  const reverseMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/reverse`)
      refetchRun()
    },
    onSuccess: () => toast({ title: 'Storno', description: 'Gegenbuchungen wurden erzeugt.' }),
    onError: (e: Error) => toast({ title: 'Storno fehlgeschlagen', description: e.message, variant: 'destructive' }),
  })

  const canValidate = importRun && ['DRAFT', 'PARSED'].includes(importRun.status)
  const canPost = importRun && importRun.status === 'VALIDATED'
  const canCancel = importRun && ['DRAFT', 'PARSED', 'VALIDATED'].includes(importRun.status)
  const canReverse = importRun && importRun.status === 'POSTED'

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Building2 className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Lohn-Connector</h1>
          <p className="text-muted-foreground text-sm">Lohnbuchungen aus Lohnbuchhaltung (LEXWARE o. ä.) importieren</p>
        </div>
      </div>

      {/* Import-Wizard: Datei-Upload → Validieren → Buchen */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Import-Wizard (Datei-Upload)
          </CardTitle>
          <CardDescription>
            CSV-Datei mit Lohnbuchungen hochladen, prüfen, validieren und ins Journal buchen.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-end gap-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.txt"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0]
                setSelectedFile(f ?? null)
                if (!f) setImportRunId(null)
              }}
            />
            <Button variant="outline" onClick={() => fileInputRef.current?.click()} className="gap-2">
              <FileUp className="h-4 w-4" /> Datei wählen
            </Button>
            {selectedFile && <span className="text-sm text-muted-foreground">{selectedFile.name}</span>}
            <Button
              disabled={!selectedFile || uploadMutation.isPending}
              onClick={() => selectedFile && uploadMutation.mutate(selectedFile)}
              className="gap-2"
            >
              <Upload className="h-4 w-4" /> Hochladen & Parsen
            </Button>
          </div>
          {importRun && (
            <div className="rounded-lg border bg-muted/30 p-4 space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium">Lauf:</span>
                <Badge variant="outline">{importRun.status}</Badge>
                <span className="text-xs text-muted-foreground font-mono">{importRun.id.slice(0, 8)}…</span>
              </div>
              {importRun.counts && (
                <div className="text-sm text-muted-foreground">
                  Zeilen: {importRun.counts.lines_total ?? 0} gesamt, {importRun.counts.lines_ok ?? 0} OK, {importRun.counts.lines_err ?? 0} Fehler
                  {importRun.counts.journal_entries_created != null && ` · Gebucht: ${importRun.counts.journal_entries_created} Belege`}
                </div>
              )}
              {importRun.totals && (
                <div className="text-sm">Soll: {importRun.totals.debit ?? '–'} · Haben: {importRun.totals.credit ?? '–'}</div>
              )}
              {importRun.error_summary && <p className="text-sm text-destructive">{importRun.error_summary}</p>}
              {runItems && runItems.length > 0 && (
                <details className="text-sm">
                  <summary>Fehlerzeilen ({runItems.length})</summary>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {runItems.slice(0, 20).map((it: ConnectorRunItem) => (
                      <li key={it.id}>Zeile {it.line_no}: {it.validation_errors?.toString() ?? it.status}</li>
                    ))}
                    {runItems.length > 20 && <li>… und {runItems.length - 20} weitere</li>}
                  </ul>
                </details>
              )}
              <div className="flex flex-wrap gap-2 pt-2">
                {canValidate && (
                  <Button variant="outline" size="sm" onClick={() => validateMutation.mutate()} disabled={validateMutation.isPending} className="gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Validieren
                  </Button>
                )}
                {canPost && (
                  <Button size="sm" onClick={() => postMutation.mutate()} disabled={postMutation.isPending} className="gap-1">
                    <BookOpen className="h-3 w-3" /> Buchen
                  </Button>
                )}
                {canCancel && (
                  <Button variant="outline" size="sm" onClick={() => cancelMutation.mutate()} disabled={cancelMutation.isPending}>Abbrechen</Button>
                )}
                {canReverse && (
                  <Button variant="outline" size="sm" onClick={() => reverseMutation.mutate()} disabled={reverseMutation.isPending} className="gap-1">
                    <Undo2 className="h-3 w-3" /> Stornieren
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Import auslösen (Legacy)</CardTitle>
          <CardDescription>Periode angeben und Import starten – erzeugt einen Lauf in der alten API.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="space-y-2">
            <Label>Periode (YYYY-MM)</Label>
            <Input
              type="month"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-40"
            />
          </div>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} />
            <span className="text-sm">Trockenlauf (keine Buchungen)</span>
          </label>
          <Button onClick={handleTrigger} disabled={trigger.isPending} className="gap-2">
            <Play className="h-4 w-4" /> Import starten
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Import-Läufe</CardTitle>
          <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading} className="gap-1">
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} /> Aktualisieren
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Lade …</p>
          ) : runs.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch keine Import-Läufe. Starten Sie einen Import oben.</p>
          ) : (
            <div className="rounded-md border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-muted/50 border-b">
                    <th className="text-left p-2">Periode</th>
                    <th className="text-left p-2">Quelle</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-right p-2">Buchungen</th>
                    <th className="text-left p-2">Erstellt</th>
                    <th className="w-20" />
                  </tr>
                </thead>
                <tbody>
                  {runs.map((r: LohnRun) => (
                    <tr key={r.id} className="border-b last:border-0">
                      <td className="p-2">{r.period}</td>
                      <td className="p-2">{r.source}</td>
                      <td className="p-2">
                        <Badge variant={r.status === 'completed' ? 'default' : 'secondary'}>{r.status}</Badge>
                      </td>
                      <td className="p-2 text-right tabular-nums">{r.journal_entry_count}</td>
                      <td className="p-2 text-muted-foreground">
                        {new Date(r.created_at).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })}
                      </td>
                      <td className="p-2">
                        {r.status === 'pending' && (
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(r.id)} disabled={deleteRun.isPending}>
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {runs.some((r: LohnRun) => Boolean(r.message)) && (
            <p className="mt-2 text-xs text-muted-foreground">
            {runs.find((r: LohnRun) => r.message)?.message}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
