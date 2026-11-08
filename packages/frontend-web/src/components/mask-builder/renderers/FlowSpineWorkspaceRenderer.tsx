import { FlowSpineWorkspaceDialogs } from './FlowSpineWorkspaceDialogs'
import { lazy, Suspense } from 'react'
import {
  Building2,
  ArrowLeftRight,
  Bell,
  BookOpen,
  Calculator,
  Calendar,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  Database,
  FileText,
  History,
  Info,
  Landmark,
  Package,
  PauseCircle,
  PlayCircle,
  Plus,
  Receipt,
  Save,
  Search,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Truck,
  UserCircle2,
  Wallet,
  Warehouse,
  XCircle,
} from 'lucide-react'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'

const AgentProcessPanel = lazy(() => import('@/components/agent').then(m => ({ default: m.AgentProcessPanel })))
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { getFlowSpineFetchErrorMessage, flowSpineFooterItemHref, flowSpineFooterItemLabel, type FlowSpineLifecycleStatus } from '@/lib/api/flow-spines'
import { cn } from '@/lib/utils'

const ICONS = {
  ArrowLeftRight,
  BookOpen,
  Calculator,
  Calendar,
  Database,
  FileText,
  Landmark,
  Package,
  Receipt,
  Search,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Truck,
  UserCircle2,
  Wallet,
  Warehouse,
  Building2,
} as const

function toneClasses(tone: string): string {
  switch (tone) {
    case 'ok':
      return 'border-emerald-500/50 bg-emerald-500/12 text-emerald-200'
    case 'warning':
      return 'border-amber-500/50 bg-amber-500/12 text-amber-100'
    case 'critical':
      return 'border-rose-500/60 bg-rose-500/12 text-rose-100'
    case 'active':
      return 'border-indigo-400/70 bg-indigo-400/15 text-indigo-100 shadow-[0_0_40px_rgba(99,102,241,0.28)]'
    default:
      return 'border-slate-500/40 bg-slate-500/10 text-slate-200'
  }
}

type LifecycleDialogMode = 'hold' | 'complete' | 'cancel' | 'fail'

type LifecycleDialogState = {
  mode: LifecycleDialogMode
  reasonCategory: string
  reasonCode: string
  reasonNote: string
  businessStatus: string
  blockedUntil: string
}

const LIFECYCLE_LABELS: Record<FlowSpineLifecycleStatus, string> = {
  draft: 'Entwurf',
  in_progress: 'In Bearbeitung',
  on_hold: 'Pausiert',
  completed: 'Abgeschlossen',
  cancelled: 'Abgebrochen',
  failed: 'Gescheitert',
}

const LIFECYCLE_TONE_CLASSES: Record<FlowSpineLifecycleStatus, string> = {
  draft: 'border-slate-500/40 bg-slate-500/10 text-slate-200',
  in_progress:
    'border-[hsl(var(--color-semantic-info-500-hsl)/0.4)] bg-[hsl(var(--color-semantic-info-500-hsl)/0.15)] text-[hsl(var(--color-semantic-info-50-hsl))]',
  on_hold:
    'border-[hsl(var(--color-semantic-warning-500-hsl)/0.4)] bg-[hsl(var(--color-semantic-warning-500-hsl)/0.15)] text-[hsl(var(--color-semantic-warning-50-hsl))]',
  completed:
    'border-[hsl(var(--color-semantic-success-500-hsl)/0.4)] bg-[hsl(var(--color-semantic-success-500-hsl)/0.15)] text-[hsl(var(--color-semantic-success-50-hsl))]',
  cancelled:
    'border-[hsl(var(--color-semantic-error-500-hsl)/0.4)] bg-[hsl(var(--color-semantic-error-500-hsl)/0.15)] text-[hsl(var(--color-semantic-error-50-hsl))]',
  failed:
    'border-[hsl(var(--color-semantic-error-500-hsl)/0.55)] bg-[hsl(var(--color-semantic-error-500-hsl)/0.2)] text-[hsl(var(--color-semantic-error-50-hsl))]',
}

function EmptyOperationalField({
  label,
  className,
}: {
  label: string
  className?: string
}): JSX.Element {
  return (
    <div className={cn('rounded-xl border border-dashed border-white/12 px-3 py-2.5', className)}>
      <div className="text-xs text-slate-500">
        {label}: <span className="text-slate-400">nicht ermittelt</span>
      </div>
    </div>
  )
}

/**
 * FSX-003 Fall 1/2-Abgrenzung — Hinweis, dass der Workspace ohne konkreten Vorgang
 * Beispielinhalte aus dem Prozessregister zeigt. Ohne diesen Hinweis liest sich der
 * Katalogfall wie ein echter Vorgang.
 */
function CatalogContentNotice(): JSX.Element {
  return (
    <div className="mb-4 flex items-start gap-3 rounded-2xl border border-dashed border-amber-400/25 bg-amber-500/5 px-4 py-3">
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
      <div className="text-sm text-slate-300">
        <span className="font-medium text-slate-100">Beispielinhalt</span> — es ist kein
        Vorgang geladen. Kennzahlen, Zeitpunkte, Dokumente und Agentenhinweise stammen aus
        der Prozessbeschreibung und gehoeren zu keinem konkreten Fall. Waehle links einen
        Vorgang, um die tatsaechlichen Werte zu sehen.
      </div>
    </div>
  )
}

/** FSX-020: die drei Arbeitsmodi des Leitstands. */
type FlowSpineViewMode = 'flow' | 'fokus' | 'uebersicht'

const VIEW_MODES: Array<{ id: FlowSpineViewMode; label: string; hint: string }> = [
  { id: 'flow', label: 'Flow', hint: 'Vollbild: Prozess, Details, Kennzahlen und Agent.' },
  { id: 'fokus', label: 'Fokus', hint: 'Nur der aktuelle Schritt und seine Aktionen.' },
  { id: 'uebersicht', label: 'Uebersicht', hint: 'Nur Prozessverlauf und Vorgangsstatus.' },
]

function formatDateTime(value?: string | null): string {
  if (!value) return '—'
  try {
    return new Intl.DateTimeFormat('de-DE', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(value))
  } catch {
    return value
  }
}

function lifecycleSummary(workspace: {
  lifecycle_status?: FlowSpineLifecycleStatus
  cancellation_reason_code?: string
  failure_reason_code?: string
  completion_reason_code?: string
  reason_note?: string
}): string {
  if (workspace.lifecycle_status === 'cancelled') {
    return workspace.cancellation_reason_code || workspace.reason_note || 'Mit Grund beendet'
  }
  if (workspace.lifecycle_status === 'failed') {
    return workspace.failure_reason_code || workspace.reason_note || 'Gescheitert'
  }
  if (workspace.lifecycle_status === 'completed') {
    return workspace.completion_reason_code || workspace.reason_note || 'Fachlich abgeschlossen'
  }
  if (workspace.lifecycle_status === 'on_hold') {
    // F2 aus der Begehung: Ein pausierter Vorgang ist nicht abgeschlossen, und
    // ein Grund IST gesetzt — er steht nur im Ereignis, nicht auf der Instanz
    // (hold_instance schreibt reason_* ausschliesslich in die Timeline).
    // "Kein Abschlussgrund gesetzt" liess den Nutzer schliessen, es gebe keinen
    // Grund. Seit FSX-001 steht er in den Knotendetails der Mitte — nicht mehr
    // nur in der eingeklappten Timeline; der Verweis zeigt jetzt dorthin.
    return workspace.reason_note || 'Pausiert — Grund in den Knotendetails'
  }
  return workspace.reason_note || 'Kein Abschlussgrund gesetzt'
}

import type { FlowSpineWorkspaceRuntime } from '../runtime/useFlowSpineWorkspaceRuntime'

export function FlowSpineWorkspaceRenderer({ state }: { state: FlowSpineWorkspaceRuntime }): JSX.Element {
  const { processKey, instanceId, navigate, location, startConfig, workspaceQuery, workspace, nodes, selectedNode, processNavItems, viewMode, setViewMode, showNodeDetails, showSideFlaechen, copilotOpen, setCopilotOpen, progressWidth, go, handleAction, handleAgentAction, handleCreateInstance, openLifecycleDialog, closeLifecycleDialog, handleSaveLifecycle, handleResumeLifecycle, handleSubmitLifecycleDialog, setSelectedNodeId, showNewInstanceDialog, setShowNewInstanceDialog, newInstanceLabel, setNewInstanceLabel, newInstancePartnerName, setNewInstancePartnerName, newInstanceSubject, setNewInstanceSubject, newInstanceEntryMode, setNewInstanceEntryMode, newInstanceCustomer, setNewInstanceCustomer, showAdvancedCustomerSearch, setShowAdvancedCustomerSearch, createInstance, executeAction, executeAgentAction, instanceSearch, setInstanceSearch, instancesQuery, timelineQuery, saveInstance, resumeInstance, holdInstance, completeInstance, cancelInstance, failInstance, lifecycleDialog, setLifecycleDialog } = state
  if (workspaceQuery.isLoading) {
    return (
      <PageSurface
        data-page-surface={`flow-spine-${processKey}`}
        className="bg-[radial-gradient(circle_at_top_left,rgba(99,102,241,0.12),transparent_28%),linear-gradient(180deg,#08101f,#0d1528)]"
      >
        <PageSection className="overflow-hidden border-white/10 bg-slate-950/70 p-0">
          {/* Header skeleton */}
          <div className="flex h-16 items-center justify-between border-b border-white/5 px-5 gap-4">
            <div className="h-4 w-48 rounded-full bg-white/10 animate-pulse" />
            <div className="h-8 flex-1 max-w-xl rounded-lg bg-white/5 animate-pulse" />
            <div className="h-8 w-32 rounded-lg bg-white/10 animate-pulse" />
          </div>
          {/* 3-column body skeleton */}
          <div className="grid min-h-[720px] grid-cols-[220px_minmax(0,1fr)_360px]">
            {/* Left nav skeleton */}
            <div className="border-r border-white/5 bg-slate-950/45 p-4 space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-10 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: `${i * 60}ms` }} />
              ))}
            </div>
            {/* Main content skeleton */}
            <div className="bg-[linear-gradient(180deg,rgba(15,23,42,0.35),rgba(15,23,42,0.15))] p-6 space-y-6">
              <div className="h-8 w-72 rounded-full bg-white/10 animate-pulse" />
              <div className="rounded-[28px] border border-white/10 bg-white/3 p-8">
                {/* Node circles */}
                <div className="flex justify-around mb-8">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="flex flex-col items-center gap-3">
                      <div className="h-16 w-16 rounded-full bg-white/10 animate-pulse" style={{ animationDelay: `${i * 80}ms` }} />
                      <div className="h-3 w-16 rounded-full bg-white/10 animate-pulse" />
                    </div>
                  ))}
                </div>
                {/* Detail cards */}
                <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
                  <div className="h-48 rounded-2xl bg-white/5 animate-pulse" />
                  <div className="h-48 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: '100ms' }} />
                </div>
              </div>
            </div>
            {/* Right panel skeleton */}
            <div className="border-l border-white/5 bg-slate-950/45 p-5 space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: `${i * 70}ms` }} />
              ))}
            </div>
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  if (workspaceQuery.isError) {
    const detail = getFlowSpineFetchErrorMessage(workspaceQuery.error)
    return (
      <PageSurface data-page-surface={`flow-spine-${processKey}`}>
        <PageSection title="Flow Spine nicht verfuegbar" description="Der Prozessraum konnte nicht geladen werden.">
          <div className="space-y-3 rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-sm">
            <p className="font-medium text-destructive">{detail}</p>
            <p className="text-muted-foreground">
              Erwartet wird{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">
                GET /api/v1/process/flow-spines/{processKey}
              </code>{' '}
              mit JSON-Feld <code className="rounded bg-muted px-1 py-0.5 text-xs">nodes</code>. Lokal: FastAPI
              starten (z.&nbsp;B. Port 8000) und sicherstellen, dass Vite{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">/api/v1</code> dorthin proxied oder{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">VITE_API_BASE_URL</code> korrekt ist.
            </p>
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  if (!workspace || nodes.length === 0 || !selectedNode) {
    return (
      <PageSurface data-page-surface={`flow-spine-${processKey}`}>
        <PageSection title="Flow Spine nicht verfuegbar" description="Der Prozessraum konnte nicht geladen werden.">
          <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-sm text-destructive">
            Ungueltige oder leere Workspace-Daten (nodes). Bitte Backend-Vertrag pruefen.
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  const lifecycleStatus = workspace.lifecycle_status ?? 'draft'
  const lifecycleLabel = LIFECYCLE_LABELS[lifecycleStatus]
  const lifecycleToneClass = LIFECYCLE_TONE_CLASSES[lifecycleStatus]
  const hasTerminalLifecycle = lifecycleStatus === 'completed' || lifecycleStatus === 'cancelled' || lifecycleStatus === 'failed'
  const lifecycleBusy =
    saveInstance.isPending ||
    resumeInstance.isPending ||
    holdInstance.isPending ||
    completeInstance.isPending ||
    cancelInstance.isPending ||
    failInstance.isPending

  return (
    <PageSurface
      data-page-surface={`flow-spine-${processKey}`}
      className="bg-[radial-gradient(circle_at_top_left,rgba(99,102,241,0.12),transparent_28%),linear-gradient(180deg,#08101f,#0d1528)]"
    >
      <PageSection className="overflow-hidden border-white/10 bg-slate-950/70 p-0 shadow-2xl shadow-indigo-950/20">
        <header className="flex h-16 items-center justify-between border-b border-white/5 px-5">
          <div className="flex items-center gap-4">
            <div className="text-sm font-semibold tracking-wide text-slate-100">{workspace.breadcrumb[0]}</div>
            <div className="text-sm text-slate-400">
              {workspace.breadcrumb[1]} <span className="px-2 text-slate-600">/</span> <span className="font-semibold text-slate-100">{workspace.instance_label}</span>
            </div>
          </div>
          <div className="relative w-full max-w-xl">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input aria-label="Globale Suche" placeholder={workspace.search_placeholder} className="border-white/10 bg-white/5 pl-9 text-slate-100 placeholder:text-slate-500" />
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              className="min-h-touch border-indigo-400/30 bg-indigo-500/10 text-indigo-200 hover:bg-indigo-500/20"
              onClick={() => setShowNewInstanceDialog(true)}
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              {startConfig.buttonLabel}
            </Button>
            <div className="flex rounded-xl bg-white/5 p-1 text-xs" role="group" aria-label="Ansicht">
              {VIEW_MODES.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  title={mode.hint}
                  aria-pressed={viewMode === mode.id}
                  onClick={() => setViewMode(mode.id)}
                  className={cn(
                    'rounded-lg px-3 py-1.5 transition',
                    viewMode === mode.id
                      ? 'bg-indigo-500/30 text-indigo-100'
                      : 'text-slate-400 hover:bg-white/5 hover:text-slate-200',
                  )}
                >
                  {mode.label}
                </button>
              ))}
            </div>
            <Bell className="h-4 w-4 text-muted-foreground" />
            <Settings className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-100">
              <UserCircle2 className="h-5 w-5 text-muted-foreground" />
              <span>{workspace.user_role}</span>
            </div>
          </div>
        </header>

        {/*
          FSX-020/023/024: Das Raster stand fest auf 220 px + 360 px = 580 px, bevor
          die eigentliche Arbeitsflaeche begann. Die Prozessspalte entfaellt in
          'fokus' ganz, die Copilot-Spalte schrumpft auf 48 px, solange sie
          eingeklappt ist.
        */}
        <div
          className={cn(
            'grid min-h-[720px]',
            copilotOpen
              ? 'grid-cols-[220px_minmax(0,1fr)_360px]'
              : 'grid-cols-[220px_minmax(0,1fr)_48px]',
          )}
        >
          <aside className="border-r border-white/5 bg-slate-950/45 p-4">
            {/*
              F4 aus der Begehung: 'fokus' hatte die ganze linke Spalte
              ausgeblendet — und damit auch den Vorgangswechsel. Fuer die Waage
              ist der Wechsel zwischen Fahrzeugen aber **die Aufgabe**, nicht
              eine Ablenkung davon. Deshalb wird jetzt getrennt: die
              Prozessnavigation (zwischen neun Prozessarten wechseln) entfaellt
              im Fokus, die Vorgangsliste bleibt.
            */}
            {viewMode !== 'fokus' ? (
            <div className="mb-6">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Prozesse</p>
              <div className="space-y-2">
                {processNavItems.length === 0 ? (
                  <p className="rounded-2xl border border-amber-400/20 bg-amber-500/10 px-3 py-2 text-xs text-amber-100/90">
                    Keine Prozesslinks geladen. Backend pruefen (Workspace + Katalog) oder Seite neu laden.
                  </p>
                ) : null}
                {processNavItems.map((process) => (
                  <button
                    key={process.key}
                    onClick={() => go(process.route_path)}
                    className={cn(
                      'flex w-full items-center justify-between rounded-2xl px-3 py-3 text-left text-sm transition',
                      process.active ? 'bg-indigo-500/12 text-indigo-100 ring-1 ring-indigo-400/20' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                    )}
                  >
                    <span>{process.label}</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                ))}
              </div>
            </div>
            ) : null}
            <div className="mb-6">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Vorgaenge</p>
              <Input
                placeholder="Suchen..."
                value={instanceSearch}
                onChange={(e) => setInstanceSearch(e.target.value)}
                className="mb-2 h-8 border-white/10 bg-white/5 text-xs text-slate-100 placeholder:text-slate-500"
              />
              <div className="space-y-1.5 max-h-[300px] overflow-y-auto">
                {instancesQuery.data?.map((inst) => (
                  <button
                    key={inst.instance_id}
                    onClick={() => {
                      const activeProcess = processNavItems.find(p => p.active)
                      const basePath = activeProcess?.route_path || window.location.pathname
                      navigate(`${basePath}?instanceId=${inst.instance_id}`)
                    }}
                    className={cn(
                      'w-full rounded-xl border px-3 py-2 text-left transition',
                      instanceId === inst.instance_id
                        ? 'border-indigo-400/40 bg-indigo-500/15 text-indigo-100'
                        : 'border-white/5 bg-white/3 text-slate-300 hover:bg-white/6',
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-xs font-medium truncate">{inst.case_number}</div>
                      {inst.lifecycle_status ? (
                        <span className={cn('shrink-0 rounded-full border px-1.5 py-0.5 text-[10px]', LIFECYCLE_TONE_CLASSES[inst.lifecycle_status])}>
                          {LIFECYCLE_LABELS[inst.lifecycle_status]}
                        </span>
                      ) : null}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate">
                      {inst.customer_name || inst.label || inst.subject || '\u2013'}
                    </div>
                  </button>
                ))}
                {instancesQuery.isLoading && (
                  <div className="text-xs text-slate-500 py-2">Laden...</div>
                )}
                {!instancesQuery.isLoading && instancesQuery.data?.length === 0 && (
                  <div className="text-xs text-slate-500 py-2">Keine Vorgaenge gefunden</div>
                )}
              </div>
            </div>
          </aside>

          <main className="bg-[linear-gradient(180deg,rgba(15,23,42,0.35),rgba(15,23,42,0.15))] p-6">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-white">{workspace.title}</h1>
                <p className="mt-1 max-w-3xl text-sm text-slate-400">{workspace.subtitle}</p>
              </div>
              <div className="flex items-center gap-2">
                {workspace.badges.map((badge) => (
                  <Badge key={badge.label} className={cn('hover:bg-transparent', badge.tone === 'ok' ? 'bg-emerald-500/15 text-emerald-200' : 'bg-amber-500/15 text-amber-100')}>
                    {badge.label}
                  </Badge>
                ))}
              </div>
            </div>

            {workspace.content_mode === 'catalog' ? <CatalogContentNotice /> : null}

            {workspace.customer_data && (
              <div className="mb-4 flex items-center gap-4 rounded-2xl border border-indigo-400/20 bg-indigo-500/8 px-5 py-3">
                <Building2 className="h-5 w-5 text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-slate-100">
                    {workspace.customer_data.name_1}
                    {workspace.customer_data.name_2 && ` \u2013 ${workspace.customer_data.name_2}`}
                  </div>
                  <div className="text-xs text-slate-400">
                    {[workspace.customer_data.street, workspace.customer_data.house_number].filter(Boolean).join(' ')}
                    {workspace.customer_data.postal_code && `, ${workspace.customer_data.postal_code}`}
                    {workspace.customer_data.city && ` ${workspace.customer_data.city}`}
                  </div>
                </div>
                <div className="text-right text-xs text-slate-500 shrink-0">
                  <div>Nr. {workspace.customer_data.partner_number}</div>
                  {workspace.customer_data.debtor_account && <div>Deb. {workspace.customer_data.debtor_account}</div>}
                  {workspace.customer_data.creditor_account && <div>Kred. {workspace.customer_data.creditor_account}</div>}
                </div>
              </div>
            )}

            {instanceId ? (
              <div className="mb-4 rounded-2xl border border-white/10 bg-slate-950/45 p-5">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="space-y-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className={cn('border px-2.5 py-1 text-xs', lifecycleToneClass)}>
                        {lifecycleLabel}
                      </Badge>
                      {workspace.case_number ? (
                        <Badge className="border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-200">
                          {workspace.case_number}
                        </Badge>
                      ) : null}
                      {workspace.business_status ? (
                        <Badge className="border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">
                          {workspace.business_status}
                        </Badge>
                      ) : null}
                    </div>
                    <div className="grid gap-2 text-xs text-slate-400 md:grid-cols-3">
                      <div>
                        <div className="uppercase tracking-[0.18em] text-slate-500">Owner</div>
                        <div className="mt-1 text-slate-200">{workspace.assigned_owner || 'Nicht gesetzt'}</div>
                      </div>
                      <div>
                        <div className="uppercase tracking-[0.18em] text-slate-500">Letzte Aktivitaet</div>
                        <div className="mt-1 text-slate-200">{formatDateTime(workspace.last_activity_at || workspace.updated_at)}</div>
                      </div>
                      <div>
                        <div className="uppercase tracking-[0.18em] text-slate-500">Zusammenfassung</div>
                        <div className="mt-1 text-slate-200">{lifecycleSummary(workspace)}</div>
                      </div>
                    </div>
                    {/*
                      FSX-021: Knoten-ID und Resume-Route sind Technik, keine Fachinformation.
                      Sie bleiben erreichbar — fuer die Fehlersuche sind sie wertvoll —, stehen
                      aber nicht mehr zwischen Status und Kundendaten.
                    */}
                    {workspace.resume_node_id || workspace.active_node_id || workspace.resume_route ? (
                      <details className="rounded-xl border border-white/10 bg-white/3 px-3 py-2">
                        <summary className="cursor-pointer text-xs text-slate-500 hover:text-slate-300">
                          Technische Details
                        </summary>
                        <div className="mt-2 space-y-1 text-xs text-slate-400">
                          <div>
                            Knoten: <span className="text-slate-200">{workspace.resume_node_id || workspace.active_node_id || '—'}</span>
                          </div>
                          {workspace.resume_route ? (
                            <div>
                              Letztes Resume-Ziel: <span className="text-slate-200">{workspace.resume_route}</span>
                            </div>
                          ) : null}
                        </div>
                      </details>
                    ) : null}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button
                      onClick={() => void handleSaveLifecycle()}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch bg-white text-slate-950 hover:bg-white/90"
                    >
                      <Save className="mr-1.5 h-4 w-4" />
                      Speichern
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => void handleResumeLifecycle()}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                    >
                      <PlayCircle className="mr-1.5 h-4 w-4" />
                      Wieder aufnehmen
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => openLifecycleDialog('hold')}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                    >
                      <PauseCircle className="mr-1.5 h-4 w-4" />
                      Pause
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => openLifecycleDialog('complete')}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch border-emerald-400/20 bg-emerald-500/10 text-emerald-100 hover:bg-emerald-500/15"
                    >
                      <CheckCircle2 className="mr-1.5 h-4 w-4" />
                      Abschliessen
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => openLifecycleDialog('cancel')}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch border-rose-400/20 bg-rose-500/10 text-rose-100 hover:bg-rose-500/15"
                    >
                      <XCircle className="mr-1.5 h-4 w-4" />
                      Abbrechen
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => openLifecycleDialog('fail')}
                      disabled={!instanceId || lifecycleBusy || hasTerminalLifecycle}
                      className="min-h-touch border-red-400/20 bg-red-500/10 text-red-100 hover:bg-red-500/15"
                    >
                      <CircleAlert className="mr-1.5 h-4 w-4" />
                      Scheitern
                    </Button>
                  </div>
                </div>
              </div>
            ) : null}

            <div className="rounded-[28px] border border-white/10 bg-white/3 p-8">
              <div className="relative mb-8">
                <div className="absolute left-8 right-8 top-10 h-[2px] rounded-full bg-white/10" />
                <div className="absolute left-8 top-10 h-[2px] rounded-full bg-linear-to-r from-emerald-400 via-indigo-400 to-amber-400" style={{ width: progressWidth }} />
                <div className={cn('relative grid gap-4', nodes.length === 4 ? 'grid-cols-4' : nodes.length === 5 ? 'grid-cols-5' : 'grid-cols-6')}>
                  {nodes.map((node) => {
                    const Icon = ICONS[node.icon as keyof typeof ICONS] ?? Sparkles
                    const active = node.id === selectedNode.id
                    return (
                      <button key={node.id} onClick={() => setSelectedNodeId(node.id)} className={cn('rounded-3xl p-3 text-center transition', active ? 'scale-[1.03]' : 'hover:-translate-y-1')}>
                        <div className={cn('mx-auto flex h-16 w-16 items-center justify-center rounded-full border', toneClasses(node.status), active && 'h-20 w-20')}>
                          <Icon className="h-6 w-6" />
                        </div>
                        <div className="mt-3 text-sm font-semibold text-slate-100">{node.label}</div>
                        {node.status === 'unknown' ? <div className="text-xs text-slate-500">Status nicht ermittelt</div> : null}
                        {/* FSX-003: metric/submetric sind operativ. Fehlen sie, bleibt die
                            Zeile leer statt einen Registry-Vorgabewert zu zeigen. */}
                        {node.metric ? <div className="text-xs text-slate-500">{node.metric}</div> : null}
                        {node.submetric ? <div className="text-[11px] text-slate-400">{node.submetric}</div> : null}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/*
                FSX-020: In 'uebersicht' zaehlt der Prozessverlauf, nicht der einzelne
                Knoten. Die Detailflaeche entfaellt dort ganz — das ist der Unterschied
                zwischen einem Modus und einer Beschriftung.
              */}
              {showNodeDetails ? (
              <div className={cn('grid gap-5', showSideFlaechen && 'xl:grid-cols-[1fr_300px]')}>
                <div className="grid gap-5">
                  {/*
                    FSX-002: Der "KPI Health Score" ist ersatzlos entfallen. Er zeigte einen
                    Fallback von 92 % und eine fest verdrahtete Balkenbreite von ebenfalls
                    92 % — eine Zahl ohne Quelle, die in jedem Vorgang gleich aussah. Eine
                    Kennzahl kehrt erst zurueck, wenn sie an eine benannte Quelle gebunden
                    ist (FSX-001). Mit ihr entfaellt auch die zweite Rasterspalte.
                  */}
                  <Card className="border-white/10 bg-slate-950/50 text-slate-100">
                    <CardHeader className="flex flex-row items-start justify-between gap-4">
                      <div>
                        <CardTitle className="text-xl">Status Details: {selectedNode.label}</CardTitle>
                        <p className="mt-1 text-sm text-slate-400">{selectedNode.insight}</p>
                      </div>
                      <Badge className={cn('border px-2.5 py-1 text-xs', toneClasses(selectedNode.status))}>{selectedNode.status.toUpperCase()}</Badge>
                    </CardHeader>
                    <CardContent className="grid gap-4 md:grid-cols-2">
                      {selectedNode.detail_rows.length > 0 ? (
                        selectedNode.detail_rows.map((row) => (
                          <div key={row.label} className="space-y-1">
                            <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{row.label}</div>
                            <div className="text-sm font-medium text-slate-100">{row.value}</div>
                          </div>
                        ))
                      ) : (
                        <EmptyOperationalField label="Statusdetails" className="md:col-span-2" />
                      )}
                    </CardContent>
                  </Card>

                  {/*
                    FSX-020: In 'fokus' bleibt nur, was zum Weiterarbeiten noetig ist —
                    der Schritt und seine Aktionen. Kennzahlen, Belege und Agentenhinweis
                    sind dort Nebenflaeche.
                  */}
                  <div className={cn('grid gap-4', showSideFlaechen ? 'lg:grid-cols-4' : 'lg:grid-cols-1')}>
                    {showSideFlaechen ? (
                    <>
                    <Card className="border-white/10 bg-white/3 text-slate-100">
                      <CardHeader><CardTitle className="text-sm">KPIs</CardTitle></CardHeader>
                      <CardContent className="space-y-2 text-sm">
                        {selectedNode.kpis.length > 0 ? (
                          selectedNode.kpis.map((kpi) => <div key={kpi.label} className="flex justify-between gap-3"><span className="text-slate-400">{kpi.label}</span><span>{kpi.value}</span></div>)
                        ) : (
                          <EmptyOperationalField label="Kennzahlen" />
                        )}
                      </CardContent>
                    </Card>
                    <Card className="border-white/10 bg-white/3 text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Dokumente</CardTitle></CardHeader>
                      <CardContent className="space-y-2 text-sm">
                        {selectedNode.documents.length > 0 ? (
                          selectedNode.documents.map((doc) => <button key={doc.label} onClick={() => go(doc.href)} className="flex w-full items-center gap-2 text-left text-slate-300 hover:text-white"><FileText className="h-4 w-4 text-muted-foreground" />{doc.label}</button>)
                        ) : (
                          <EmptyOperationalField label="Belege zum Vorgang" />
                        )}
                      </CardContent>
                    </Card>
                    </>
                    ) : null}
                    <Card className="border-white/10 bg-white/3 text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Aktionen</CardTitle></CardHeader>
                      <CardContent className="space-y-3">
                        {selectedNode.actions.map((action) => (
                          <Button
                            key={action.label}
                            onClick={() => void handleAction(action)}
                            disabled={executeAction.isPending}
                            variant={action.variant === 'primary' ? 'default' : 'outline'}
                            className={cn('min-h-touch w-full justify-between', action.variant === 'primary' ? 'bg-indigo-500 text-white hover:bg-indigo-400' : 'border-white/10 bg-white/5 text-slate-200 hover:bg-white/10')}
                          >
                            {action.label}
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        ))}
                      </CardContent>
                    </Card>
                    {showSideFlaechen ? (
                    <Card className="border-indigo-400/20 bg-indigo-500/10 text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Agent</CardTitle></CardHeader>
                      <CardContent className="space-y-3 text-sm">
                        {selectedNode.agent ? (
                          <>
                            <div className="font-semibold text-white">{selectedNode.agent.headline}</div>
                            <p className="text-slate-300">{selectedNode.agent.message}</p>
                            <ul className="space-y-1 text-xs text-slate-300">{selectedNode.agent.reasons.map((reason) => <li key={reason}>- {reason}</li>)}</ul>
                          </>
                        ) : (
                          <EmptyOperationalField label="Agentenbewertung" />
                        )}
                      </CardContent>
                    </Card>
                    ) : null}
                  </div>
                </div>

                {showSideFlaechen ? (
                <div className="space-y-4">
                  <Suspense fallback={null}><AgentProcessPanel domain={workspace.right_panel.domain} className="max-w-none border-white/10 bg-slate-950/50" /></Suspense>
                  <Card className="border-white/10 bg-slate-950/50 text-slate-100">
                    <CardHeader><CardTitle className="text-lg">Linked Modules</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {workspace.right_panel.linked_modules.map((module) => (
                        <button
                          key={module.label}
                          onClick={() => {
                            if (module.api_path) {
                              void executeAction.mutateAsync({ apiPath: module.api_path })
                            }
                            if (module.href) go(module.href)
                          }}
                          className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-sm text-slate-200 hover:bg-white/5"
                        >
                          <span>{module.label}</span>
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        </button>
                      ))}
                    </CardContent>
                  </Card>
                </div>
                ) : null}
              </div>
              ) : null}
            </div>

            {/* FSX-020: Die Fusskarten sind Prozessbeschreibung — in 'fokus' stehen sie im Weg. */}
            {viewMode !== 'fokus' ? (
            <div className="mt-6 grid gap-4 lg:grid-cols-3">
              {workspace.footer_cards.map((card) => {
                const isNextSteps =
                  /schritt/i.test(card.title) || /naechste/i.test(card.title)
                const hasNavigableItems = card.items.some(
                  (item) => flowSpineFooterItemHref(item) !== undefined,
                )
                return (
                <Card key={card.title} className="border-white/10 bg-slate-950/45 text-slate-100">
                  <CardHeader>
                    <CardTitle className="text-base">{card.title}</CardTitle>
                    {isNextSteps && !hasNavigableItems ? (
                      <CardDescription className="text-slate-400">
                        Orientierung — keine Navigation; die Punkte sind als Checkliste gemeint.
                      </CardDescription>
                    ) : null}
                  </CardHeader>
                  <CardContent className="text-sm text-slate-300">
                    <ul
                      className={
                        isNextSteps && !hasNavigableItems
                          ? 'list-disc space-y-1.5 pl-5 marker:text-slate-500'
                          : 'space-y-2'
                      }
                    >
                      {card.items.map((item) => {
                        const label = flowSpineFooterItemLabel(item)
                        const href = flowSpineFooterItemHref(item)
                        if (href) {
                          return (
                            <li key={`${label}:${href}`}>
                              <button
                                type="button"
                                onClick={() => go(href)}
                                className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/5"
                              >
                                <span>{label}</span>
                                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                              </button>
                            </li>
                          )
                        }
                        return (
                          <li
                            key={label}
                            className={
                              isNextSteps
                                ? 'leading-snug'
                                : 'rounded-2xl border border-white/10 px-4 py-3'
                            }
                          >
                            {label}
                          </li>
                        )
                      })}
                    </ul>
                  </CardContent>
                </Card>
              )})}
            </div>
            ) : null}
          </main>

          {/*
            FSX-023: Die Copilot-Spalte hat 360 px dauerhaft belegt und ihre Inhalte
            (Aktionen, Agent, Dokumente) standen bereits in der Mitte. Sie bleibt
            vollstaendig erreichbar, beansprucht aber keinen Platz mehr, solange
            niemand sie aufklappt.
          */}
          <aside
            className={cn(
              'border-l border-white/5 bg-slate-950/45',
              copilotOpen ? 'p-5' : 'flex w-12 flex-col items-center gap-3 py-4',
            )}
          >
            <button
              type="button"
              onClick={() => setCopilotOpen((open) => !open)}
              aria-expanded={copilotOpen}
              aria-label={copilotOpen ? 'Copilot einklappen' : 'Copilot aufklappen'}
              className={cn(
                'rounded-lg text-slate-400 transition hover:bg-white/5 hover:text-slate-100',
                copilotOpen ? 'mb-3 flex w-full items-center justify-between px-2 py-1.5' : 'p-2',
              )}
            >
              {copilotOpen ? (
                <>
                  <span className="text-sm font-semibold text-slate-100">AI Copilot</span>
                  <ArrowLeftRight className="h-4 w-4" />
                </>
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
            </button>
            {!copilotOpen ? (
              <span className="text-2xs uppercase tracking-wide text-slate-500 [writing-mode:vertical-rl]">
                Copilot
              </span>
            ) : null}
            {copilotOpen ? (
            <>
            <Tabs defaultValue="agent" className="flex h-full flex-col">
              <TabsList className="grid w-full grid-cols-5 bg-white/5">
                <TabsTrigger value="agent">Agent</TabsTrigger>
                <TabsTrigger value="actions">Aktionen</TabsTrigger>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
                <TabsTrigger value="docs">Docs</TabsTrigger>
                <TabsTrigger value="kpis">KPIs</TabsTrigger>
              </TabsList>
              <TabsContent value="agent" className="mt-4 space-y-4">
                {!selectedNode.agent ? (
                  <EmptyOperationalField label="Agentenbewertung" />
                ) : (
                <Card className="border-white/10 bg-white/3 text-slate-100">
                  <CardHeader><CardTitle className="text-base">{selectedNode.agent.headline}</CardTitle></CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <p>{selectedNode.agent.message}</p>
                    <div className="space-y-1 text-xs text-slate-300">{selectedNode.agent.reasons.map((reason) => <div key={reason}>- {reason}</div>)}</div>
                    <div className="grid grid-cols-3 gap-2">
                      {selectedNode.agent.actions.map((action) => (
                        <Button
                          key={action}
                          disabled={executeAgentAction.isPending}
                          onClick={() => void handleAgentAction(action)}
                          variant={action === 'Uebernehmen' ? 'default' : 'outline'}
                          className={cn(
                            'min-h-touch',
                            action === 'Uebernehmen' ? 'bg-white text-slate-900 hover:bg-white/90' : 'border-white/10 bg-white/5 text-white hover:bg-white/10',
                          )}
                        >
                          {action}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
                )}
              </TabsContent>
              <TabsContent value="actions" className="mt-4 space-y-3">
                {selectedNode.actions.map((action) => (
                  <Button
                    key={action.label}
                    onClick={() => void handleAction(action)}
                    disabled={executeAction.isPending}
                    className={cn('min-h-touch w-full justify-between', action.variant === 'primary' ? 'bg-indigo-500 text-white hover:bg-indigo-400' : 'border-white/10 bg-white/5 text-slate-200 hover:bg-white/10')}
                    variant={action.variant === 'primary' ? 'default' : 'outline'}
                  >
                    {action.label}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                ))}
              </TabsContent>
              <TabsContent value="timeline" className="mt-4 space-y-3">
                {!instanceId ? (
                  <div className="rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-sm text-slate-400">
                    Timeline verfuegbar, sobald eine konkrete Instanz geladen ist.
                  </div>
                ) : timelineQuery.isLoading ? (
                  <div className="rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-sm text-slate-400">
                    Timeline wird geladen...
                  </div>
                ) : (
                  <div className="space-y-3">
                    {timelineQuery.data?.events.length ? (
                      timelineQuery.data.events.slice().reverse().map((event) => (
                        <div key={event.event_id} className="rounded-2xl border border-white/10 bg-white/3 p-4">
                          <div className="flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2 text-sm font-medium text-slate-100">
                              <History className="h-4 w-4 text-muted-foreground" />
                              {event.event_type}
                            </div>
                            <div className="text-[11px] text-slate-500">{formatDateTime(event.created_at)}</div>
                          </div>
                          <div className="mt-2 space-y-1 text-xs text-slate-400">
                            <div>Status: {event.from_lifecycle_status || '—'} → {event.to_lifecycle_status || '—'}</div>
                            {event.node_id ? <div>Knoten: {event.node_id}</div> : null}
                            {event.reason_code ? <div>Grund: {event.reason_category || '—'} / {event.reason_code}</div> : null}
                            {event.reason_note ? <div>Bemerkung: {event.reason_note}</div> : null}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-sm text-slate-400">
                        Noch keine Timeline-Eintraege vorhanden.
                      </div>
                    )}
                  </div>
                )}
              </TabsContent>
              <TabsContent value="docs" className="mt-4 space-y-3">
                {selectedNode.documents.length === 0 && workspace.right_panel.resources.length === 0 ? (
                  <EmptyOperationalField label="Belege zum Vorgang" />
                ) : null}
                {selectedNode.documents.concat(workspace.right_panel.resources).map((doc) => (
                  <button
                    key={`${doc.label}-${doc.href}`}
                    onClick={() => go(doc.href)}
                    className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/3 px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/5"
                  >
                    <span className="flex items-center gap-2"><FileText className="h-4 w-4 text-muted-foreground" />{doc.label}</span>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </button>
                ))}
              </TabsContent>
              <TabsContent value="kpis" className="mt-4 space-y-3">
                {selectedNode.kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-2xl border border-white/10 bg-white/3 p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{kpi.label}</div>
                    <div className="mt-2 text-lg font-semibold text-white">{kpi.value}</div>
                  </div>
                ))}
              </TabsContent>
            </Tabs>
            </>
            ) : null}
          </aside>
        </div>
      </PageSection>

      {/* Neue Instanz Dialog */}
      <FlowSpineWorkspaceDialogs state={state} />
    </PageSurface>
  )
}

