import { useState, type ComponentType } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/typed-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { type WeighingTicket } from '@/lib/api/weighing-tickets'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { ArrowRight, CheckCircle, Clock, FileText, Link, Scale, Truck } from 'lucide-react'
import { readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { WorkflowProcessBand } from '@/components/workflow/WorkflowProcessBand'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

// ── Tabs ─────────────────────────────────────────────────────────────────────
type TabId = 'gewichte' | 'qualitaet' | 'kontrakt' | 'verlauf'

const TABS: { id: TabId; label: string }[] = [
  { id: 'gewichte', label: 'Gewichte' },
  { id: 'qualitaet', label: 'Qualität' },
  { id: 'kontrakt', label: 'Kontrakt' },
  { id: 'verlauf', label: 'Verlauf' },
]

type WeighingDetailRoleFocus = 'all' | 'scale' | 'inbound' | 'dispatch' | 'quality' | 'billing'

const weighingDetailRoleProfiles: Array<{ id: WeighingDetailRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt den Wiegeschein fuer Waage, Annahme, Disposition, QS und Abrechnung.',
  },
  {
    id: 'scale',
    label: 'Waage',
    description: 'Fokus auf Gewichte, Status und Wiegescheinabschluss.',
  },
  {
    id: 'inbound',
    label: 'Annahme',
    description: 'Fokus auf Fahrzeug, Richtung, Artikel und Uebergabe.',
  },
  {
    id: 'dispatch',
    label: 'Disposition',
    description: 'Fokus auf Kontraktzuordnung und Objektkette.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf Feuchte, Protein, Besatz und HL-Gewicht.',
  },
  {
    id: 'billing',
    label: 'Abrechnung',
    description: 'Fokus auf Abrechnungsgewicht, Kontrakt und Settlement.',
  },
]

// ── Mock fallback (dev mode) ──────────────────────────────────────────────────
function buildMockTicket(id: string): WeighingTicket {
  return {
    id,
    ticket_number: id.toUpperCase().startsWith('WS-') ? id.toUpperCase() : `WS-${id.slice(0, 8).toUpperCase()}`,
    scale_id: 'WAAGE-01',
    vehicle_plate: 'AB-CD 1234',
    gross_weight: 28500,
    tare_weight: 6500,
    net_weight: 22000,
    billing_weight: 21450,
    first_weighing_at: new Date(Date.now() - 7200000).toISOString(),
    second_weighing_at: new Date(Date.now() - 3600000).toISOString(),
    moisture_pct: 15.2,
    protein_pct: 12.8,
    impurities_pct: 1.4,
    hl_weight: 78.5,
    contract_id: null,
    allocated_quantity_kg: null,
    allocation_status: 'unallocated',
    status: 'posted',
    direction: 'inbound',
    reference_doc: null,
    article_group: 'Getreide',
    article_id: 'WEIZEN',
    notes: null,
  }
}

// ── Status helpers ────────────────────────────────────────────────────────────
function allocationStatusLabel(status: string | null | undefined): string {
  switch (status) {
    case 'allocated':
      return 'Zugeordnet'
    case 'partially_allocated':
      return 'Teilweise zugeordnet'
    case 'unallocated':
    default:
      return 'Nicht zugeordnet'
  }
}

function allocationStatusVariant(
  status: string | null | undefined,
): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'allocated':
      return 'outline'
    case 'partially_allocated':
      return 'secondary'
    default:
      return 'destructive'
  }
}

function ticketStatusLabel(status: string): string {
  switch (status) {
    case 'posted':
      return 'Verbucht'
    case 'allocated':
      return 'Zugeordnet'
    case 'closed':
      return 'geschlossen'
    case 'open':
      return 'offen'
    default:
      return status
  }
}

function ticketStatusVariant(
  status: string,
): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'posted':
      return 'outline'
    case 'allocated':
      return 'default'
    default:
      return 'secondary'
  }
}

// ── Read-only field ───────────────────────────────────────────────────────────
function ReadField({
  label,
  value,
}: {
  label: string
  value: string | number | null | undefined
}): JSX.Element {
  return (
    <div>
      <Label className="text-xs text-muted-foreground uppercase tracking-wide">{label}</Label>
      <div className="mt-1 min-h-11 rounded-md border bg-muted px-3 py-2 text-base font-medium">
        {value ?? '—'}
      </div>
    </div>
  )
}

// ── Timeline step ─────────────────────────────────────────────────────────────
function TimelineStep({
  icon: Icon,
  label,
  timestamp,
  done,
}: {
  icon: ComponentType<{ className?: string }>
  label: string
  timestamp?: string | null
  done: boolean
}): JSX.Element {
  return (
    <div className="flex items-start gap-3">
      <div
        className={`mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 ${
          done ? 'border-status-success text-status-success' : 'border-muted-foreground/30 bg-muted text-muted-foreground'
        }`}
      >
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className={`text-sm font-medium ${done ? '' : 'text-muted-foreground'}`}>{label}</p>
        {timestamp && (
          <p className="text-xs text-muted-foreground">
            {new Date(timestamp).toLocaleString('de-DE')}
          </p>
        )}
        {!done && !timestamp && (
          <p className="text-xs text-muted-foreground">Ausstehend</p>
        )}
      </div>
    </div>
  )
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function WiegescheinDetailPage(): JSX.Element {
  const { id = '' } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabId>('gewichte')
  const [allocateOpen, setAllocateOpen] = useState(false)
  const [contractInput, setContractInput] = useState('')
  const [roleFocus, setRoleFocus] = useState<WeighingDetailRoleFocus>('all')
  const { data: chain } = useSupplyChainOverview()
  const workflowContext = readWorkflowEntryContext(searchParams)
  const transferSummary = summarizeSupplyTransfer(chain)

  // ── Fetch ticket ────────────────────────────────────────────────────────────
  const {
    data: ticket,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['weighing-tickets', id],
    queryFn: async () => {
      try {
        return (await apiClient.get<WeighingTicket>(`/api/v1/weighing-tickets/${encodeURIComponent(id)}`)).data
      } catch {
        // Dev-mode fallback
        return buildMockTicket(id)
      }
    },
    enabled: Boolean(id),
    staleTime: 30 * 1000,
  })

  // ── Allocate mutation ───────────────────────────────────────────────────────
  const allocate = useMutation({
    mutationFn: async () => {
      return (
        await apiClient.post(`/api/v1/weighing-tickets/${encodeURIComponent(id)}/allocate-contract`, {
          contract_id: contractInput.trim(),
        })
      ).data
    },
    onSuccess: () => {
      toast({ title: 'Kontrakt zugeordnet', description: `Kontrakt ${contractInput} wurde zugeordnet.` })
      void queryClient.invalidateQueries({ queryKey: ['weighing-tickets', id] })
      setAllocateOpen(false)
      setContractInput('')
    },
    onError: (e: unknown) => {
      const message = e instanceof Error ? e.message : 'Zuordnung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    },
  })

  const tabIds: TabId[] = ['gewichte', 'qualitaet', 'kontrakt', 'verlauf']
  useKeyboardShortcuts([
    { key: 'Escape', label: 'Zurück', action: () => navigate('/waage/wiegungen') },
    {
      key: 'k',
      ctrl: true,
      label: 'Kontrakt zuordnen',
      action: () => setAllocateOpen(true),
      disabled: !ticket || ticket.status === 'posted',
    },
    {
      key: 'ArrowRight',
      alt: true,
      label: 'Nächster Tab',
      action: () => setActiveTab((t) => tabIds[(tabIds.indexOf(t) + 1) % tabIds.length]),
    },
    {
      key: 'ArrowLeft',
      alt: true,
      label: 'Vorheriger Tab',
      action: () => setActiveTab((t) => tabIds[(tabIds.indexOf(t) - 1 + tabIds.length) % tabIds.length]),
    },
  ])

  // ── Loading / Error ─────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="p-6">
        <ModuleToolbar backTarget="/waage/wiegungen" closeTarget="/waage/wiegungen" title="Wiegeschein" />
        <div className="mt-8 text-center text-muted-foreground">Lade Wiegeschein…</div>
      </div>
    )
  }

  if (isError || !ticket) {
    return (
      <div className="p-6">
        <ModuleToolbar backTarget="/waage/wiegungen" closeTarget="/waage/wiegungen" title="Wiegeschein" />
        <div className="mt-8 text-center text-status-error">Wiegeschein konnte nicht geladen werden.</div>
      </div>
    )
  }

  const netWeight = ticket.net_weight ?? (ticket.gross_weight != null && ticket.tare_weight != null ? ticket.gross_weight - ticket.tare_weight : null)
  const hasWeights = ticket.gross_weight != null && ticket.tare_weight != null && netWeight != null
  const hasQualityValues = ticket.moisture_pct != null || ticket.protein_pct != null || ticket.impurities_pct != null || ticket.hl_weight != null
  const hasContract = Boolean(ticket.contract_id || ticket.allocation_status === 'allocated' || ticket.allocation_status === 'partially_allocated')
  const isPosted = ticket.status === 'posted' || ticket.status === 'closed'
  const isWeighingDetailReady = hasWeights && hasQualityValues && hasContract
  const weighingDetailNextAction = !hasWeights
    ? 'Brutto, Tara und Nettogewicht pruefen.'
    : !hasQualityValues
      ? 'Qualitaetswerte pruefen oder nachtragen.'
      : !hasContract
        ? 'Kontrakt zuordnen.'
        : !isPosted
          ? 'Wiegeschein abschliessen oder Settlement vorbereiten.'
          : 'Abrechnung fortsetzen.'
  const weighingDetailTaskItems: UxTaskItem[] = [
    {
      label: 'Gewichte pruefen',
      done: hasWeights,
      hint: hasWeights ? `Netto ${netWeight?.toLocaleString('de-DE')} kg.` : 'Brutto, Tara und Netto sind noch nicht vollstaendig.',
    },
    {
      label: 'Qualitaet sichern',
      done: hasQualityValues,
      hint: hasQualityValues ? 'Qualitaetswerte sind vorhanden.' : 'Feuchte, Protein, Besatz oder HL-Gewicht pruefen.',
    },
    {
      label: 'Kontrakt zuordnen',
      done: hasContract,
      hint: hasContract ? `Zuordnung: ${allocationStatusLabel(ticket.allocation_status)}.` : 'Kontrakt ist fuer Abrechnung und Nachweis noch offen.',
    },
    {
      label: 'Abschluss und Settlement',
      done: isPosted,
      hint: isPosted ? 'Wiegeschein ist abgeschlossen oder verbucht.' : 'Nach Kontraktzuordnung Settlement vorbereiten.',
    },
  ]
  const weighingDetailCrudCapabilities = [
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Gewichte, Qualitaet, Kontrakt, Verlauf und Objektkette sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Kontrakt zuordnen',
      available: !isPosted,
      hint: !isPosted ? 'Kontraktzuordnung ist im Detaildialog verfuegbar.' : 'Verbuchte Wiegescheine sind fuer Zuordnung gesperrt.',
    },
    {
      key: 'approve',
      label: 'Abrechnung vorbereiten',
      available: hasContract,
      hint: hasContract ? 'Settlement-Folge kann fortgesetzt werden.' : 'Abrechnung braucht eine Kontraktzuordnung.',
    },
    {
      key: 'evidence',
      label: 'Nachweis',
      available: Boolean(ticket.ticket_number),
      hint: 'Ticketnummer, Gewichte, Qualitaetswerte, Fahrzeug und Kontrakt bilden den Nachweis.',
    },
    {
      key: 'audit',
      label: 'Pruefspur',
      available: true,
      hint: 'Timeline, Status, Zuordnung und Objektkette machen den Vorgang nachvollziehbar.',
    },
  ]

  const shortcutsForBar = [
    { key: 'Escape', label: 'Zurück', action: () => navigate('/waage/wiegungen') },
    { key: 'k', ctrl: true, label: 'Kontrakt zuordnen', action: () => setAllocateOpen(true), disabled: ticket.status === 'posted' },
    { key: '←', alt: true, label: 'Vorheriger Tab', action: () => {} },
    { key: '→', alt: true, label: 'Nächster Tab', action: () => {} },
  ]

  // ── Tab content ─────────────────────────────────────────────────────────────
  const tabContent: Record<TabId, JSX.Element> = {
    gewichte: (
      <div className="grid gap-4 sm:grid-cols-2">
        <ReadField label="Bruttogewicht (kg)" value={ticket.gross_weight?.toLocaleString('de-DE')} />
        <ReadField label="Taragewicht (kg)" value={ticket.tare_weight?.toLocaleString('de-DE')} />
        <ReadField label="Nettogewicht (kg)" value={netWeight?.toLocaleString('de-DE')} />
        <ReadField
          label="Abrechnungsgewicht (kg)"
          value={ticket.billing_weight?.toLocaleString('de-DE')}
        />
      </div>
    ),
    qualitaet: (
      <div className="grid gap-4 sm:grid-cols-2">
        <ReadField
          label="Feuchte %"
          value={ticket.moisture_pct != null ? `${ticket.moisture_pct.toFixed(1)} %` : null}
        />
        <ReadField
          label="Protein %"
          value={ticket.protein_pct != null ? `${ticket.protein_pct.toFixed(1)} %` : null}
        />
        <ReadField
          label="Besatz %"
          value={ticket.impurities_pct != null ? `${ticket.impurities_pct.toFixed(1)} %` : null}
        />
        <ReadField
          label="HL-Gewicht"
          value={ticket.hl_weight != null ? `${ticket.hl_weight.toFixed(1)} kg/hl` : null}
        />
      </div>
    ),
    kontrakt: (
      <div className="space-y-4">
        <div className="rounded-md border p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Zuordnungsstatus</span>
            <Badge variant={allocationStatusVariant(ticket.allocation_status)}>
              {allocationStatusLabel(ticket.allocation_status)}
            </Badge>
          </div>
          {ticket.contract_id && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Kontrakt-ID</span>
              <span className="font-semibold font-mono">{ticket.contract_id}</span>
            </div>
          )}
          {ticket.allocated_quantity_kg != null && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Zugeordnete Menge</span>
              <span className="font-semibold">
                {ticket.allocated_quantity_kg.toLocaleString('de-DE')} kg
              </span>
            </div>
          )}
        </div>
        <Button
          variant="outline"
          className="min-h-touch gap-2 touch-manipulation"
          onClick={() => setAllocateOpen(true)}
          disabled={ticket.status === 'posted'}
        >
          <Link className="h-4 w-4" />
          Kontrakt zuordnen
        </Button>
        {ticket.status === 'posted' && (
          <p className="text-xs text-muted-foreground">
            Bereits verbuchte Wiegescheine können nicht mehr zugeordnet werden.
          </p>
        )}
      </div>
    ),
    verlauf: (
      <div className="space-y-4">
        <TimelineStep
          icon={Truck}
          label="Ersterfassung (Erstwiegung)"
          timestamp={ticket.first_weighing_at}
          done={Boolean(ticket.first_weighing_at)}
        />
        <div className="ml-4 border-l-2 border-muted h-4" />
        <TimelineStep
          icon={Scale}
          label="Qualitätsprüfung / Zweitwiegung"
          timestamp={ticket.second_weighing_at}
          done={Boolean(ticket.second_weighing_at)}
        />
        <div className="ml-4 border-l-2 border-muted h-4" />
        <TimelineStep
          icon={Link}
          label="Kontrakt-Zuordnung"
          timestamp={undefined}
          done={ticket.allocation_status === 'allocated' || ticket.allocation_status === 'partially_allocated'}
        />
        <div className="ml-4 border-l-2 border-muted h-4" />
        <TimelineStep
          icon={CheckCircle}
          label="Verbucht / Abgeschlossen"
          timestamp={undefined}
          done={ticket.status === 'posted'}
        />
      </div>
    ),
  }

  return (
    <div className="flex flex-col">
    <div className="space-y-6 p-3 md:p-6">
      <ModuleToolbar
        backTarget="/waage/wiegungen"
        closeTarget="/waage/wiegungen"
        title="Wiegeschein"
        actions={
          <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={() => navigate('/waage/wiegungen')}>
            <ArrowRight className="h-4 w-4" />
            Alle Wiegungen
          </Button>
        }
      />

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <FileText className="h-6 w-6 shrink-0 text-muted-foreground" />
                <h1 className="text-2xl font-bold">{ticket.ticket_number}</h1>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge variant={ticketStatusVariant(ticket.status)}>
                  {ticketStatusLabel(ticket.status)}
                </Badge>
                <Badge variant={allocationStatusVariant(ticket.allocation_status)}>
                  {allocationStatusLabel(ticket.allocation_status)}
                </Badge>
                {ticket.direction === 'inbound' && (
                  <Badge variant="secondary">Eingang</Badge>
                )}
              </div>
            </div>
            <div className="space-y-1 text-sm text-muted-foreground sm:text-right">
              {ticket.article_id && (
                <div>
                  Artikel: <span className="font-semibold text-foreground">{ticket.article_id}</span>
                </div>
              )}
              {ticket.vehicle_plate && (
                <div className="flex items-center gap-1 sm:justify-end">
                  <Truck className="h-4 w-4" />
                  <span className="font-semibold text-foreground">{ticket.vehicle_plate}</span>
                </div>
              )}
              {ticket.first_weighing_at && (
                <div className="flex items-center gap-1 sm:justify-end">
                  <Clock className="h-4 w-4" />
                  {new Date(ticket.first_weighing_at).toLocaleDateString('de-DE')}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabId)}>
        <TabsList variant="register" className="flex-wrap" aria-label="Wiegeschein">
          {TABS.map((tab) => (
            <TabsTrigger key={tab.id} value={tab.id} className="min-h-11">
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {TABS.map((tab) => (
          <TabsContent key={tab.id} value={tab.id}>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{tab.label}</CardTitle>
              </CardHeader>
              <CardContent>{tabContent[tab.id]}</CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {ticket.notes && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Bemerkungen</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{ticket.notes}</p>
          </CardContent>
        </Card>
      )}

      {!isTouch ? (
      <div className="space-y-6">
      {workflowContext ? <WorkflowProcessBand context={workflowContext} /> : null}
      <OperationalCaseHeader
        title={ticket.ticket_number}
        description="Wiegeschein als operativer Brueckenvorgang zwischen Annahme, Qualitaet, Kontrakt und Abrechnung."
        status={ticket.allocation_status === 'unallocated' ? 'wartet_auf_mensch' : normalizeOperationalStatus(ticket.status)}
        owner="Waage / Disposition"
        blocker={ticket.allocation_status === 'unallocated' ? 'Der Wiegeschein ist noch keinem Kontrakt zugeordnet.' : null}
        nextAction={ticket.allocation_status === 'unallocated' ? 'Kontrakt zuordnen' : 'Abrechnung fortsetzen'}
        caseLabel={workflowContext?.caseNumber || 'Wiegevorgang'}
        tags={[ticket.direction, ticket.article_group || 'Artikelgruppe offen']}
      />
      <RoleFocusBar
        roles={weighingDetailRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: isWeighingDetailReady,
          allowedLabel: 'Abrechnungsbereit',
          blockedLabel: 'Stopper offen',
          summary: isWeighingDetailReady
            ? `Gewichte, Qualitaet und Kontrakt sind vorhanden. ${weighingDetailNextAction}`
            : `Vor der Abrechnung ist noch etwas offen: ${weighingDetailNextAction}`,
          blockerCount: [!hasWeights, !hasQualityValues, !hasContract].filter(Boolean).length,
          nextFocus: weighingDetailNextAction,
          template: {
            label: 'Wiegungen oeffnen',
            href: '/waage/wiegungen',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Wiegeschein-Aufgabenplan" items={weighingDetailTaskItems} />
        <div className="space-y-3">
          <NextActionPanel
            action={weighingDetailNextAction}
            tone={isWeighingDetailReady ? 'emerald' : !hasContract ? 'amber' : 'blue'}
          />
          <EvidenceTemplateLink link={{ label: 'Wiegungen oeffnen', href: '/waage/wiegungen' }} />
        </div>
      </div>
      <CrudCapabilityChecklist capabilities={weighingDetailCrudCapabilities} />
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Objektkette zu diesem Wiegeschein</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <div><div className="text-xs text-muted-foreground">Wartende Annahmen</div><div className="text-2xl font-semibold">{chain?.waitingInbound ?? 0}</div></div>
          <div><div className="text-xs text-muted-foreground">Offene Wiegungen</div><div className="text-2xl font-semibold">{chain?.openWeighingTickets ?? 0}</div></div>
          <div><div className="text-xs text-muted-foreground">Gesperrte Chargen</div><div className="text-2xl font-semibold">{chain?.blockedCharges ?? 0}</div></div>
          <div><div className="text-xs text-muted-foreground">Fracht in Transit</div><div className="text-2xl font-semibold">{chain?.freightInTransit ?? 0}</div></div>
        </CardContent>
      </Card>
      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
        <OperationalTimeline
          title="Vorgangstimeline"
          items={[
            { label: 'Erstwiegung', timestamp: ticket.first_weighing_at, detail: ticket.vehicle_plate || undefined },
            { label: 'Zweitwiegung', timestamp: ticket.second_weighing_at, detail: ticket.ticket_number },
            { label: 'Objektkettenabgleich', detail: `${chain?.waitingInbound ?? 0} wartend / ${chain?.openWeighingTickets ?? 0} offen / ${chain?.freightInTransit ?? 0} Transit` },
          ]}
        />
        <OperationalContextPanel
          title="Wiegescheinkontext"
          sections={[
            {
              title: 'Ressourcenlage',
              items: [
                { label: 'Nettogewicht', value: netWeight != null ? `${netWeight.toLocaleString('de-DE')} kg` : '-' },
                { label: 'Artikel', value: ticket.article_group || ticket.article_id || '-' },
              ],
            },
            {
              title: 'Logistiklage',
              items: [
                { label: 'Fahrzeug', value: ticket.vehicle_plate || '-' },
                { label: 'Richtung', value: ticket.direction || '-' },
              ],
            },
            {
              title: 'Governance',
              items: [
                { label: 'Zuordnung', value: allocationStatusLabel(ticket.allocation_status) },
                { label: 'Naechster Schritt', value: ticket.allocation_status === 'unallocated' ? 'Kontrakt zuordnen' : 'Settlement vorbereiten' },
              ],
            },
          ]}
        />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Uebergabedruck</CardTitle></CardHeader>
          <CardContent><Badge variant={transferSummary.transferPressure === 'hoch' ? 'destructive' : 'outline'}>{transferSummary.transferPressure}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Offene Kettenpunkte</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{transferSummary.handoverRisk}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Kettenaktion</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{transferSummary.nextAction}</div></CardContent>
        </Card>
      </div>
      </div>
      ) : null}

      <Dialog open={allocateOpen} onOpenChange={(open) => !open && setAllocateOpen(false)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Kontrakt zuordnen</DialogTitle>
            <DialogDescription>
              Wiegeschein {ticket.ticket_number} — Kontrakt-ID eingeben, um den Wiegeschein einem offenen Kontrakt zuzuordnen.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="contract-id">Kontrakt-ID</Label>
              <Input
                id="contract-id"
                value={contractInput}
                onChange={(e) => setContractInput(e.target.value)}
                placeholder="z.B. KT-2026-0042"
                autoFocus
                className="min-h-touch"
              />
            </div>
            <p className="text-sm text-muted-foreground">
              Wiegeschein {ticket.ticket_number} — Nettomenge: {netWeight?.toLocaleString('de-DE') ?? '—'} kg
            </p>
          </div>
          <DialogFooter className="flex flex-wrap gap-2">
            <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => setAllocateOpen(false)}>
              Abbrechen
            </Button>
            <Button
              className="min-h-touch touch-manipulation"
              onClick={() => allocate.mutate()}
              disabled={!contractInput.trim() || allocate.isPending}
            >
              {allocate.isPending ? 'Wird zugeordnet…' : 'Zuordnen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcutsForBar} /> : null}
    </div>
  )
}
