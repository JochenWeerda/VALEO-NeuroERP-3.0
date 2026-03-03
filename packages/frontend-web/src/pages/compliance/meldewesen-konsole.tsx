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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CalendarDays, Play, Save, ShieldAlert, Upload, Download, Trash2, Plus, FileText, Clock } from "lucide-react"
import { ErrorState } from "@/components/ErrorState"
import {
  listConnectors,
  listReportingUnits,
  listSchedules,
  listJobs,
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

// ── API ↔ Frontend Mappers ────────────────────────────────────────────────────

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

  const thresholds = useMemo(
    () => ({
      INTRASTAT_ARRIVAL: { reached: false, progressPct: 62 },
      INTRASTAT_DISPATCH: { reached: false, progressPct: 18 },
    }),
    []
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

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Meldewesen-Konsole</h1>
          <p className="text-sm text-muted-foreground">
            Konfiguration für Meldestellen/Übertragungswege, Stichtags-Jobs, Artefakte (CSV/XML/JSON) und Audit-Logs.
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

      <Alert>
        <ShieldAlert className="h-4 w-4" />
        <AlertTitle>Hinweis (Produktivbetrieb)</AlertTitle>
        <AlertDescription>
          API-Keys/Zertifikate sollten serverseitig verschlüsselt gespeichert werden (Vault/KMS). Das Frontend sollte nur maskiert anzeigen.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="schedules" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="schedules">Zeitpläne</TabsTrigger>
          <TabsTrigger value="connectors">Übertragungswege</TabsTrigger>
          <TabsTrigger value="units">Firmen/Konzern</TabsTrigger>
          <TabsTrigger value="jobs">Läufe &amp; Logs</TabsTrigger>
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
                  <div className="text-sm text-muted-foreground">Wähle links einen Connector aus.</div>
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
                        <Select
                          value={activeConnector.transport}
                          onValueChange={(v) => upsertConnector({ ...activeConnector, transport: v as TransportKind })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Transport wählen" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="file-drop">file-drop (Outbox)</SelectItem>
                            <SelectItem value="https">https (API)</SelectItem>
                            <SelectItem value="sftp">sftp</SelectItem>
                            <SelectItem value="email">email</SelectItem>
                            <SelectItem value="provider">provider (Zoll)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Unterstützte Meldungen</Label>
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
                        <Label>Base URL (für https/provider)</Label>
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
                          placeholder="••••••"
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
                        placeholder="z. B. Upload-Maske, Ansprechpartner, Formatvorgaben…"
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
                        <Trash2 className="h-4 w-4 mr-2" /> Löschen
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
                        {u.countryIso2} · {u.vatId ?? "(keine USt-ID)"}
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
                <CardTitle>Schwellen / Aktivierungslogik (Demo)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm text-muted-foreground">
                  In echt: Schwellen automatisch aus Jahresdaten ermitteln (YTD + Vorjahr) pro Reporting Unit.
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">Intrastat Eingang</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Fortschritt (Demo)</span>
                        <span className="font-medium">{thresholds.INTRASTAT_ARRIVAL.progressPct}%</span>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">Intrastat Versendung</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Fortschritt (Demo)</span>
                        <span className="font-medium">{thresholds.INTRASTAT_DISPATCH.progressPct}%</span>
                      </div>
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
                <CardTitle>Zeitpläne</CardTitle>
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
                          {s.cadence} · {String(s.dayOfMonth).padStart(2, "0")} · {s.timeHHmm} · lead {s.leadDays}d
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
                  <div className="text-sm text-muted-foreground">Wähle links einen Zeitplan aus.</div>
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
                        <Select value={activeSchedule.reportType} onValueChange={(v) => upsertSchedule({ ...activeSchedule, reportType: v as ReportType })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="INTRASTAT_DE">INTRASTAT_DE</SelectItem>
                            <SelectItem value="BLE_MVO">BLE_MVO</SelectItem>
                            <SelectItem value="ZOLL_ATLAS_PROVIDER">ZOLL_ATLAS_PROVIDER</SelectItem>
                            <SelectItem value="EUDR_DDS">EUDR_DDS</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Firma (Reporting Unit)</Label>
                        <Select value={activeSchedule.reportingUnitId} onValueChange={(v) => upsertSchedule({ ...activeSchedule, reportingUnitId: v })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {units.map((u) => (
                              <SelectItem key={u.id} value={u.id}>
                                {u.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Übertragungsweg (Connector)</Label>
                        <Select value={activeSchedule.connectorId} onValueChange={(v) => upsertSchedule({ ...activeSchedule, connectorId: v })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {connectors.map((c) => (
                              <SelectItem key={c.id} value={c.id}>
                                {c.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
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
                        <Select value={activeSchedule.cadence} onValueChange={(v) => upsertSchedule({ ...activeSchedule, cadence: v as Schedule["cadence"] })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="monthly">monatlich</SelectItem>
                            <SelectItem value="quarterly">quartalsweise</SelectItem>
                            <SelectItem value="yearly">jährlich</SelectItem>
                          </SelectContent>
                        </Select>
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
                        <Label>Auslösen vorher (leadDays)</Label>
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
                        <Label>Schwellen-Schlüssel</Label>
                        <Select
                          value={activeSchedule.thresholdKey ?? "INTRASTAT_ARRIVAL"}
                          onValueChange={(v) => upsertSchedule({ ...activeSchedule, thresholdKey: v as Schedule["thresholdKey"] })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="INTRASTAT_ARRIVAL">INTRASTAT_ARRIVAL</SelectItem>
                            <SelectItem value="INTRASTAT_DISPATCH">INTRASTAT_DISPATCH</SelectItem>
                          </SelectContent>
                        </Select>
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
                            <CalendarDays className="h-4 w-4" /> Nächste Ausführungen
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
                            <Play className="h-4 w-4 mr-2" /> Jetzt ausführen
                          </Button>
                          <Button variant="outline" className="w-full" onClick={() => upsertSchedule(activeSchedule)}>
                            <Save className="h-4 w-4 mr-2" /> Speichern
                          </Button>
                          <Button variant="destructive" className="w-full" onClick={() => removeSchedule(activeSchedule.id)}>
                            <Trash2 className="h-4 w-4 mr-2" /> Löschen
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
                <CardTitle>Läufe</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm text-muted-foreground">Job-Läufe aus dem Backend (DB).</div>
                <div className="space-y-2">
                  {jobs.slice(0, 12).map((j) => (
                    <div key={j.id} className="p-3 rounded-lg border">
                      <div className="flex items-center justify-between gap-2">
                        <div className="font-medium">{j.reportType}</div>
                        <Badge variant={j.status === "success" ? "default" : j.status === "failed" ? "destructive" : "secondary"}>{j.status}</Badge>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(j.createdAt).toLocaleString()} · {j.scheduleId ?? "ad-hoc"}
                      </div>
                      {j.message && <div className="text-sm mt-2">{j.message}</div>}
                    </div>
                  ))}
                  {jobs.length === 0 && <div className="text-sm text-muted-foreground">Noch keine Läufe.</div>}
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
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
                  Läufe aktualisieren
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
              <span className="font-mono">GET/PUT/PATCH/DELETE /api/v1/config/connectors</span> – Connectoren
            </li>
            <li>
              <span className="font-mono">GET/PUT/PATCH/DELETE /api/v1/config/schedules</span> – Zeitpläne
            </li>
            <li>
              <span className="font-mono">POST /api/v1/jobs/run</span> – Job sofort starten
            </li>
            <li>
              <span className="font-mono">GET /api/v1/jobs</span> – Läufe/Status/Logs
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
