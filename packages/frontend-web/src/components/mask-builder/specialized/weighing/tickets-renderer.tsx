import { canDomainAction, fieldsEditable } from '../intake/domain-runtime'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState } from '@/components/ErrorState'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'

import { type WeighingTicket } from '@/lib/api/weighing-tickets'

import { Scale, Search, Plus, Link2 } from 'lucide-react'

import { CrudCapabilityChecklist, EvidenceTemplateLink, ManagementDecisionPanel, NextActionPanel, OperationalTaskPlan, RoleFocusBar } from '@/components/workflow'

type WeighingRoleFocus = 'all' | 'scale' | 'inbound' | 'dispatch' | 'quality' | 'billing'

const weighingRoleProfiles: Array<{ id: WeighingRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Waagearbeit fuer Waage, Annahme, Disposition, QS und Abrechnung.',
  },
  {
    id: 'scale',
    label: 'Waage',
    description: 'Fokus auf Ticketnummer, Waage, Kennzeichen, Brutto, Tara und Abschluss.',
  },
  {
    id: 'inbound',
    label: 'Annahme',
    description: 'Fokus auf wartende Anlieferungen, Fahrzeug und Rueckstand.',
  },
  {
    id: 'dispatch',
    label: 'Disposition',
    description: 'Fokus auf Kontraktzuordnung, offene Tickets und Folgepfad.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf Feuchte, Besatz und gesperrte Chargen.',
  },
  {
    id: 'billing',
    label: 'Abrechnung',
    description: 'Fokus auf Abrechnungsgewicht, Kontrakt und Settlement-Folge.',
  },
]

type NewTicketForm = {
  ticketNumber: string
  scaleId: string
  vehiclePlate: string
  grossWeight: number
  tareWeight: number
  moisturePct: number
  impuritiesPct: number
}

const initialForm: NewTicketForm = {
  ticketNumber: '',
  scaleId: '',
  vehiclePlate: '',
  grossWeight: 0,
  tareWeight: 0,
  moisturePct: 0,
  impuritiesPct: 0,
}

import type { TicketsState } from './tickets-controller'
export function TicketsRenderer({ state }: { state: TicketsState }): JSX.Element {
  const { plan, isTouch, searchTerm, setSearchTerm, selectedTicketId, setSelectedTicketId, selectedContractId, setSelectedContractId, form, setForm, roleFocus, setRoleFocus, searchRef, ticketNumberRef, chain, ticketsQuery, contractsQuery, createMutation, updateMutation, allocateMutation, tickets, filteredTickets, totalNetKg, totalBillingKg, openTickets, ticketsWithoutContract, hasCreateInput, hasWeightInput, hasAllocationInput, canProceedWeighing, weighingNextAction, weighingTaskItems, weighingCrudCapabilities, fallkopf, onCreate, onSetSecondWeighing, onAllocate, shortcuts } = state
  if (ticketsQuery.isError) {
    return <ErrorState error={ticketsQuery.error as Error} onRetry={() => { void ticketsQuery.refetch() }} />
  }

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-3 md:p-6">

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neuen Wiegeschein anlegen</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div>
            <Label htmlFor="ticketNumber">{plan.fieldsByKey.ticketNumber.label}</Label>
            <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.ticketNumber.readOnly} id="ticketNumber" ref={ticketNumberRef} value={form.ticketNumber} onChange={(e) => setForm((p) => ({ ...p, ticketNumber: e.target.value }))} />
          </div>
          <div>
            <Label htmlFor="scaleId">{plan.fieldsByKey.scaleId.label}</Label>
            <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.scaleId.readOnly} id="scaleId" value={form.scaleId} onChange={(e) => setForm((p) => ({ ...p, scaleId: e.target.value }))} />
          </div>
          <div>
            <Label htmlFor="vehiclePlate">{plan.fieldsByKey.vehiclePlate.label}</Label>
            <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.vehiclePlate.readOnly} id="vehiclePlate" value={form.vehiclePlate} onChange={(e) => setForm((p) => ({ ...p, vehiclePlate: e.target.value }))} />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label htmlFor="grossWeight">{plan.fieldsByKey.grossWeight.label}</Label>
              {/* Touch-optimized: h-14 ≥ 44px touch target (Gap 024) */}
              <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.grossWeight.readOnly} id="grossWeight" type="number" inputMode="decimal" value={form.grossWeight} onChange={(e) => setForm((p) => ({ ...p, grossWeight: Number(e.target.value) }))} className="h-14 text-base" />
            </div>
            <div>
              <Label htmlFor="tareWeight">{plan.fieldsByKey.tareWeight.label}</Label>
              <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.tareWeight.readOnly} id="tareWeight" type="number" inputMode="decimal" value={form.tareWeight} onChange={(e) => setForm((p) => ({ ...p, tareWeight: Number(e.target.value) }))} className="h-14 text-base" />
            </div>
          </div>
          <div>
            <Label htmlFor="moisturePct">{plan.fieldsByKey.moisturePct.label}</Label>
            <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.moisturePct.readOnly} id="moisturePct" type="number" inputMode="decimal" step="0.1" value={form.moisturePct} onChange={(e) => setForm((p) => ({ ...p, moisturePct: Number(e.target.value) }))} className="h-14 text-base" />
          </div>
          <div>
            <Label htmlFor="impuritiesPct">{plan.fieldsByKey.impuritiesPct.label}</Label>
            <Input disabled={!canDomainAction(plan, 'create') || plan.fieldsByKey.impuritiesPct.readOnly} id="impuritiesPct" type="number" inputMode="decimal" step="0.1" value={form.impuritiesPct} onChange={(e) => setForm((p) => ({ ...p, impuritiesPct: Number(e.target.value) }))} className="h-14 text-base" />
          </div>
          <div className="md:col-span-2 flex items-end">
            <Button size="touch" className="gap-2" onClick={() => { void onCreate() }} disabled={createMutation.isPending || !canDomainAction(plan, 'create') || !fieldsEditable(plan, ['ticketNumber', 'scaleId', 'vehiclePlate', 'grossWeight', 'tareWeight', 'moisturePct', 'impuritiesPct'])}>
              <Plus className="h-5 w-5" />
              Anlegen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Kontrakt zuordnen</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <div>
            <Label htmlFor="selectTicket">Ticket</Label>
            <select
              disabled={plan.fieldsByKey.selectedTicketId.readOnly} id="selectTicket"
              className="mt-1 h-14 w-full rounded-md border bg-background px-3 text-base"
              value={selectedTicketId}
              onChange={(e) => setSelectedTicketId(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              {tickets.filter((t) => !t.contract_id).map((ticket) => (
                <option key={ticket.id} value={ticket.id}>
                  {ticket.ticket_number} | {ticket.vehicle_plate ?? '-'} | {(ticket.billing_weight ?? ticket.net_weight ?? 0).toFixed(3)} kg
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="selectContract">Offener Kontrakt</Label>
            <select
              disabled={plan.fieldsByKey.selectedContractId.readOnly} id="selectContract"
              className="mt-1 h-14 w-full rounded-md border bg-background px-3 text-base"
              value={selectedContractId}
              onChange={(e) => setSelectedContractId(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              {(contractsQuery.data ?? []).map((contract) => (
                <option key={contract.id} value={contract.id}>
                  {contract.contract_number} | Rest: {contract.remaining_quantity_kg.toFixed(3)} kg
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button size="touch" className="gap-2" onClick={() => { void onAllocate() }} disabled={allocateMutation.isPending || !canDomainAction(plan, 'allocate') || !fieldsEditable(plan, ['selectedTicketId', 'selectedContractId'])}>
              <Link2 className="h-5 w-5" />
              Zuordnen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={searchRef}
              aria-label="Wiegeschein suchen"
              placeholder="Ticket, Kennzeichen, Waage..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="min-h-touch pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable
            data={filteredTickets}
            columns={[
              { key: 'ticket_number', label: 'Ticket' },
              { key: 'vehicle_plate', label: 'Kennzeichen' },
              { key: 'scale_id', label: 'Waage' },
              { key: 'gross_weight', label: 'Brutto (kg)' },
              { key: 'tare_weight', label: 'Tara (kg)' },
              {
                key: 'net_weight',
                label: 'Netto (kg)',
                render: (t: WeighingTicket) => <span className="font-semibold">{(t.net_weight ?? 0).toFixed(3)}</span>,
              },
              {
                key: 'billing_weight',
                label: 'Abrechnung (kg)',
                render: (t: WeighingTicket) => (t.billing_weight ?? t.net_weight ?? 0).toFixed(3),
              },
              {
                key: 'status',
                label: 'Status',
                render: (t: WeighingTicket) => <Badge variant={t.status === 'closed' ? 'outline' : 'secondary'}>{t.status === 'closed' ? 'geschlossen' : 'offen'}</Badge>,
              },
              {
                key: 'allocation_status',
                label: 'Kontrakt',
                render: (t: WeighingTicket) => (
                  <Badge variant={t.contract_id ? 'outline' : 'secondary'}>
                    {t.contract_id ? 'zugeordnet' : (t.allocation_status ?? 'offen')}
                  </Badge>
                ),
              },
              {
                key: 'actions',
                label: 'Aktion',
                render: (t: WeighingTicket) => (
                  <Button
                    variant="outline"
                    className="min-h-touch touch-manipulation"
                    disabled={!canDomainAction(plan, 'close') || (updateMutation.isPending && updateMutation.variables?.id === t.id) || t.status === 'closed'}
                    onClick={() => { void onSetSecondWeighing(t) }}
                  >
                    Schließen
                  </Button>
                ),
              },
            ]}
          />
        </CardContent>
      </Card>

      {!isTouch ? (
      <div className="space-y-4">
        <RoleFocusBar
          roles={weighingRoleProfiles}
          value={roleFocus}
          onChange={setRoleFocus}
          visibleCount={roleFocus === 'all' ? 5 : 1}
          totalCount={5}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: canProceedWeighing,
            allowedLabel: 'Bearbeitbar',
            blockedLabel: 'Stopper offen',
            summary: canProceedWeighing
              ? `Die Waagearbeit kann fortgesetzt werden. ${tickets.length} Tickets, ${openTickets} offen, ${ticketsWithoutContract} ohne Kontrakt.`
              : `Vor der naechsten Buchung ist noch etwas offen: ${weighingNextAction}`,
            blockerCount: [!hasCreateInput, !hasWeightInput, ticketsWithoutContract > 0 && !hasAllocationInput].filter(Boolean).length,
            nextFocus: weighingNextAction,
            template: {
              label: 'Hofliste oeffnen',
              href: '/waage/hofliste',
            },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Waage-Aufgabenplan" items={weighingTaskItems} />
          <div className="space-y-3">
            <NextActionPanel
              action={weighingNextAction}
              tone={canProceedWeighing ? 'emerald' : ticketsWithoutContract > 0 ? 'amber' : 'blue'}
            />
            <EvidenceTemplateLink link={{ label: 'Wiegescheinliste pruefen', href: '/waage/liste' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={weighingCrudCapabilities} />

        <Card className={`border ${fallkopf.statusColor}`}>
          <CardContent className="pt-4 pb-3 text-sm space-y-1">
            <div className="font-semibold">Wiegungen: {fallkopf.status}</div>
            <div>Rueckstand: {fallkopf.rueckstand}</div>
            <div>Blocker: {fallkopf.blocker}</div>
            <div>Folgepfad: {fallkopf.folgepfad}</div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Wiegescheine</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-bold">{tickets.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Netto gesamt (kg)</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{totalNetKg.toFixed(3)}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Abrechnungsgewicht (kg)</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{totalBillingKg.toFixed(3)}</span>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Wartende Annahmen</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain?.waitingInbound ?? 0}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Wiegungen</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain?.openWeighingTickets ?? 0}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesperrte Chargen</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain?.blockedCharges ?? 0}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Fracht in Transit</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain?.freightInTransit ?? 0}</span></CardContent>
          </Card>
        </div>
      </div>
      ) : null}
    </div>
      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </div>
  )
}
