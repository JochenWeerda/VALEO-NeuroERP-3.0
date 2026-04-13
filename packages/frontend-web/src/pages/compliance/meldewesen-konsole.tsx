import React, { useCallback, useMemo, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { NativeSelect } from "@/components/ui/native-select"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CalendarDays, Play, Save, ShieldAlert, Upload, Download, Trash2, Plus, FileText, Clock } from "lucide-react"
import { ErrorState } from "@/components/ErrorState"
import { KeyboardShortcutBar } from "@/components/keyboard/KeyboardShortcutBar"
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"
import { AgentProcessPanel } from "@/components/agent"
import { summarizeMeldewesenFeedback } from "@/lib/domain-depth"
import { OperationalCaseHeader } from "@/components/workflow/OperationalCaseHeader"
import { normalizeOperationalStatus } from "@/lib/operational-status"
import {
  listConnectors,
  listReportingUnits,
  listSchedules,
  listJobs,
  getJobArtifacts,
  runJob,
  createConnector,
  updateConnector,
  deleteConnector,
  createReportingUnit,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  type ConnectorApi,
  type ReportingUnitApi,
  type ScheduleApi,
  type JobApi,
} from "@/lib/api/meldewesen"
import { useDokumenteAblage, useWiegungen } from "@/lib/api/betrieb"
import { useWarteschlange } from "@/lib/api/inventory"
import { useFrachtbriefe } from "@/lib/api/misc-modules"

type ReportType = "INTRASTAT_DE" | "BLE_MVO" | "ZOLL_ATLAS_PROVIDER" | "EUDR_DDS"
type TransportKind = "file-drop" | "https" | "sftp" | "email" | "provider"

type Connector = {
  id: string
  name: string
  enabled: boolean
  transport: TransportKind
  supportedReportTypes: ReportType[]
  secrets: Record<string, string | undefined>
  notes?: string
}

type ReportingUnit = {
  id: string
  name: string
  countryIso2: string
  vatId?: string
  intrastatEnabled: boolean
  bleMvoEnabled: boolean
  eudrEnabled: boolean
}

type Schedule = {
  id: string
  enabled: boolean
  name: string
  reportType: ReportType
  reportingUnitId: string
  connectorId: string
  cadence: "monthly" | "quarterly" | "yearly"
  dayOfMonth: number
  timeHHmm: string
  leadDays: number
  gateByThreshold: boolean
  thresholdKey?: "INTRASTAT_ARRIVAL" | "INTRASTAT_DISPATCH"
  outputFormats: Array<"csv" | "xml" | "json">
  jobParamsJson: string
}

type JobRun = {
  id: string
  createdAt: string
  scheduleId?: string
  reportType: ReportType
  reportingUnitId: string
  connectorId: string
  status: "queued" | "running" | "success" | "failed"
  message?: string
  artifacts?: Array<{ name: string; mime: string; sha256: string }>
}

function uid(prefix: string) {
  return `${prefix}_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`
}

function safeJsonParse<T>(s: string, fallback: T): T {
  try {
    return JSON.parse(s) as T
  } catch {
    return fallback
  }
}

function downloadText(filename: string, text: string, mime = "application/json") {
  const blob = new Blob([text], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function nextRunsPreview(s: Schedule) {
  const out: string[] = []
  const now = new Date()
  for (let i = 0; i < 3; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, s.dayOfMonth)
    const [hh, mm] = s.timeHHmm.split(":").map((x) => Number(x))
    d.setHours(hh || 0, mm || 0, 0, 0)
    const trigger = new Date(d.getTime())
    trigger.setDate(trigger.getDate() - (s.leadDays || 0))
    out.push(trigger.toLocaleString())
  }
  return out
}

// â”€â”€ API â†” Frontend Mappers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function connectorFromApi(a: ConnectorApi): Connector {
  const cfg = (a.config_json ?? {}) as Record<string, unknown>
  return {
    id: a.id,
    name: a.display_name ?? a.connector_key,
    enabled: a.is_active,
    transport: (a.connector_type as TransportKind) || "file-drop",
    supportedReportTypes: (cfg.supportedReportTypes as ReportType[]) ?? ["INTRASTAT_DE"],
    secrets: (cfg.secrets as Record<string, string>) ?? {},
    notes: cfg.notes as string | undefined,
  }
}

function connectorToApiCreate(c: Connector): Parameters<typeof createConnector>[0] {
  return {
    connector_key: c.id || uid("conn"),
    connector_type: c.transport,
    display_name: c.name,
    config_json: {
      supportedReportTypes: c.supportedReportTypes,
      secrets: c.secrets,
      notes: c.notes,
    },
    is_active: c.enabled,
  }
}

function connectorToApiUpdate(c: Connector): Parameters<typeof updateConnector>[1] {
  return {
    display_name: c.name,
    config_json: { supportedReportTypes: c.supportedReportTypes, secrets: c.secrets, notes: c.notes },
    is_active: c.enabled,
  }
}

function unitFromApi(a: ReportingUnitApi): ReportingUnit {
  const cfg = (a.config_json ?? {}) as Record<string, unknown>
  return {
    id: a.id,
    name: a.display_name,
    countryIso2: (cfg.countryIso2 as string) ?? "DE",
    vatId: cfg.vatId as string | undefined,
    intrastatEnabled: (cfg.intrastatEnabled as boolean) ?? true,
    bleMvoEnabled: (cfg.bleMvoEnabled as boolean) ?? false,
    eudrEnabled: (cfg.eudrEnabled as boolean) ?? false,
  }
}

function unitToApiCreate(u: ReportingUnit): Parameters<typeof createReportingUnit>[0] {
  return {
    unit_key: u.id || uid("unit"),
    display_name: u.name,
    config_json: {
      countryIso2: u.countryIso2,
      vatId: u.vatId,
      intrastatEnabled: u.intrastatEnabled,
      bleMvoEnabled: u.bleMvoEnabled,
      eudrEnabled: u.eudrEnabled,
    },
    is_active: true,
  }
}

function scheduleFromApi(a: ScheduleApi): Schedule {
  const cfg = (a.config_json ?? {}) as Record<string, unknown>
  const fmts = a.output_format ? (a.output_format.split(",") as Array<"csv" | "xml" | "json">) : ["csv"]
  return {
    id: a.id,
    enabled: a.is_active,
    name: a.display_name,
    reportType: (cfg.reportType as ReportType) ?? "INTRASTAT_DE",
    reportingUnitId: a.reporting_unit_id ?? "",
    connectorId: (cfg.connectorId as string) ?? "",
    cadence: (cfg.cadence as Schedule["cadence"]) ?? "monthly",
    dayOfMonth: (cfg.dayOfMonth as number) ?? 20,
    timeHHmm: (cfg.timeHHmm as string) ?? "09:00",
    leadDays: a.lead_days ?? 5,
    gateByThreshold: (cfg.gateByThreshold as boolean) ?? false,
    thresholdKey: cfg.thresholdKey as Schedule["thresholdKey"],
    outputFormats: (cfg.outputFormats as Schedule["outputFormats"]) ?? fmts,
    jobParamsJson: typeof cfg.jobParamsJson === "string" ? cfg.jobParamsJson : JSON.stringify(cfg.jobParamsJson ?? {}, null, 2),
  }
}

function scheduleToApiCreate(s: Schedule): Parameters<typeof createSchedule>[0] {
  return {
    schedule_key: s.id || uid("sch"),
    display_name: s.name,
    reporting_unit_id: s.reportingUnitId || undefined,
    lead_days: s.leadDays,
    output_format: s.outputFormats.join(","),
    config_json: {
      reportType: s.reportType,
      connectorId: s.connectorId,
      cadence: s.cadence,
      dayOfMonth: s.dayOfMonth,
      timeHHmm: s.timeHHmm,
      gateByThreshold: s.gateByThreshold,
      thresholdKey: s.thresholdKey,
      outputFormats: s.outputFormats,
      jobParamsJson: s.jobParamsJson,
    },
    is_active: s.enabled,
  }
}

function scheduleToApiUpdate(s: Schedule): Parameters<typeof updateSchedule>[1] {
  return {
    display_name: s.name,
    reporting_unit_id: s.reportingUnitId || undefined,
    lead_days: s.leadDays,
    output_format: s.outputFormats.join(","),
    config_json: {
      reportType: s.reportType,
      connectorId: s.connectorId,
      cadence: s.cadence,
      dayOfMonth: s.dayOfMonth,
      timeHHmm: s.timeHHmm,
      gateByThreshold: s.gateByThreshold,
      thresholdKey: s.thresholdKey,
      outputFormats: s.outputFormats,
      jobParamsJson: s.jobParamsJson,
    },
    is_active: s.enabled,
  }
}

function jobFromApi(j: JobApi): JobRun {
  return {
    id: j.id,
    createdAt: j.triggered_at ?? j.created_at ?? new Date().toISOString(),
    scheduleId: j.schedule_id ?? undefined,
    reportType: j.job_type as ReportType,
    reportingUnitId: "",
    connectorId: "",
    status: j.status === "completed" ? "success" : j.status === "failed" ? "failed" : j.status === "running" ? "running" : "queued",
    message: j.error_message ?? undefined,
  }
}

export default function MeldewesenKonsole() {
  const qc = useQueryClient()
  const [activeConnectorId, setActiveConnectorId] = useState<string>("")
  const [activeScheduleId, setActiveScheduleId] = useState<string>("")

  const { data: connectorsApi = [], isLoading: loadingC, isError: errC, error: errConn, refetch: refetchC } = useQuery({
    queryKey: ["meldewesen", "connectors"],
    queryFn: listConnectors,
  })
  const { data: unitsApi = [], isLoading: loadingU, isError: errU, error: errUnit, refetch: refetchU } = useQuery({
    queryKey: ["meldewesen", "reportingUnits"],
    queryFn: listReportingUnits,
  })
  const { data: schedulesApi = [], isLoading: loadingS, isError: errS, error: errSched, refetch: refetchS } = useQuery({
    queryKey: ["meldewesen", "schedules"],
    queryFn: listSchedules,
  })
  const { data: jobsApi = [], refetch: refetchJ } = useQuery({
    queryKey: ["meldewesen", "jobs"],
    queryFn: () => listJobs({ limit: 50 }),
  })

  const connectors = useMemo(() => connectorsApi.map(connectorFromApi), [connectorsApi])
  const units = useMemo(() => unitsApi.map(unitFromApi), [unitsApi])
  const schedules = useMemo(() => schedulesApi.map(scheduleFromApi), [schedulesApi])
  const jobs = useMemo(() => jobsApi.map(jobFromApi), [jobsApi])
  const latestJob = jobs[0]
  const artifactsQuery = useQuery({
    queryKey: ["meldewesen", "jobs", "artifacts", latestJob?.id],
    queryFn: () => {
      if (!latestJob?.id) {
        return Promise.resolve([])
      }
      return getJobArtifacts(latestJob.id)
    },
    enabled: Boolean(latestJob?.id),
  })
  const { data: dokumente = [] } = useDokumenteAblage()
  const { data: wiegungen = [] } = useWiegungen()
  const { data: warteschlange } = useWarteschlange()
  const { data: frachtbriefe = [] } = useFrachtbriefe()

  const createConnectorMu = useMutation({
    mutationFn: createConnector,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "connectors"] }),
  })
  const updateConnectorMu = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateConnector>[1] }) => updateConnector(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "connectors"] }),
  })
  const deleteConnectorMu = useMutation({
    mutationFn: deleteConnector,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "connectors"] }),
  })
  const createUnitMu = useMutation({
    mutationFn: createReportingUnit,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "reportingUnits"] }),
  })
  const createScheduleMu = useMutation({
    mutationFn: createSchedule,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "schedules"] }),
  })
  const updateScheduleMu = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateSchedule>[1] }) => updateSchedule(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "schedules"] }),
  })
  const deleteScheduleMu = useMutation({
    mutationFn: deleteSchedule,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "schedules"] }),
  })
  const runJobMu = useMutation({
    mutationFn: runJob,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["meldewesen", "jobs"] }),
  })

  const activeConnector = useMemo(() => connectors.find((c) => c.id === activeConnectorId) ?? connectors[0] ?? null, [connectors, activeConnectorId])
  const activeSchedule = useMemo(() => schedules.find((s) => s.id === activeScheduleId) ?? schedules[0] ?? null, [schedules, activeScheduleId])
  React.useEffect(() => {
    if (connectors.length && !activeConnectorId) setActiveConnectorId(connectors[0].id)
  }, [connectors, activeConnectorId])
  React.useEffect(() => {
    if (schedules.length && !activeScheduleId) setActiveScheduleId(schedules[0].id)
  }, [schedules, activeScheduleId])

  const thresholds = useMemo(() => {
    const intrastatUnits = units.filter((unit) => unit.intrastatEnabled)
    const arrivalSchedules = schedules.filter((schedule) => schedule.thresholdKey === "INTRASTAT_ARRIVAL" || schedule.reportType === "INTRASTAT_DE")
    const dispatchSchedules = schedules.filter((schedule) => schedule.thresholdKey === "INTRASTAT_DISPATCH" || schedule.reportType === "INTRASTAT_DE")
    const arrivalJobs = jobs.filter((job) => job.reportType === "INTRASTAT_DE" && job.status !== "failed")
    const dispatchJobs = jobs.filter((job) => job.reportType === "INTRASTAT_DE")
    const failedIntrastatJobs = jobs.filter((job) => job.reportType === "INTRASTAT_DE" && job.status === "failed").length

    const buildThreshold = (
      matchingSchedules: Schedule[],
      matchingJobs: JobRun[],
      hasRelevantUnits: boolean,
      blockedByFailures: boolean,
    ) => {
      const readinessParts = [
        hasRelevantUnits ? 35 : 0,
        matchingSchedules.some((schedule) => schedule.enabled) ? 35 : 0,
        matchingJobs.some((job) => job.status === "success") ? 20 : matchingJobs.some((job) => job.status === "running" || job.status === "queued") ? 10 : 0,
        blockedByFailures ? 0 : 10,
      ]
      const progressPct = Math.max(0, Math.min(100, readinessParts.reduce((sum, part) => sum + part, 0)))
      return {
        reached: hasRelevantUnits && matchingSchedules.some((schedule) => schedule.enabled),
        progressPct,
        scheduleCount: matchingSchedules.length,
        jobCount: matchingJobs.length,
        statusLabel: blockedByFailures ? "Stoerung" : progressPct >= 80 ? "arbeitsfaehig" : progressPct >= 50 ? "in Vorbereitung" : "unvollstaendig",
        hint: blockedByFailures
          ? "Fehlgeschlagene Intrastat-Laeufe blockieren derzeit den sauberen Aktivierungspfad."
          : !hasRelevantUnits
            ? "Noch keine geeignete Reporting Unit mit Intrastat-Aktivierung vorhanden."
            : matchingSchedules.length === 0
              ? "Reporting Unit vorhanden, aber noch kein belastbarer Zeitplan eingerichtet."
              : matchingJobs.length === 0
                ? "Zeitplaene stehen, aber es fehlt noch ein erster erfolgreicher Lauf."
                : "Zeitplaene und Laeufe liefern einen belastbaren Aktivierungsstand.",
      }
    }

    return {
      INTRASTAT_ARRIVAL: buildThreshold(arrivalSchedules, arrivalJobs, intrastatUnits.length > 0, failedIntrastatJobs > 0),
      INTRASTAT_DISPATCH: buildThreshold(dispatchSchedules, dispatchJobs, intrastatUnits.length > 0, failedIntrastatJobs > 0),
    }
  }, [jobs, schedules, units])
  const feedbackSummary = useMemo(
    () =>
      summarizeMeldewesenFeedback({
        failedJobs: jobs.filter((job) => job.status === 'failed').length,
        runningJobs: jobs.filter((job) => job.status === 'running' || job.status === 'queued').length,
        artifactCount: (artifactsQuery.data ?? []).length,
        queueCount: warteschlange?.items?.length ?? 0,
        weighingCount: wiegungen.length,
        freightCount: frachtbriefe.length,
        documentCount: dokumente.length,
      }),
    [artifactsQuery.data, dokumente.length, frachtbriefe.length, jobs, warteschlange?.items?.length, wiegungen.length],
  )

  const upsertConnector = useCallback(
    (next: Connector) => {
      const existing = connectorsApi.find((c) => c.id === next.id)
      if (existing) {
        updateConnectorMu.mutate({ id: next.id, payload: connectorToApiUpdate(next) })
      } else {
        createConnectorMu.mutate({
          ...connectorToApiCreate(next),
          connector_key: next.id || uid("conn"),
        })
      }
    },
    [connectorsApi, createConnectorMu, updateConnectorMu]
  )

  const upsertSchedule = useCallback(
    (next: Schedule) => {
      const existing = schedulesApi.find((s) => s.id === next.id)
      if (existing) {
        updateScheduleMu.mutate({ id: next.id, payload: scheduleToApiUpdate(next) })
      } else {
        createScheduleMu.mutate({
          ...scheduleToApiCreate(next),
          schedule_key: next.id || uid("sch"),
        })
      }
    },
    [schedulesApi, createScheduleMu, updateScheduleMu]
  )

  const removeSchedule = useCallback(
    (id: string) => {
      deleteScheduleMu.mutate(id)
      if (activeScheduleId === id) setActiveScheduleId(schedules[0]?.id ?? "")
    },
    [activeScheduleId, deleteScheduleMu, schedules]
  )

  const runScheduleNow = useCallback(
    async (s: Schedule) => {
      runJobMu.mutate({
        schedule_id: s.id,
        job_type: s.reportType,
        dry_run: false,
      })
      refetchJ()
    },
    [runJobMu, refetchJ]
  )

  const exportAllConfig = useCallback(() => {
    const payload = {
      version: 1,
      exportedAt: new Date().toISOString(),
      connectors,
      units,
      schedules,
    }
    downloadText(`meldewesen_config_${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(payload, null, 2))
  }, [connectors, units, schedules])

  const importAllConfig = useCallback(
    (file: File) => {
      const reader = new FileReader()
      reader.onload = () => {
        const txt = String(reader.result ?? "")
        const parsed = safeJsonParse<{ connectors?: Connector[]; units?: ReportingUnit[]; schedules?: Schedule[] }>(txt, {})
        if (!parsed?.connectors || !parsed?.units || !parsed?.schedules) return
        parsed.connectors.forEach((c) => upsertConnector({ ...c, id: c.id || uid("conn") }))
        parsed.units.forEach((u) => createUnitMu.mutate(unitToApiCreate({ ...u, id: u.id || uid("unit") })))
        parsed.schedules.forEach((s) => createScheduleMu.mutate(scheduleToApiCreate({ ...s, id: s.id || uid("sch") })))
      }
      reader.readAsText(file)
    },
    [createScheduleMu, createUnitMu, upsertConnector]
  )

  const isLoading = loadingC || loadingU || loadingS
  const isError = errC || errU || errS
  const error = errConn ?? errUnit ?? errSched

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetchC(); void refetchU(); void refetchS(); void refetchJ() },
  })
  useKeyboardShortcuts(shortcuts)

  if (isError) {
    return (
      <div className="p-4">
        <ErrorState error={error as Error} onRetry={() => { void refetchC(); void refetchU(); void refetchS(); void refetchJ() }} />
      </div>
    )
  }

  if (isLoading && !connectors.length) {
    return (
      <div className="p-4 md:p-6 space-y-4">
        <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        <div className="h-64 bg-muted animate-pulse rounded" />
      </div>
    )
  }

  const operationalStatus = normalizeOperationalStatus(feedbackSummary.feedbackRisk)

  return (
    <div className="flex flex-col">
    <div className="p-4 md:p-6 space-y-4">
      <OperationalCaseHeader
        title="Meldewesen-Konsole"
        status={operationalStatus}
        blocker={jobs.filter((j) => j.status === 'failed').length > 0 ? `${jobs.filter((j) => j.status === 'failed').length} fehlgeschlagene(r) Lauf/Läufe` : null}
        nextAction={feedbackSummary.nextAction}
        caseLabel="Compliance"
      />
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Meldewesen-Konsole</h1>
          <p className="text-sm text-muted-foreground">
            Konfiguration fÃ¼r Meldestellen/Ãœbertragungswege, Stichtags-Jobs, Artefakte (CSV/XML/JSON) und Audit-Logs.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={exportAllConfig}>
            <Download className="h-4 w-4 mr-2" /> Export
          </Button>
          <label className="inline-flex items-center">
            <input
              type="file"
              className="hidden"
              accept="application/json"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) importAllConfig(f)
              }}
            />
            <Button variant="secondary" asChild>
              <span>
                <Upload className="h-4 w-4 mr-2" /> Import
              </span>
            </Button>
          </label>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Rueckmeldungsrisiko</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{feedbackSummary.feedbackRisk}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Artefakte letzter Lauf</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">{(artifactsQuery.data ?? []).length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Naechster Nachweisschritt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-semibold">{feedbackSummary.nextAction}</div>
          </CardContent>
        </Card>
      </div>

      <AgentProcessPanel domain="compliance" />

      <Alert>
        <ShieldAlert className="h-4 w-4" />
        <AlertTitle>Hinweis (Produktivbetrieb)</AlertTitle>
        <AlertDescription>
          API-Keys/Zertifikate sollten serverseitig verschlÃ¼sselt gespeichert werden (Vault/KMS). Das Frontend sollte nur maskiert anzeigen.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="schedules" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="schedules">ZeitplÃ¤ne</TabsTrigger>
          <TabsTrigger value="connectors">Ãœbertragungswege</TabsTrigger>
          <TabsTrigger value="units">Firmen/Konzern</TabsTrigger>
          <TabsTrigger value="jobs">LÃ¤ufe &amp; Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="connectors" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Connector-Liste</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    const c: Connector = {
                      id: uid("conn"),
                      name: "Neuer Connector",
                      enabled: true,
                      transport: "file-drop",
                      supportedReportTypes: ["INTRASTAT_DE"],
                      secrets: { outboxPath: "./outbox" },
                    }
                    createConnectorMu.mutate(
                      {
                        connector_key: c.id,
                        connector_type: c.transport,
                        display_name: c.name,
                        config_json: { supportedReportTypes: c.supportedReportTypes, secrets: c.secrets },
                        is_active: true,
                      },
                      { onSuccess: (data) => setActiveConnectorId(data.id) }
                    )
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" /> Neu
                </Button>
                <Separator />
                <ScrollArea className="h-[420px] pr-2">
                  <div className="space-y-2">
                    {connectors.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => setActiveConnectorId(c.id)}
                        className={`w-full text-left p-3 rounded-lg border transition ${c.id === activeConnectorId ? "bg-muted" : "hover:bg-muted/50"}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-medium">{c.name}</div>
                          <Badge variant={c.enabled ? "default" : "secondary"}>{c.transport}</Badge>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">{c.supportedReportTypes.join(", ")}</div>
                      </button>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Connector bearbeiten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!activeConnector ? (
                  <div className="text-sm text-muted-foreground">WÃ¤hle links einen Connector aus.</div>
                ) : (
                  <>
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1">
                        <Label>Name</Label>
                        <Input value={activeConnector.name} onChange={(e) => upsertConnector({ ...activeConnector, name: e.target.value })} />
                      </div>
                      <div className="flex items-center gap-2 mt-6">
                        <Switch checked={activeConnector.enabled} onCheckedChange={(v) => upsertConnector({ ...activeConnector, enabled: v })} />
                        <span className="text-sm">Aktiv</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label>Transport</Label>
                        <NativeSelect
                          value={activeConnector.transport}
                          onValueChange={(v) => upsertConnector({ ...activeConnector, transport: v as TransportKind })}
                          options={[
                            { value: "file-drop", label: "file-drop (Outbox)" },
                            { value: "https", label: "https (API)" },
                            { value: "sftp", label: "sftp" },
                            { value: "email", label: "email" },
                            { value: "provider", label: "provider (Zoll)" },
                          ]}
                          placeholder="Transport wÃ¤hlen"
                        />
                      </div>

                      <div>
                        <Label>UnterstÃ¼tzte Meldungen</Label>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {(["INTRASTAT_DE", "BLE_MVO", "ZOLL_ATLAS_PROVIDER", "EUDR_DDS"] as ReportType[]).map((t) => {
                            const on = activeConnector.supportedReportTypes.includes(t)
                            return (
                              <Button
                                key={t}
                                size="sm"
                                variant={on ? "default" : "outline"}
                                onClick={() => {
                                  const next = on
                                    ? activeConnector.supportedReportTypes.filter((x) => x !== t)
                                    : [...activeConnector.supportedReportTypes, t]
                                  upsertConnector({ ...activeConnector, supportedReportTypes: next })
                                }}
                              >
                                {t}
                              </Button>
                            )
                          })}
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label>Base URL (fÃ¼r https/provider)</Label>
                        <Input
                          value={activeConnector.secrets.baseUrl ?? ""}
                          onChange={(e) =>
                            upsertConnector({
                              ...activeConnector,
                              secrets: { ...activeConnector.secrets, baseUrl: e.target.value },
                            })
                          }
                          placeholder="https://..."
                        />
                      </div>
                      <div>
                        <Label>API Key (maskiert anzeigen im Backend!)</Label>
                        <Input
                          value={activeConnector.secrets.apiKey ?? ""}
                          onChange={(e) =>
                            upsertConnector({
                              ...activeConnector,
                              secrets: { ...activeConnector.secrets, apiKey: e.target.value },
                            })
                          }
                          placeholder="â€¢â€¢â€¢â€¢â€¢â€¢"
                        />
                      </div>
                      <div>
                        <Label>Outbox Pfad (file-drop)</Label>
                        <Input
                          value={activeConnector.secrets.outboxPath ?? ""}
                          onChange={(e) =>
                            upsertConnector({
                              ...activeConnector,
                              secrets: { ...activeConnector.secrets, outboxPath: e.target.value },
                            })
                          }
                          placeholder="./outbox"
                        />
                      </div>
                    </div>

                    <div>
                      <Label>Notizen</Label>
                      <Textarea
                        value={activeConnector.notes ?? ""}
                        onChange={(e) => upsertConnector({ ...activeConnector, notes: e.target.value })}
                        placeholder="z. B. Upload-Maske, Ansprechpartner, Formatvorgabenâ€¦"
                      />
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button
                        variant="destructive"
                        onClick={() => {
                          deleteConnectorMu.mutate(activeConnector.id)
                          setActiveConnectorId(connectors.find((x) => x.id !== activeConnector.id)?.id ?? connectors[0]?.id ?? "")
                        }}
                      >
                        <Trash2 className="h-4 w-4 mr-2" /> LÃ¶schen
                      </Button>
                      <Button onClick={() => upsertConnector(activeConnector)}>
                        <Save className="h-4 w-4 mr-2" /> Speichern
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="units" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Firmen / Reporting Units</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    const u: ReportingUnit = {
                      id: uid("unit"),
                      name: "Neue Firma",
                      countryIso2: "DE",
                      intrastatEnabled: true,
                      bleMvoEnabled: false,
                      eudrEnabled: false,
                    }
                    createUnitMu.mutate(unitToApiCreate(u))
                    refetchU()
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" /> Neu
                </Button>
                <Separator />
                <div className="space-y-2">
                  {units.map((u) => (
                    <div key={u.id} className="p-3 rounded-lg border">
                      <div className="font-medium">{u.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {u.countryIso2} Â· {u.vatId ?? "(keine USt-ID)"}
                      </div>
                      <div className="flex gap-2 mt-2 flex-wrap">
                        {u.intrastatEnabled && <Badge>Intrastat</Badge>}
                        {u.bleMvoEnabled && <Badge>BLE/MVO</Badge>}
                        {u.eudrEnabled && <Badge>EUDR</Badge>}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Schwellen / Aktivierungslogik</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm text-muted-foreground">
                  Die Bewertung verdichtet vorhandene Reporting Units, Zeitplaene und bisherige Laeufe zu einem
                  belastbaren Aktivierungsstand fuer Intrastat.
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">Intrastat Eingang</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Aktivierungsstand</span>
                        <span className="font-medium">{thresholds.INTRASTAT_ARRIVAL.progressPct}%</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Status</span>
                        <Badge variant={thresholds.INTRASTAT_ARRIVAL.reached ? "default" : "secondary"}>{thresholds.INTRASTAT_ARRIVAL.statusLabel}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Zeitplaene / Laeufe</span>
                        <span>{thresholds.INTRASTAT_ARRIVAL.scheduleCount} / {thresholds.INTRASTAT_ARRIVAL.jobCount}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{thresholds.INTRASTAT_ARRIVAL.hint}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">Intrastat Versendung</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Aktivierungsstand</span>
                        <span className="font-medium">{thresholds.INTRASTAT_DISPATCH.progressPct}%</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Status</span>
                        <Badge variant={thresholds.INTRASTAT_DISPATCH.reached ? "default" : "secondary"}>{thresholds.INTRASTAT_DISPATCH.statusLabel}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Zeitplaene / Laeufe</span>
                        <span>{thresholds.INTRASTAT_DISPATCH.scheduleCount} / {thresholds.INTRASTAT_DISPATCH.jobCount}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{thresholds.INTRASTAT_DISPATCH.hint}</p>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="schedules" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>ZeitplÃ¤ne</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    const s: Schedule = {
                      id: uid("sch"),
                      enabled: true,
                      name: "Neuer Zeitplan",
                      reportType: "INTRASTAT_DE",
                      reportingUnitId: units[0]?.id ?? "",
                      connectorId: connectors[0]?.id ?? "",
                      cadence: "monthly",
                      dayOfMonth: 20,
                      timeHHmm: "09:00",
                      leadDays: 2,
                      gateByThreshold: false,
                      outputFormats: ["csv"],
                      jobParamsJson: JSON.stringify({ direction: "ARRIVAL", currency: "EUR" }, null, 2),
                    }
                    createScheduleMu.mutate(scheduleToApiCreate(s), {
                      onSuccess: (data) => setActiveScheduleId(data.id),
                    })
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" /> Neu
                </Button>
                <Separator />
                <ScrollArea className="h-[420px] pr-2">
                  <div className="space-y-2">
                    {schedules.map((s) => (
                      <button
                        key={s.id}
                        onClick={() => setActiveScheduleId(s.id)}
                        className={`w-full text-left p-3 rounded-lg border transition ${s.id === activeScheduleId ? "bg-muted" : "hover:bg-muted/50"}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-medium">{s.name}</div>
                          <Badge variant={s.enabled ? "default" : "secondary"}>{s.reportType}</Badge>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {s.cadence} Â· {String(s.dayOfMonth).padStart(2, "0")} Â· {s.timeHHmm} Â· lead {s.leadDays}d
                        </div>
                      </button>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Zeitplan bearbeiten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!activeSchedule ? (
                  <div className="text-sm text-muted-foreground">WÃ¤hle links einen Zeitplan aus.</div>
                ) : (
                  <>
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1">
                        <Label>Name</Label>
                        <Input value={activeSchedule.name} onChange={(e) => upsertSchedule({ ...activeSchedule, name: e.target.value })} />
                      </div>
                      <div className="flex items-center gap-2 mt-6">
                        <Switch checked={activeSchedule.enabled} onCheckedChange={(v) => upsertSchedule({ ...activeSchedule, enabled: v })} />
                        <span className="text-sm">Aktiv</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label>Meldungstyp</Label>
                        <NativeSelect
                          value={activeSchedule.reportType}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, reportType: v as ReportType })}
                          options={[
                            { value: "INTRASTAT_DE", label: "INTRASTAT_DE" },
                            { value: "BLE_MVO", label: "BLE_MVO" },
                            { value: "ZOLL_ATLAS_PROVIDER", label: "ZOLL_ATLAS_PROVIDER" },
                            { value: "EUDR_DDS", label: "EUDR_DDS" },
                          ]}
                        />
                      </div>

                      <div>
                        <Label>Firma (Reporting Unit)</Label>
                        <NativeSelect
                          value={activeSchedule.reportingUnitId}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, reportingUnitId: v })}
                          options={units.map((u) => ({ value: u.id, label: u.name }))}
                        />
                      </div>

                      <div>
                        <Label>Ãœbertragungsweg (Connector)</Label>
                        <NativeSelect
                          value={activeSchedule.connectorId}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, connectorId: v })}
                          options={connectors.map((c) => ({ value: c.id, label: c.name }))}
                        />
                      </div>

                      <div>
                        <Label>Exportformate</Label>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {(["csv", "xml", "json"] as const).map((fmt) => {
                            const on = activeSchedule.outputFormats.includes(fmt)
                            return (
                              <Button
                                key={fmt}
                                size="sm"
                                variant={on ? "default" : "outline"}
                                onClick={() => {
                                  const next = on
                                    ? activeSchedule.outputFormats.filter((x) => x !== fmt)
                                    : [...activeSchedule.outputFormats, fmt]
                                  upsertSchedule({ ...activeSchedule, outputFormats: next })
                                }}
                              >
                                <FileText className="h-4 w-4 mr-2" /> {fmt.toUpperCase()}
                              </Button>
                            )
                          })}
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label>Takt</Label>
                        <NativeSelect
                          value={activeSchedule.cadence}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, cadence: v as Schedule["cadence"] })}
                          options={[
                            { value: "monthly", label: "monatlich" },
                            { value: "quarterly", label: "quartalsweise" },
                            { value: "yearly", label: "j?hrlich" },
                          ]}
                        />
                      </div>
                      <div>
                        <Label>Stichtag (Tag im Monat)</Label>
                        <Input
                          type="number"
                          min={1}
                          max={28}
                          value={activeSchedule.dayOfMonth}
                          onChange={(e) => upsertSchedule({ ...activeSchedule, dayOfMonth: Number(e.target.value || 1) })}
                        />
                      </div>
                      <div>
                        <Label>Uhrzeit</Label>
                        <Input value={activeSchedule.timeHHmm} onChange={(e) => upsertSchedule({ ...activeSchedule, timeHHmm: e.target.value })} placeholder="09:00" />
                      </div>
                      <div>
                        <Label>AuslÃ¶sen vorher (leadDays)</Label>
                        <Input
                          type="number"
                          min={0}
                          max={14}
                          value={activeSchedule.leadDays}
                          onChange={(e) => upsertSchedule({ ...activeSchedule, leadDays: Number(e.target.value || 0) })}
                        />
                      </div>
                    </div>

                    <Separator />

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Gate by Threshold</Label>
                      </div>
                      <Switch checked={activeSchedule.gateByThreshold} onCheckedChange={(v) => upsertSchedule({ ...activeSchedule, gateByThreshold: v })} />
                    </div>
                    {activeSchedule.gateByThreshold && (
                      <div>
                        <Label>Schwellen-SchlÃ¼ssel</Label>
                        <NativeSelect
                          value={activeSchedule.thresholdKey ?? "INTRASTAT_ARRIVAL"}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, thresholdKey: v as Schedule["thresholdKey"] })}
                          options={[
                            { value: "INTRASTAT_ARRIVAL", label: "INTRASTAT_ARRIVAL" },
                            { value: "INTRASTAT_DISPATCH", label: "INTRASTAT_DISPATCH" },
                          ]}
                        />
                      </div>
                    )}

                    <div>
                      <Label>Job-Parameter (JSON)</Label>
                      <Textarea
                        value={activeSchedule.jobParamsJson}
                        onChange={(e) => upsertSchedule({ ...activeSchedule, jobParamsJson: e.target.value })}
                        className="font-mono text-xs"
                        rows={10}
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base flex items-center gap-2">
                            <CalendarDays className="h-4 w-4" /> NÃ¤chste AusfÃ¼hrungen
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-1 text-sm">
                          {nextRunsPreview(activeSchedule).map((x) => (
                            <div key={x} className="flex items-center gap-2">
                              <Clock className="h-4 w-4" /> <span>{x}</span>
                            </div>
                          ))}
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Aktionen</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                          <Button
                            className="w-full"
                            onClick={() => runScheduleNow(activeSchedule)}
                            disabled={runJobMu.isPending}
                          >
                            <Play className="h-4 w-4 mr-2" /> Jetzt ausfÃ¼hren
                          </Button>
                          <Button variant="outline" className="w-full" onClick={() => upsertSchedule(activeSchedule)}>
                            <Save className="h-4 w-4 mr-2" /> Speichern
                          </Button>
                          <Button variant="destructive" className="w-full" onClick={() => removeSchedule(activeSchedule.id)}>
                            <Trash2 className="h-4 w-4 mr-2" /> LÃ¶schen
                          </Button>
                        </CardContent>
                      </Card>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="jobs" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>LÃ¤ufe</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm text-muted-foreground">Job-LÃ¤ufe aus dem Backend (DB).</div>
                <div className="space-y-2">
                  {jobs.slice(0, 12).map((j) => (
                    <div key={j.id} className="p-3 rounded-lg border">
                      <div className="flex items-center justify-between gap-2">
                        <div className="font-medium">{j.reportType}</div>
                        <Badge variant={j.status === "success" ? "default" : j.status === "failed" ? "destructive" : "secondary"}>{j.status}</Badge>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(j.createdAt).toLocaleString()} Â· {j.scheduleId ?? "ad-hoc"}
                      </div>
                      {j.message && <div className="text-sm mt-2">{j.message}</div>}
                    </div>
                  ))}
                  {jobs.length === 0 && <div className="text-sm text-muted-foreground">Noch keine LÃ¤ufe.</div>}
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Rückmeldungen und Objektbezug</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="rounded-lg border p-3 text-sm">
                  <div className="font-medium">{latestJob?.reportType ?? "Noch kein Lauf"}</div>
                  <div className="text-xs text-muted-foreground">{latestJob?.createdAt ? new Date(latestJob.createdAt).toLocaleString() : "n/a"}</div>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-muted-foreground">Artefakte</span>
                    <Badge variant="outline">{(artifactsQuery.data ?? []).length}</Badge>
                  </div>
                </div>
                <div className="grid gap-2 text-sm">
                  <div className="flex items-center justify-between rounded border px-3 py-2"><span>Warteschlange</span><span className="font-medium">{warteschlange?.items?.length ?? 0}</span></div>
                  <div className="flex items-center justify-between rounded border px-3 py-2"><span>Wiegungen</span><span className="font-medium">{wiegungen.length}</span></div>
                  <div className="flex items-center justify-between rounded border px-3 py-2"><span>Frachtbriefe</span><span className="font-medium">{frachtbriefe.length}</span></div>
                  <div className="flex items-center justify-between rounded border px-3 py-2"><span>Dokumente</span><span className="font-medium">{dokumente.length}</span></div>
                </div>
                <Separator />
                <div className="font-medium text-sm">Quick Actions</div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="w-full">
                      Konfig anzeigen (JSON)
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Aktuelle Konfiguration</DialogTitle>
                    </DialogHeader>
                    <ScrollArea className="h-[420px]">
                      <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto">
                        {JSON.stringify({ connectors, units, schedules }, null, 2)}
                      </pre>
                    </ScrollArea>
                  </DialogContent>
                </Dialog>
                <Button variant="outline" className="w-full" onClick={() => void refetchJ()}>
                  LÃ¤ufe aktualisieren
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Backend-Anbindung</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <div>Dieses UI ist an die APIs /api/v1/config und /api/v1/jobs angebunden. Daten werden in der Datenbank gespeichert.</div>
          <ul className="list-disc ml-5 space-y-1">
            <li>
              <span className="font-mono">GET/PUT/PATCH/DELETE /api/v1/config/connectors</span> â€“ Connectoren
            </li>
            <li>
              <span className="font-mono">GET/PUT/PATCH/DELETE /api/v1/config/schedules</span> â€“ ZeitplÃ¤ne
            </li>
            <li>
              <span className="font-mono">POST /api/v1/jobs/run</span> â€“ Job sofort starten
            </li>
            <li>
              <span className="font-mono">GET /api/v1/jobs</span> â€“ LÃ¤ufe/Status/Logs
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
