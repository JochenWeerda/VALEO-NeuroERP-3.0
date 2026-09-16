/**
 * Sales API Hooks
 * TanStack Query hooks for Verkauf (Orders, Offers, Deliveries, Invoices)
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type AuftragStatus = 'open' | 'offen' | 'teilgeliefert' | 'geliefert' | 'fakturiert' | 'storniert'
export type AngebotStatus = 'offen' | 'angenommen' | 'abgelehnt' | 'abgelaufen'

// ── Backend response shapes ───────────────────────────────────────────────────

export type SalesOrderItem = {
  id: string
  line_number: number
  article_number: string
  description?: string
  quantity: number
  unit_price: number
  discount_percent: number
  line_total: number
}

export type SalesOrder = {
  id: string
  tenant_id: string
  order_number: string
  customer_id?: string
  customer_name?: string
  subject: string
  description?: string
  total_amount: number
  currency: string
  status: string
  contact_person?: string
  delivery_date?: string
  delivery_address?: string
  shipping_method?: string
  payment_terms?: string
  notes?: string
  items: SalesOrderItem[]
  created_at?: string
  updated_at?: string
  version: number
}

export type SalesOfferItem = {
  id: string
  line_number: number
  article_number: string
  description?: string
  quantity: number
  unit: string
  unit_price: number
  ek_price?: number
  discount_percent: number
  line_total: number
}

export type SalesOffer = {
  id: string
  tenant_id: string
  offer_number: string
  customer_id?: string
  customer_name?: string
  subject: string
  description?: string
  total_amount: number
  currency: string
  status: string
  contact_person?: string
  valid_until?: string
  notes?: string
  is_pauschale: boolean
  items: SalesOfferItem[]
  created_at?: string
  updated_at?: string
  version: number
}

export type SalesOrderScreenSummary = {
  schema_version: 1
  screen_id: 'sales/sales-order'
  order_id: string
  tenant_id?: string | null
  title: string
  subtitle?: string | null
  summary: {
    total_amount: number
    item_count: number
    status: string
    delivery_date?: string | null
  }
  available_tabs: string[]
  tab_endpoints?: Record<string, string>
  actions: Array<{ key: string; label: string; permission?: string }>
  customer_name?: string | null
  performance: {
    initial_payload_budget_kb: number
    tabs_lazy: boolean
    lookup_min_chars: number
    default_table_limit: number
  }
}

type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

const EMPTY_SALES_ORDERS: SalesOrder[] = []
const EMPTY_SALES_OFFERS: SalesOffer[] = []
const EMPTY_AUFTRAEGE: Auftrag[] = []
const EMPTY_ANGEBOTE: Angebot[] = []
const EMPTY_LIEFERUNGEN: Lieferung[] = []
const EMPTY_RECHNUNGEN: Rechnung[] = []

// ── Legacy UI types (kept for backward compat) ────────────────────────────────

export type LieferungStatus = 'geplant' | 'unterwegs' | 'zugestellt' | 'storniert'

export type Lieferung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  auftragsNr: string
  menge: number
  status: LieferungStatus
}

export type RechnungStatus =
  | 'entwurf'
  | 'gebucht'
  | 'offen'
  | 'teilbezahlt'
  | 'bezahlt'
  | 'ueberfaellig'
  | 'storniert'

export type Rechnung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  /** Leer, solange die Rechnung ihre Quelle ueber Zuordnungen fuehrt, nicht ueber eine Auftragsnummer. */
  auftragsNr: string
  betrag: number
  faelligAm: string
  status: RechnungStatus
  /** Positionszahl aus dem Beleg; 0 ist ein Befund, kein Formfehler. */
  positionen?: number
}

export type Auftrag = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: AuftragStatus
  liefertermin: string
}

export type Angebot = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: AngebotStatus
  gueltigBis: string
}

// ── Query keys ────────────────────────────────────────────────────────────────

export const salesKeys = {
  all: ['sales'] as const,
  orders: (filters?: Record<string, unknown>) => [...salesKeys.all, 'orders', filters] as const,
  order: (id: string) => [...salesKeys.all, 'orders', id] as const,
  orderScreenSummary: (id: string) => [...salesKeys.order(id), 'screen-summary'] as const,
  offers: (filters?: Record<string, unknown>) => [...salesKeys.all, 'offers', filters] as const,
  offer: (id: string) => [...salesKeys.all, 'offers', id] as const,
  // legacy aliases
  auftraege: (filters?: Record<string, unknown>) => salesKeys.orders(filters),
  angebote: (filters?: Record<string, unknown>) => salesKeys.offers(filters),
}

// ── Transformers ──────────────────────────────────────────────────────────────

function formatDate(iso?: string): string {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('de-DE')
  } catch {
    return iso
  }
}

function orderToAuftrag(o: SalesOrder): Auftrag {
  return {
    id: o.id,
    nummer: o.order_number,
    datum: formatDate(o.created_at),
    kunde: o.customer_name ?? o.customer_id ?? '',
    betrag: o.total_amount,
    status: (o.status as AuftragStatus) ?? 'offen',
    liefertermin: formatDate(o.delivery_date),
  }
}

function offerToAngebot(o: SalesOffer): Angebot {
  return {
    id: o.id,
    nummer: o.offer_number,
    datum: formatDate(o.created_at),
    kunde: o.customer_name ?? o.customer_id ?? '',
    betrag: o.total_amount,
    status: (o.status as AngebotStatus) ?? 'offen',
    gueltigBis: formatDate(o.valid_until),
  }
}

// ── Raw REST fetchers ─────────────────────────────────────────────────────────

async function fetchOrders(params: Record<string, unknown> = {}): Promise<SalesOrder[]> {
  const query = new URLSearchParams()
  query.set('limit', '100')
  if (params.search) query.set('search', String(params.search))
  if (params.status) query.set('status', String(params.status))
  if (params.customer_id) query.set('customer_id', String(params.customer_id))
  const resp = await apiClient.get<PaginatedResponse<SalesOrder>>(`/api/v1/sales/orders/?${query.toString()}`)
  return resp.data.items ?? []
}

async function fetchOffers(params: Record<string, unknown> = {}): Promise<SalesOffer[]> {
  const query = new URLSearchParams()
  query.set('limit', '100')
  if (params.search) query.set('search', String(params.search))
  if (params.status) query.set('status', String(params.status))
  if (params.customer_id) query.set('customer_id', String(params.customer_id))
  const resp = await apiClient.get<PaginatedResponse<SalesOffer>>(`/api/v1/sales/offers/?${query.toString()}`)
  return resp.data.items ?? []
}

// ── Hooks: Orders ─────────────────────────────────────────────────────────────

async function fetchSalesOrder(id: string): Promise<SalesOrder> {
  const resp = await apiClient.get<SalesOrder>(`/api/v1/sales/orders/${id}`)
  return resp.data
}

export function useSalesOrder(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: salesKeys.order(id),
    queryFn: () => fetchSalesOrder(id),
    enabled: Boolean(id) && (options?.enabled ?? true),
  })
}

export function useSalesOrderScreenSummary(id: string) {
  return useQuery({
    queryKey: salesKeys.orderScreenSummary(id),
    queryFn: async () => {
      const response = await apiClient.get<SalesOrderScreenSummary>(`/api/v1/sales/orders/${id}/screen-summary`)
      return response.data
    },
    enabled: Boolean(id),
    staleTime: 5 * 60 * 1000,
  })
}

export function useSalesOrders(filters?: { status?: string; search?: string; customer_id?: string }) {
  return useQuery({
    queryKey: salesKeys.orders(filters),
    queryFn: () => fetchOrders(filters ?? {}),
    initialData: EMPTY_SALES_ORDERS,
    staleTime: 2 * 60 * 1000,
  })
}

/** Legacy alias – returns UI-shaped Auftrag objects */
export function useAuftraege(filters?: { status?: AuftragStatus; search?: string }) {
  return useQuery<Auftrag[]>({
    queryKey: salesKeys.auftraege(filters),
    queryFn: async () => {
      const orders = await fetchOrders(filters ?? {})
      let items = orders.map(orderToAuftrag)
      if (filters?.status) items = items.filter((a) => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter((a) => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
    initialData: EMPTY_AUFTRAEGE,
    staleTime: 2 * 60 * 1000,
  })
}

// ── Hooks: Offers ─────────────────────────────────────────────────────────────

export function useSalesOffers(filters?: { status?: string; search?: string; customer_id?: string }) {
  return useQuery({
    queryKey: salesKeys.offers(filters),
    queryFn: () => fetchOffers(filters ?? {}),
    initialData: EMPTY_SALES_OFFERS,
    staleTime: 2 * 60 * 1000,
  })
}

/** Legacy alias – returns UI-shaped Angebot objects */
export function useAngebote(filters?: { status?: AngebotStatus; search?: string }) {
  return useQuery<Angebot[]>({
    queryKey: salesKeys.angebote(filters),
    queryFn: async () => {
      const offers = await fetchOffers(filters ?? {})
      let items = offers.map(offerToAngebot)
      if (filters?.status) items = items.filter((a) => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter((a) => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
    initialData: EMPTY_ANGEBOTE,
    staleTime: 2 * 60 * 1000,
  })
}

// ── Mutations: Offers ─────────────────────────────────────────────────────────

type CreateOfferPayload = Omit<SalesOffer, 'id' | 'tenant_id' | 'version' | 'created_at' | 'updated_at'>

export function useCreateOffer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreateOfferPayload) => {
      const resp = await apiClient.post<SalesOffer>('/api/v1/sales/offers/', payload)
      return resp.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: salesKeys.all }),
  })
}

export function useDeleteOffer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/sales/offers/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: salesKeys.all }),
  })
}

export function useConvertOfferToOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const resp = await apiClient.post<SalesOffer>(`/api/v1/sales/offers/${id}/convert-to-order`)
      return resp.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: salesKeys.all }),
  })
}

// ── Mutations: Orders ─────────────────────────────────────────────────────────

export function useDeleteOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/sales/orders/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: salesKeys.all }),
  })
}

// ── Hooks: Deliveries ─────────────────────────────────────────────────────────

export function useLieferungen() {
  return useQuery<Lieferung[]>({
    queryKey: [...salesKeys.all, 'deliveries'],
    queryFn: async () => {
      try {
        const resp = await apiClient.get<{ items: Lieferung[] }>('/api/v1/sales/deliveries/?limit=100')
        return resp.data.items ?? []
      } catch {
        return []
      }
    },
    initialData: EMPTY_LIEFERUNGEN,
    staleTime: 2 * 60 * 1000,
  })
}

// ── Hooks: Invoices ───────────────────────────────────────────────────────────

/**
 * Rohform einer Rechnung aus `GET /sales/invoices`.
 *
 * Bis zu FSX-RECHNUNGSMASKE gab es diesen Endpunkt nicht: Der Abruf lief in
 * einen 404, das `catch` machte daraus eine leere Liste, und die Maske sah aus,
 * als gaebe es keine Rechnungen. Seit es ihn gibt, muss die Antwort auch
 * **gelesen** werden — die Feldnamen des Belegs sind andere als die der Maske.
 */
export type SalesInvoiceListRow = {
  id?: string
  invoice_number?: string
  customer_id?: string
  invoice_date?: string
  due_date?: string | null
  status?: string
  net_amount?: string
  gross_amount?: string
  line_count?: number
}

/**
 * Belegstatus auf den Status der Faktura-Liste.
 *
 * `gebucht` wird zu `offen`: Eine gebuchte Rechnung ist fachlich eine offene
 * Forderung. `teilbezahlt` und `ueberfaellig` entstehen hier **nicht** — beide
 * haengen am Zahlungsstand, den der Beleg nicht fuehrt. Sie aus dem
 * Faelligkeitsdatum zu erfinden waere eine Aussage ueber Zahlungen, die wir an
 * dieser Stelle nicht haben.
 */
export function rechnungStatus(status?: string): RechnungStatus {
  switch (status) {
    case 'entwurf':
      return 'entwurf'
    case 'gebucht':
      return 'offen'
    case 'bezahlt':
      return 'bezahlt'
    case 'storniert':
      return 'storniert'
    default:
      return 'entwurf'
  }
}

export function zuRechnung(zeile: SalesInvoiceListRow): Rechnung {
  const betrag = Number(zeile.gross_amount ?? zeile.net_amount ?? '0')
  return {
    id: String(zeile.id ?? ''),
    nummer: String(zeile.invoice_number ?? ''),
    datum: String(zeile.invoice_date ?? ''),
    kunde: String(zeile.customer_id ?? ''),
    // Die Herkunft der Rechnung steht in den Zuordnungen, nicht in einer
    // Auftragsnummer am Kopf. Leer ist hier richtig, nicht unvollstaendig.
    auftragsNr: '',
    betrag: Number.isFinite(betrag) ? betrag : 0,
    faelligAm: String(zeile.due_date ?? ''),
    status: rechnungStatus(zeile.status),
    positionen: typeof zeile.line_count === 'number' ? zeile.line_count : undefined,
  }
}

export function useRechnungen() {
  return useQuery<Rechnung[]>({
    queryKey: [...salesKeys.all, 'invoices'],
    queryFn: async () => {
      try {
        const resp = await apiClient.get<{ items?: SalesInvoiceListRow[] }>(
          '/api/v1/sales/invoices?limit=100',
        )
        return (resp.data?.items ?? []).map(zuRechnung)
      } catch {
        // Bewusst still: Die Liste ist eine Uebersicht, kein Vorgang. Ein
        // Fehlerbanner statt der Tabelle waere hier die schlechtere Auskunft.
        return []
      }
    },
    initialData: EMPTY_RECHNUNGEN,
    staleTime: 2 * 60 * 1000,
  })
}
