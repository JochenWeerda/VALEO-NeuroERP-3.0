import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type SupplyChainOverview = {
  waitingInbound: number
  weighingTickets: number
  openWeighingTickets: number
  charges: number
  blockedCharges: number
  freightLetters: number
  freightInTransit: number
  chargeArticles: string[]
  activeVehiclePlates: string[]
}

export function useSupplyChainOverview() {
  return useQuery({
    queryKey: ['supply-chain', 'overview'],
    queryFn: async (): Promise<SupplyChainOverview> => {
      const [queueRes, weighingRes, chargesRes, freightRes] = await Promise.all([
        apiClient.get<{ items: Array<{ kennzeichen?: string | null }> }>('/api/v1/annahme/warteschlange'),
        apiClient.get<{ items: Array<{ ticket_number: string; status: string; vehicle_plate?: string | null }> }>('/api/v1/weighing-tickets?limit=100'),
        apiClient.get<{ items: Array<{ artikel: string; status: string }> }>('/api/v1/chargen'),
        apiClient.get<Array<{ nummer: string; status: string; kennzeichen?: string | null }>>('/api/v1/logistik/frachtbriefe'),
      ])

      const waiting = queueRes.data.items ?? []
      const weighings = weighingRes.data.items ?? []
      const charges = chargesRes.data.items ?? []
      const freight = freightRes.data ?? []
      const activeVehiclePlates = Array.from(
        new Set(
          [
            ...waiting.map((item) => item.kennzeichen).filter(Boolean),
            ...weighings.map((item) => item.vehicle_plate).filter(Boolean),
            ...freight.map((item) => item.kennzeichen).filter(Boolean),
          ].map((item) => String(item)),
        ),
      )

      return {
        waitingInbound: waiting.length,
        weighingTickets: weighings.length,
        openWeighingTickets: weighings.filter((item) => item.status !== 'closed').length,
        charges: charges.length,
        blockedCharges: charges.filter((item) => item.status === 'gesperrt' || item.status === 'in-pruefung').length,
        freightLetters: freight.length,
        freightInTransit: freight.filter((item) => item.status === 'unterwegs').length,
        chargeArticles: Array.from(new Set(charges.map((item) => item.artikel).filter(Boolean))).slice(0, 6),
        activeVehiclePlates,
      }
    },
    initialData: {
      waitingInbound: 0,
      weighingTickets: 0,
      openWeighingTickets: 0,
      charges: 0,
      blockedCharges: 0,
      freightLetters: 0,
      freightInTransit: 0,
      chargeArticles: [],
      activeVehiclePlates: [],
    } satisfies SupplyChainOverview,
    staleTime: 30_000,
  })
}

// ── Traceability (DOM-SUPPLY-004): durchgängige Kette je Lieferung ────────────
// Wiegung → Annahme → Lager → Abrechnung (Rückgrat: Wiegeschein).
// Backend: app/api/v1/endpoints/supply_chain.py

export type TraceTicket = {
  ticket_id: string
  ticket_nr: string
  datum: string | null
  menge_kg: number | null
  status: string
  allokation: string
  hat_annahme: boolean
  hat_lager: boolean
  hat_abrechnung: boolean
  vollstaendig: boolean
}

export type TraceNode = {
  stage: 'wiegung' | 'annahme' | 'lager' | 'abrechnung'
  label: string
  ref: string | null
  ref_id: string
  status: string | null
  menge_kg: number | null
  zeitpunkt: string | null
  facts: Record<string, unknown>
}

export type MengenCheck = {
  von: string
  nach: string
  menge_von_kg: number | null
  menge_nach_kg: number | null
  differenz_kg: number | null
  differenz_pct: number | null
  abweichung: boolean
  hinweis: string
}

export type Luecke = { stufe: string; schwere: 'info' | 'warnung' | string; text: string }

export type ChainEvent = {
  id: string
  ticket_id: string
  stage: string
  ref_type: string | null
  ref_id: string | null
  ref_label: string | null
  event_type: string
  status_from: string | null
  status_to: string | null
  menge_kg: number | null
  abweichung_grund: string | null
  bediener: string | null
  source: 'backfill' | 'auto' | 'manual' | string
  occurred_at: string | null
  created_at: string | null
}

export type TraceResult = {
  found: boolean
  detail?: string
  ticket_id?: string
  ticket_nr?: string | null
  kette?: TraceNode[]
  mengen_konsistenz?: MengenCheck[]
  luecken?: Luecke[]
  ereignisse?: ChainEvent[]
  kanon_status?: { status: string; rang: number }
  summary?: {
    stufen: number
    vollstaendig: boolean
    hat_mengen_abweichung: boolean
    offene_luecken: number
    status?: string
  }
}

const TRACE_BASE = '/api/v1/supply-chain/traceability'

export function useTraceTickets(limit = 50) {
  return useQuery({
    queryKey: ['supply-chain', 'tickets', limit],
    queryFn: async () => {
      const res = await apiClient.get<{ items: TraceTicket[] }>(`${TRACE_BASE}/tickets`, { params: { limit } })
      return res.data?.items ?? []
    },
  })
}

export function useTrace(ticket: string | null) {
  return useQuery({
    queryKey: ['supply-chain', 'trace', ticket],
    enabled: !!ticket,
    queryFn: async () => {
      const res = await apiClient.get<TraceResult>(TRACE_BASE, { params: { ticket } })
      return res.data
    },
  })
}

export function useSyncChain() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (ticket: string) =>
      (await apiClient.post<{ synced: number; total: number }>(`${TRACE_BASE}/sync`, {}, { params: { ticket } })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['supply-chain', 'trace'] }) },
  })
}

export type ChainEventInput = {
  ticketId: string
  stage?: string
  eventType?: string
  refLabel?: string
  statusFrom?: string
  statusTo?: string
  mengeKg?: number
  abweichungGrund?: string
  bediener?: string
}

export function useAddChainEvent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: ChainEventInput) =>
      (await apiClient.post<{ ok: boolean; event?: ChainEvent; detail?: string }>('/api/v1/supply-chain/events', input)).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['supply-chain', 'trace'] }) },
  })
}

// ── Lot-Folgeaktionen (Sperre/QS-Freigabe/Schwund) — DOM-SUPPLY-004.3 ─────────
export type LotAction =
  | { kind: 'block'; lotId: string; grund: string }
  | { kind: 'release'; lotId: string; grund: string }
  | { kind: 'shrinkage'; lotId: string; grund: string; mengeKg: number }

export function useLotAction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (a: LotAction) => {
      const base = `/api/v1/supply-chain/lots/${encodeURIComponent(a.lotId)}`
      if (a.kind === 'shrinkage') {
        return (await apiClient.post(`${base}/shrinkage`, { mengeKg: a.mengeKg, grund: a.grund })).data
      }
      return (await apiClient.post(`${base}/${a.kind}`, { grund: a.grund })).data
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['supply-chain', 'trace'] })
      void qc.invalidateQueries({ queryKey: ['supply-chain', 'tickets'] })
    },
  })
}
