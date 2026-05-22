/**
 * VALEO Suite Anlagen (Asset Ledger) – Zentrale Anlagenbuchhaltung.
 * Bündelt: Anlagenverwaltung (Stammdaten, AfA, Buchwerte), Import-Wizard und Connector-Konfiguration.
 */

import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Building2, LayoutGrid, Save, RefreshCw, ArrowRightLeft, FileUp, Upload, CheckCircle2, BookOpen, Undo2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { useFibuCockpit } from '@/lib/api/fibu'
import { normalizeOperationalStatus } from '@/lib/operational-status'

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
  payload?: Record<string, unknown>
  validation_errors?: unknown[]
}

type ConnectorConfig = {
  id: string
  tenant_id: string
  connector_code: string
  name?: string
  config_json: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

function useAssetLedgerConfig() {
  return useQuery({
    queryKey: ['finance', 'asset-ledger-connector', 'config'],
    queryFn: async () => {
      return await apiClient.get<ConnectorConfig | null>('/api/v1/finance/asset-ledger-connector/config')
    },
  })
}

export default function AnlagenSuitePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: fibuCockpit } = useFibuCockpit()
  const qc = useQueryClient()
  const { data: config, isLoading } = useAssetLedgerConfig()
  const [name, setName] = useState('VALEO Suite Anlagen (Asset Ledger)')
  const [endpoint, setEndpoint] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    if (config) {
      setName(config.name ?? 'VALEO Suite Anlagen (Asset Ledger)')
      setIsActive(config.is_active)
      const c = config.config_json as Record<string, string>
      setEndpoint(c?.endpoint_url ?? '')
    }
  }, [config])

  const saveMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put('/api/v1/finance/asset-ledger-connector/config', {
        name,
        config_json: { endpoint_url: endpoint },
        is_active: isActive,
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'asset-ledger-connector', 'config'] })
      toast({ title: 'Gespeichert', description: 'Konfiguration wurde gespeichert.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
    },
  })

  const syncMutation = useMutation({
    mutationFn: async (direction: 'export' | 'import') => {
      return await apiClient.post<{ success: boolean; message: string }>('/api/v1/finance/asset-ledger-connector/sync', {
        direction,
        options: {},
      })
    },
    onMutate: () => setSyncing(true),
    onSettled: () => setSyncing(false),
    onSuccess: (data) => {
      toast({ title: 'Sync', description: data.message })
    },
    onError: (e: Error) => {
      toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
    },
  })

  // ---------- Import-Wizard (FIBU Connector API) ----------
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
        `${CONNECTOR_BASE}/ASSET_LEDGER/imports`,
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
      return await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/validate`)
    },
    onSuccess: () => {
      refetchRun()
      toast({ title: 'Validierung', description: 'Lauf wurde validiert.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Validierung fehlgeschlagen', description: e.message, variant: 'destructive' })
    },
  })

  const postMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/post`)
    },
    onSuccess: () => {
      refetchRun()
      toast({ title: 'Buchung', description: 'Buchungen wurden ins Journal übernommen.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Buchung fehlgeschlagen', description: e.message, variant: 'destructive' })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/cancel`)
    },
    onSuccess: () => {
      refetchRun()
      toast({ title: 'Abgebrochen', description: 'Import-Lauf wurde abgebrochen.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
    },
  })

  const reverseMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.post<ConnectorRunSummary>(`${CONNECTOR_BASE}/imports/${importRunId}/reverse`)
    },
    onSuccess: () => {
      refetchRun()
      toast({ title: 'Storno', description: 'Gegenbuchungen wurden erzeugt.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Storno fehlgeschlagen', description: e.message, variant: 'destructive' })
    },
  })

  const canValidate = importRun && ['DRAFT', 'PARSED'].includes(importRun.status)
  const canPost = importRun && importRun.status === 'VALIDATED'
  const canCancel = importRun && ['DRAFT', 'PARSED', 'VALIDATED'].includes(importRun.status)
  const canReverse = importRun && importRun.status === 'POSTED'
  const operationalStatus = normalizeOperationalStatus(
    importRun?.status === 'POSTED'
      ? 'abgeschlossen'
      : importRun?.status === 'VALIDATED'
        ? 'wartet_auf_mensch'
        : importRun?.status
          ? 'in_pruefung'
          : 'offen'
  )
  const contextSections = [
    {
      title: 'Anlagen & Connector',
      items: [
        { label: 'Connector aktiv', value: isActive ? 'Ja' : 'Nein' },
        { label: 'Importlauf', value: importRun?.id || 'Kein aktiver Lauf' },
        { label: 'Status', value: importRun?.status || 'Kein aktiver Lauf' },
      ],
    },
    {
      title: 'Revisionslage',
      items: [
        { label: 'Connector-Profile', value: String(fibuCockpit.master_data.connector_profile_count) },
        { label: 'Exportlaeufe', value: String(fibuCockpit.revision.export_runs) },
        { label: 'Jahreswechsel', value: fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klaerungen' },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: canPost ? 'Importlauf buchen' : canValidate ? 'Importlauf validieren' : 'Anlagenraum oder Connector pruefen' },
        { label: 'Blocker', value: importRun?.error_summary || 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Anlagen-Suite geladen', detail: name },
    importRun ? { label: 'Importlauf aktiv', detail: `${importRun.status} / ${importRun.id}` } : null,
    selectedFile ? { label: 'Datei bereit', detail: selectedFile.name } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto space-y-8">
      <OperationalCaseHeader
        title="VALEO Suite Anlagen"
        description="Anlagenbuchhaltung mit Connector-, Import- und Revisionskontext in einem kompakten Steuerungsbild."
        status={operationalStatus}
        owner="Anlagenbuchhaltung"
        blocker={importRun?.error_summary || null}
        nextAction={canPost ? 'Importlauf buchen' : canValidate ? 'Importlauf validieren' : 'Anlagenraum oder Connector pruefen'}
        caseLabel="Asset Ledger"
        tags={['FIBU', 'Anlagen']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Anlagenverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center gap-3">
        <LayoutGrid className="h-9 w-9 text-primary" />
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">VALEO Suite Anlagen (Asset Ledger)</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Anlagenbuchhaltung: Stammdaten, Abschreibungen, Umbuchungen, Abgänge und Import von Anlagenbuchungen
          </p>
        </div>
      </div>

      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle>FIBU-Stammdaten und Revision</CardTitle>
          <CardDescription>
            Connector-Profile, Exportpfade und Jahreswechsel-Readiness für die exklusive FIBU-Tiefe.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <div><div className="text-xs text-muted-foreground">Connector-Profile</div><div className="text-2xl font-semibold">{fibuCockpit.master_data.connector_profile_count}</div></div>
          <div><div className="text-xs text-muted-foreground">Exportläufe</div><div className="text-2xl font-semibold">{fibuCockpit.revision.export_runs}</div></div>
          <div><div className="text-xs text-muted-foreground">Journal zuletzt</div><div className="text-sm font-semibold">{fibuCockpit.revision.last_entry_date ?? 'n/a'}</div></div>
          <div><div className="text-xs text-muted-foreground">Jahreswechsel</div><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></div>
        </CardContent>
      </Card>

      {/* Anlagenverwaltung – zentrale Karte */}
      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Anlagenverwaltung
          </CardTitle>
          <CardDescription>
            Anlagevermögen verwalten: Anlagennummer, Bezeichnung, Anschaffungskosten, AfA-Satz, kumulierte Abschreibungen, Buchwert. Neue Anlage anlegen oder bestehende bearbeiten.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <Button onClick={() => navigate('/fibu/anlagen')} className="gap-2">
            <Building2 className="h-4 w-4" />
            Zur Anlagenverwaltung
          </Button>
          <Button variant="outline" onClick={() => navigate('/fibu/anlage/neu')} className="gap-2">
            <FileUp className="h-4 w-4" />
            Neue Anlage anlegen
          </Button>
        </CardContent>
      </Card>

      {/* Import-Wizard: Upload → Validieren → Buchen */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Import-Wizard (Anlagenbuchungen)
          </CardTitle>
          <CardDescription>
            CSV-Datei hochladen, Ergebnis prüfen, validieren und ins Journal buchen. Ein Lauf kann bis nach der Validierung abgebrochen werden; nach dem Buchen nur Storno (Gegenbuchungen).
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
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              className="gap-2"
            >
              <FileUp className="h-4 w-4" />
              Datei wählen
            </Button>
            {selectedFile && (
              <span className="text-sm text-muted-foreground">{selectedFile.name}</span>
            )}
            <Button
              disabled={!selectedFile || uploadMutation.isPending}
              onClick={() => selectedFile && uploadMutation.mutate(selectedFile)}
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              Hochladen & Parsen
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
                <div className="text-sm">
                  Soll: {importRun.totals.debit ?? '–'} · Haben: {importRun.totals.credit ?? '–'}
                </div>
              )}
              {importRun.error_summary && (
                <p className="text-sm text-destructive">{importRun.error_summary}</p>
              )}
              {runItems && runItems.length > 0 && (
                <details className="text-sm">
                  <summary>Fehlerzeilen anzeigen ({runItems.length})</summary>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {runItems.slice(0, 20).map((it: ConnectorRunItem) => (
                      <li key={it.id}>
                        Zeile {it.line_no}: {it.validation_errors?.toString() ?? it.status}
                      </li>
                    ))}
                    {runItems.length > 20 && <li>… und {runItems.length - 20} weitere</li>}
                  </ul>
                </details>
              )}
              <div className="flex flex-wrap gap-2 pt-2">
                {canValidate && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => validateMutation.mutate()}
                    disabled={validateMutation.isPending}
                    className="gap-1"
                  >
                    <CheckCircle2 className="h-3 w-3" /> Validieren
                  </Button>
                )}
                {canPost && (
                  <Button
                    size="sm"
                    onClick={() => postMutation.mutate()}
                    disabled={postMutation.isPending}
                    className="gap-1"
                  >
                    <BookOpen className="h-3 w-3" /> Buchen
                  </Button>
                )}
                {canCancel && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    className="gap-1"
                  >
                    Abbrechen
                  </Button>
                )}
                {canReverse && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => reverseMutation.mutate()}
                    disabled={reverseMutation.isPending}
                    className="gap-1"
                  >
                    <Undo2 className="h-3 w-3" /> Stornieren
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Import / Connector (Konfiguration) */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Import & Connector (Konfiguration)</CardTitle>
          <CardDescription>
            Konfiguration und Sync fuer den Import von Anlagen- und Abschreibungsbuchungen (z. B. aus externen Systemen). Nutzen Sie alternativ den einheitlichen FIBU-Connector-Workflow im Schnittstellen-Center fuer Upload, Pruefung und Buchung.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Bezeichnung</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="VALEO Suite Anlagen (Asset Ledger)" />
          </div>
          <div className="space-y-2">
            <Label>Endpoint-URL (optional)</Label>
            <Input value={endpoint} onChange={(e) => setEndpoint(e.target.value)} placeholder="https://…" />
          </div>
          <div className="flex items-center justify-between">
            <Label>Connector aktiv</Label>
            <Switch checked={isActive} onCheckedChange={setIsActive} />
          </div>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="gap-2">
              <Save className="h-4 w-4" /> Speichern
            </Button>
            <Button
              variant="outline"
              onClick={() => syncMutation.mutate('export')}
              disabled={syncing || isLoading || !config?.is_active}
              className="gap-2"
            >
              <ArrowRightLeft className="h-4 w-4" /> Export
            </Button>
            <Button
              variant="outline"
              onClick={() => syncMutation.mutate('import')}
              disabled={syncing || isLoading || !config?.is_active}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" /> Import
            </Button>
          </div>
        </CardContent>
      </Card>

      <p className="text-sm text-muted-foreground">
        Gebuchte Belege aus dem Import finden Sie im{' '}
        <Link to="/fibu/buchungsjournal" className="text-primary underline hover:no-underline">
          Buchungsjournal
        </Link>
        {importRunId && importRun?.status === 'POSTED' && (
          <> (Filter: Referenz = <span className="font-mono">{importRunId.slice(0, 8)}…</span>)</>
        )}.
      </p>

      {!config && !isLoading && (
        <p className="text-sm text-muted-foreground">
          Noch keine Konfiguration vorhanden. Bezeichnung setzen und „Speichern“ klicken, um eine Konfiguration anzulegen.
        </p>
      )}
    </div>
  )
}
