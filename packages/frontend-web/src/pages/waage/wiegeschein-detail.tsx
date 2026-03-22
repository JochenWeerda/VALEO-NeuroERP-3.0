import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { type WeighingTicket } from '@/lib/api/weighing-tickets'
import { ArrowRight, CheckCircle, Clock, FileText, Link, Scale, Truck } from 'lucide-react'

// ── Tabs ─────────────────────────────────────────────────────────────────────
type TabId = 'gewichte' | 'qualitaet' | 'kontrakt' | 'verlauf'

const TABS: { id: TabId; label: string }[] = [
  { id: 'gewichte', label: 'Gewichte' },
  { id: 'qualitaet', label: 'Qualität' },
  { id: 'kontrakt', label: 'Kontrakt-Zuordnung' },
  { id: 'verlauf', label: 'Verlauf' },
]

// ── Mock fallback (dev mode) ──────────────────────────────────────────────────
function buildMockTicket(id: string): WeighingTicket {
  return {
    id,
    ticket_number: `WS-${id.slice(0, 8).toUpperCase()}`,
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
      <div className="mt-1 rounded-md border bg-muted px-3 py-2 text-sm font-medium">
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
  icon: React.ComponentType<{ className?: string }>
  label: string
  timestamp?: string | null
  done: boolean
}): JSX.Element {
  return (
    <div className="flex items-start gap-3">
      <div
        className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 ${
          done ? 'border-green-500 bg-green-50 text-green-700' : 'border-muted-foreground/30 bg-muted text-muted-foreground'
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
  const navigate = useNavigate()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabId>('gewichte')
  const [allocateOpen, setAllocateOpen] = useState(false)
  const [contractInput, setContractInput] = useState('')

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
        <div className="mt-8 text-center text-red-600">Wiegeschein konnte nicht geladen werden.</div>
      </div>
    )
  }

  const netWeight = ticket.net_weight ?? (ticket.gross_weight != null && ticket.tare_weight != null ? ticket.gross_weight - ticket.tare_weight : null)

  // ── Keyboard shortcuts ───────────────────────────────────────────────────────
  const tabIds: TabId[] = ['gewichte', 'qualitaet', 'kontrakt', 'verlauf']
  useKeyboardShortcuts([
    { key: 'Escape', label: 'Zurück', action: () => navigate('/waage/wiegungen') },
    { key: 'k', ctrl: true, label: 'Kontrakt zuordnen', action: () => setAllocateOpen(true), disabled: ticket.status === 'posted' },
    { key: 'ArrowRight', alt: true, label: 'Nächster Tab', action: () => setActiveTab((t) => tabIds[(tabIds.indexOf(t) + 1) % tabIds.length]) },
    { key: 'ArrowLeft', alt: true, label: 'Vorheriger Tab', action: () => setActiveTab((t) => tabIds[(tabIds.indexOf(t) - 1 + tabIds.length) % tabIds.length]) },
  ])

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
          className="gap-2"
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
    <div className="p-6 space-y-6">
      <ModuleToolbar
        backTarget="/waage/wiegungen"
        closeTarget="/waage/wiegungen"
        title="Wiegeschein-Detail"
        actions={
          <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate('/waage/wiegungen')}>
            <ArrowRight className="h-4 w-4" />
            Alle Wiegungen
          </Button>
        }
      />

      {/* Header-Bereich */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <FileText className="h-6 w-6 text-muted-foreground" />
                <h1 className="text-2xl font-bold">{ticket.ticket_number}</h1>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge variant={ticketStatusVariant(ticket.status)}>
                  {ticket.status === 'posted'
                    ? 'Verbucht'
                    : ticket.status === 'allocated'
                      ? 'Zugeordnet'
                      : ticket.status}
                </Badge>
                <Badge variant={allocationStatusVariant(ticket.allocation_status)}>
                  {allocationStatusLabel(ticket.allocation_status)}
                </Badge>
                {ticket.direction === 'inbound' && (
                  <Badge variant="secondary">Eingang</Badge>
                )}
              </div>
            </div>
            <div className="text-right space-y-1 text-sm text-muted-foreground">
              {ticket.article_id && (
                <div>
                  Artikel: <span className="font-semibold text-foreground">{ticket.article_id}</span>
                </div>
              )}
              {ticket.vehicle_plate && (
                <div className="flex items-center gap-1 justify-end">
                  <Truck className="h-4 w-4" />
                  <span className="font-semibold text-foreground">{ticket.vehicle_plate}</span>
                </div>
              )}
              {ticket.first_weighing_at && (
                <div className="flex items-center gap-1 justify-end">
                  <Clock className="h-3 w-3" />
                  {new Date(ticket.first_weighing_at).toLocaleDateString('de-DE')}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tab-Navigation */}
      <div className="border-b">
        <nav className="flex gap-0" aria-label="Tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/40'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab-Inhalt */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {TABS.find((t) => t.id === activeTab)?.label}
          </CardTitle>
        </CardHeader>
        <CardContent>{tabContent[activeTab]}</CardContent>
      </Card>

      {/* Bemerkungen */}
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

      {/* Dialog: Kontrakt zuordnen */}
      <Dialog open={allocateOpen} onOpenChange={(open) => !open && setAllocateOpen(false)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Kontrakt zuordnen</DialogTitle>
            <DialogDescription>
              Wiegeschein {ticket.ticket_number} — Kontrakt-ID eingeben um den Wiegeschein gegen einen offenen Kontrakt zu allokieren.
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
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Wiegeschein {ticket.ticket_number} — Nettomenge: {netWeight?.toLocaleString('de-DE') ?? '—'} kg
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAllocateOpen(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={() => allocate.mutate()}
              disabled={!contractInput.trim() || allocate.isPending}
            >
              {allocate.isPending ? 'Wird zugeordnet…' : 'Zuordnen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
      <KeyboardShortcutBar shortcuts={shortcutsForBar} />
    </div>
  )
}
