import { useDomainSupplyChain, useDomainTickets, useDomainContracts } from '../intake/domain-data'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable, useDomainDispatch } from '../intake/domain-runtime'
import { useMemo, useRef, useState } from 'react'

import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'
import { useAllocateContract, useCreateWeighingTicket, useUpdateWeighingTicket, type WeighingTicket } from '@/lib/api/weighing-tickets'

import { useTouchDevice } from '@/hooks/useTouchDevice'
import { type UxTaskItem } from '@/components/workflow'

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

export function useTicketsController(plan: RenderPlan) {
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTicketId, setSelectedTicketId] = useState<string>('')
  const [selectedContractId, setSelectedContractId] = useState<string>('')
  const [form, setForm] = useState<NewTicketForm>(initialForm)
  const [roleFocus, setRoleFocus] = useState<WeighingRoleFocus>('all')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const ticketNumberRef = useRef<HTMLInputElement | null>(null)
  const { data: chain } = useDomainSupplyChain()

  const ticketsQuery = useDomainTickets()
  const contractsQuery = useDomainContracts()
  const createMutation = useCreateWeighingTicket()
  const updateMutation = useUpdateWeighingTicket()
  const allocateMutation = useAllocateContract()

  const tickets = ticketsQuery.data?.items ?? []
  const filteredTickets = useMemo(
    () =>
      tickets.filter((ticket) => {
        const s = searchTerm.toLowerCase().trim()
        if (!s) return true
        return (
          ticket.ticket_number.toLowerCase().includes(s)
          || (ticket.vehicle_plate ?? '').toLowerCase().includes(s)
          || (ticket.scale_id ?? '').toLowerCase().includes(s)
        )
      }),
    [tickets, searchTerm],
  )

  const totalNetKg = tickets.reduce((sum, t) => sum + Number(t.net_weight ?? 0), 0)
  const totalBillingKg = tickets.reduce((sum, t) => sum + Number(t.billing_weight ?? t.net_weight ?? 0), 0)
  const openTickets = tickets.filter((t) => t.status !== 'closed').length
  const ticketsWithoutContract = tickets.filter((t) => !t.contract_id).length
  const hasCreateInput = Boolean(form.ticketNumber.trim() && form.scaleId.trim())
  const hasWeightInput = form.grossWeight > 0 && form.tareWeight >= 0
  const hasAllocationInput = Boolean(selectedTicketId && selectedContractId)
  const canProceedWeighing = (hasCreateInput && hasWeightInput) || ticketsWithoutContract === 0
  const weighingNextAction = !hasCreateInput
    ? 'Ticketnummer, Waage und Kennzeichen fuer die naechste Wiegung erfassen.'
    : !hasWeightInput
      ? 'Brutto- und Taragewicht pruefen.'
      : ticketsWithoutContract > 0 && !hasAllocationInput
        ? 'Offenes Ticket und passenden Kontrakt auswaehlen.'
        : openTickets > 0
          ? 'Offene Tickets schliessen oder zweites Gewicht buchen.'
          : 'Wiegung anlegen oder Kontraktzuordnung fortsetzen.'
  const weighingTaskItems: UxTaskItem[] = [
    {
      label: 'Ticket vorbereiten',
      done: hasCreateInput,
      hint: hasCreateInput ? `Ticket ${form.ticketNumber || 'neu'} auf Waage ${form.scaleId}.` : 'Ticketnummer und Waage sind Pflicht fuer eine neue Wiegung.',
    },
    {
      label: 'Gewichte und Qualitaet pruefen',
      done: hasWeightInput,
      hint: hasWeightInput ? `Brutto ${form.grossWeight} kg, Tara ${form.tareWeight} kg, Feuchte ${form.moisturePct} %, Besatz ${form.impuritiesPct} %. ` : 'Gewichte sowie Feuchte/Besatz vor der Anlage pruefen.',
    },
    {
      label: 'Kontrakt zuordnen',
      done: ticketsWithoutContract === 0 || hasAllocationInput,
      hint: ticketsWithoutContract === 0 ? 'Alle Tickets sind zugeordnet.' : `${ticketsWithoutContract} Tickets brauchen eine Kontraktzuordnung.`,
    },
    {
      label: 'Abschluss sichern',
      done: openTickets === 0 && tickets.length > 0,
      hint: openTickets === 0 && tickets.length > 0 ? 'Alle Wiegungen sind abgeschlossen.' : `${openTickets} Wiegungen sind noch offen.`,
    },
  ]
  const weighingCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: hasCreateInput && hasWeightInput,
      hint: hasCreateInput && hasWeightInput ? 'Neuer Wiegeschein kann angelegt werden.' : 'Ticketnummer, Waage und Gewichte fehlen noch.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Tickets, Gewichte, Kontrakte, Status und Supply-Chain-Kennzahlen sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Schliessen',
      available: openTickets > 0,
      hint: openTickets > 0 ? 'Offene Tickets koennen geschlossen werden.' : 'Keine offenen Tickets zum Schliessen.',
    },
    {
      key: 'allocate',
      label: 'Kontraktzuordnung',
      available: ticketsWithoutContract > 0,
      hint: ticketsWithoutContract > 0 ? 'Tickets ohne Kontrakt koennen allokiert werden.' : 'Alle Tickets sind bereits zugeordnet.',
    },
    {
      key: 'evidence',
      label: 'Nachweis',
      available: tickets.length > 0,
      hint: tickets.length > 0 ? 'Wiegescheinnummer, Gewichtsdaten und Kontrakt bilden den Nachweis.' : 'Nachweis entsteht mit dem ersten Ticket.',
    },
    {
      key: 'audit',
      label: 'Pruefspur',
      available: true,
      hint: 'Status, Kontrakt, Schliessen-Aktion und Gewichtsdaten sind nachvollziehbar.',
    },
  ]

  const fallkopf = useMemo(() => {
    const offeneTickets = tickets.filter((t) => t.status !== 'closed').length
    const ohneKontrakt = tickets.filter((t) => !t.contract_id).length
    const total = tickets.length
    return {
      status: offeneTickets > 0 ? `${offeneTickets} offene Wiegung(en)` : total > 0 ? 'Alle Wiegungen abgeschlossen' : 'Keine Wiegungen',
      statusColor: offeneTickets > 0 ? 'text-amber-700 bg-amber-50 border-amber-300' : 'text-green-700 bg-green-50 border-green-300',
      rueckstand: offeneTickets > 0 ? `${offeneTickets} Ticket(s) noch offen` : 'Kein Rueckstand',
      blocker: ohneKontrakt > 0 ? `${ohneKontrakt} Ticket(s) ohne Kontraktzuordnung` : 'Alle Tickets zugeordnet',
      folgepfad: offeneTickets > 0 ? 'Offene Tickets schliessen' : ohneKontrakt > 0 ? 'Kontraktzuordnung durchfuehren' : 'Keine dringende Aktion',
    }
  }, [tickets])

  async function onCreate(): Promise<void> {
    if (!canDomainAction(plan, 'create') || !fieldsEditable(plan, ['ticketNumber', 'scaleId', 'vehiclePlate', 'grossWeight', 'tareWeight', 'moisturePct', 'impuritiesPct'])) return
    if (!form.ticketNumber.trim()) {
      toast({ title: 'Fehlende Ticketnummer', description: 'ticket_number ist erforderlich', variant: 'destructive' })
      return
    }
    try {
      await createMutation.mutateAsync({
        ticket_number: form.ticketNumber.trim(),
        scale_id: form.scaleId.trim() || undefined,
        vehicle_plate: form.vehiclePlate.trim() || undefined,
        gross_weight: form.grossWeight,
        tare_weight: form.tareWeight,
        moisture_pct: form.moisturePct,
        impurities_pct: form.impuritiesPct,
        direction: 'in',
      })
      toast({ title: 'Wiegeschein erstellt', description: 'Datensatz wurde persistiert.' })
      setForm(initialForm)
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Erstellung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  async function onSetSecondWeighing(ticket: WeighingTicket): Promise<void> {
    if (!canDomainAction(plan, 'close')) return
    try {
      await updateMutation.mutateAsync({
        id: ticket.id,
        payload: { status: 'closed' },
      })
      toast({ title: 'Status aktualisiert', description: `Ticket ${ticket.ticket_number} geschlossen.` })
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Update fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  async function onAllocate(): Promise<void> {
    if (!canDomainAction(plan, 'allocate') || !fieldsEditable(plan, ['selectedTicketId', 'selectedContractId'])) return
    if (!selectedTicketId || !selectedContractId) {
      toast({ title: 'Zuordnung fehlt', description: 'Bitte Ticket und Kontrakt auswählen.', variant: 'destructive' })
      return
    }
    try {
      await allocateMutation.mutateAsync({
        ticketId: selectedTicketId,
        contractId: selectedContractId,
      })
      toast({ title: 'Kontrakt zugeordnet', description: 'Wiegeschein wurde gegen Kontrakt allokiert.' })
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Kontraktzuordnung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void onCreate() },
    onSearch: () => searchRef.current?.focus(),
    onNew: () => ticketNumberRef.current?.focus(),
    onRefresh: () => { void ticketsQuery.refetch() },
    isSaveDisabled: createMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  useDomainDispatch(plan, { create: onCreate, allocate: onAllocate, close: async () => { const ticket = tickets.find(item => item.id === selectedTicketId); if (ticket) await onSetSecondWeighing(ticket) }, refresh: () => { void ticketsQuery.refetch() } })
  return { plan, isTouch, searchTerm, setSearchTerm, selectedTicketId, setSelectedTicketId, selectedContractId, setSelectedContractId, form, setForm, roleFocus, setRoleFocus, searchRef, ticketNumberRef, chain, ticketsQuery, contractsQuery, createMutation, updateMutation, allocateMutation, tickets, filteredTickets, totalNetKg, totalBillingKg, openTickets, ticketsWithoutContract, hasCreateInput, hasWeightInput, hasAllocationInput, canProceedWeighing, weighingNextAction, weighingTaskItems, weighingCrudCapabilities, fallkopf, onCreate, onSetSecondWeighing, onAllocate, shortcuts }
}
export type TicketsState = ReturnType<typeof useTicketsController>
