import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kreditlimit-Prüfung & Billing-Status (DOM-SALES-004.3).
 * Backend: app/api/v1/endpoints/sales_credit.py
 */

export type CreditAmpel = 'ok' | 'warnung' | 'blockiert' | 'kein_limit' | string

export type CreditInfo = {
  ampel: CreditAmpel
  limit: number
  exposure: number
  verfuegbar: number | null
  auslastung_pct: number
  auslastung_neu_pct: number
}

export type CreditBilling = { lieferschein: string; rechnung: string | null; billing_status: 'berechnet' | 'offen' | string; datum: string | null }

export type OrderCredit = {
  found: boolean
  detail?: string
  order_number?: string
  kunde?: string | null
  customer_id?: string
  auftrag_betrag?: number
  kredit?: CreditInfo
  billing?: CreditBilling[]
  summary?: { ampel: CreditAmpel; verfuegbar: number | null; lieferscheine: number; offen_unberechnet: number }
}

export type CreditCustomerRow = CreditInfo & { customer_id: string; kunde: string | null; auftraege: number }

const BASE = '/api/v1/sales/credit-check'

export function useCreditCustomers() {
  return useQuery({
    queryKey: ['sales-credit', 'customers'],
    queryFn: async () => (await apiClient.get<{ items: CreditCustomerRow[] }>(`${BASE}/customers`)).data?.items ?? [],
  })
}

export function useOrderCredit(auftrag: string | null) {
  return useQuery({
    queryKey: ['sales-credit', 'order', auftrag],
    enabled: !!auftrag,
    queryFn: async () => (await apiClient.get<OrderCredit>(BASE, { params: { auftrag } })).data,
  })
}
