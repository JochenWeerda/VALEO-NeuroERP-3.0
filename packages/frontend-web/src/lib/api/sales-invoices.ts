/**
 * Ausgangsrechnungen — TanStack-Query-Hooks fuer /api/v1/sales/invoices
 *
 * Die Zahlen kommen als **Zeichenketten** vom Endpunkt und bleiben es hier.
 * Ein `Number('12.345678')` waere eine stille Rundung an einer Stelle, an der
 * niemand sie sucht; gerundet wird erst in der Anzeige, aus einem Wert, der
 * noch vollstaendig ist.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

/** Woher die berechnete Menge einer Rechnungsposition stammt. */
export type InvoiceLineOrigin = {
  source_document_type: string
  source_document_id: string
  source_line_id: string
  quantity: string
  unit: string
  reason?: string | null
}

export type SalesInvoiceLine = {
  line_no: string
  article_id?: string | null
  article_number?: string | null
  description?: string | null
  quantity: string
  unit: string
  unit_price: string
  net_amount: string
  vat_rate?: string | null
  /**
   * Leer heisst: **keine Zuordnung vorhanden** — nicht "noch nicht geladen".
   * Die Herkunft kommt mit dem Beleg in derselben Abfrage.
   */
  origins: InvoiceLineOrigin[]
}

export type SalesInvoice = {
  id: string
  invoice_number: string
  customer_id: string
  invoice_date: string
  due_date?: string | null
  status: string
  currency: string
  net_amount: string
  vat_amount: string
  gross_amount: string
  lines: SalesInvoiceLine[]
  total: number
}

export type SalesInvoiceListItem = {
  id: string
  invoice_number: string
  customer_id: string
  invoice_date: string
  due_date?: string | null
  status: string
  currency: string
  net_amount: string
  vat_amount: string
  gross_amount: string
  /** Positionszahl — beantwortet "sieht der Beleg leer aus", ohne ihn zu oeffnen. */
  line_count: number
}

export type SalesInvoiceListResponse = {
  items: SalesInvoiceListItem[]
  /** Trefferzahl ohne Seitenbegrenzung: "50 von 50" ist nicht "50 von 900". */
  total: number
  limit: number
  offset: number
}

export type SalesInvoiceFilter = {
  customer_id?: string
  status?: string
  invoice_number?: string
  date_from?: string
  date_to?: string
  limit?: number
  offset?: number
}

// ========== QUERY KEYS ==========

export const salesInvoiceKeys = {
  list: (filter?: SalesInvoiceFilter) => ['sales-invoices', 'list', filter ?? {}] as const,
  detail: (id?: string) => ['sales-invoices', 'detail', id ?? ''] as const,
}

const BASE = '/api/v1/sales/invoices'

/** Leere Felder gehoeren nicht in die Abfrage — `status=` filtert sonst auf nichts. */
function gesetzteFelder(filter?: SalesInvoiceFilter): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  if (!filter) return params
  for (const [schluessel, wert] of Object.entries(filter)) {
    if (wert === undefined || wert === null || wert === '') continue
    params[schluessel] = wert as string | number
  }
  return params
}

// ========== HOOKS ==========

export function useSalesInvoices(filter?: SalesInvoiceFilter) {
  return useQuery({
    queryKey: salesInvoiceKeys.list(filter),
    queryFn: async () => {
      const res = await apiClient.get<SalesInvoiceListResponse>(BASE, {
        params: gesetzteFelder(filter),
      })
      return res.data
    },
  })
}

export function useSalesInvoice(id?: string) {
  return useQuery({
    queryKey: salesInvoiceKeys.detail(id),
    enabled: Boolean(id),
    queryFn: async () => {
      const res = await apiClient.get<SalesInvoice>(`${BASE}/${encodeURIComponent(id as string)}`)
      return res.data
    },
  })
}

// ========== ANZEIGE ==========

/**
 * Betrag mit Waehrung, deutsch formatiert — aus der ungerundeten Zeichenkette.
 *
 * Ist der Wert keine Zahl, bleibt er stehen wie er kam: Eine "0,00 EUR" statt
 * eines unlesbaren Werts waere eine Behauptung ueber einen Betrag, den wir
 * nicht kennen.
 */
export function formatBetrag(wert: string, waehrung = 'EUR'): string {
  const zahl = Number(wert)
  if (!Number.isFinite(zahl)) return wert
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: waehrung || 'EUR',
  }).format(zahl)
}

/** Menge mit Einheit — bis zu drei Nachkommastellen, ohne unnoetige Nullen. */
export function formatMenge(wert: string, einheit: string): string {
  const zahl = Number(wert)
  const gezeigt = Number.isFinite(zahl)
    ? new Intl.NumberFormat('de-DE', { maximumFractionDigits: 3 }).format(zahl)
    : wert
  return `${gezeigt} ${einheit}`.trim()
}

/** ISO-Datum als `TT.MM.JJJJ`; ein unlesbares Datum bleibt unveraendert. */
export function formatDatum(wert?: string | null): string {
  if (!wert) return '—'
  const datum = new Date(wert)
  if (Number.isNaN(datum.getTime())) return wert
  return new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium' }).format(datum)
}
