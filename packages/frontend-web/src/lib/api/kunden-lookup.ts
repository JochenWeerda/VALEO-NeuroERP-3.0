import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Satelliten-basierte Kundenauswahl (Stammdaten-Konsolidierung, Phase 2D).
 *
 * - `useKundenLookup`  → GET /api/v1/customers/lookup  (kunden_lookup-View,
 *   schlanke Such-/Listenfelder; schnelle Auswahl)
 * - `useKundenDetail`  → GET /api/v1/customers/lookup/{kunden_nr}/detail
 *   (Adresse/Zahlung/External-Refs on-demand aus den kunden_*-Satelliten)
 *
 * Schlüssel ist die fachliche `kunden_nr`; `business_partner_id` ist die
 * technische SoR-Identität (für spätere BP-Verknüpfung).
 */

export type KundenLookupItem = {
  business_partner_id: string | null
  kunden_nr: string
  name: string | null
  matchcode: string | null
  aktiv: boolean
  plz: string | null
  ort: string | null
  strasse: string | null
  ust_id_nr: string | null
  kundengruppe: string | null
  betreuer: string | null
  sperrgrund: string | null
}

export type KundenDetail = {
  kunden_nr: string
  adresse: Record<string, string | number | boolean | null>
  zahlung: Record<string, string | number | boolean | null>
  external_refs: Record<string, string>
}

const keys = {
  lookup: (q: string, limit: number) => ['kunden-lookup', q, limit] as const,
  detail: (kundenNr: string) => ['kunden-lookup', 'detail', kundenNr] as const,
}

export function useKundenLookup(q: string, limit = 20) {
  return useQuery({
    queryKey: keys.lookup(q, limit),
    queryFn: async () => {
      const res = await apiClient.get<KundenLookupItem[]>('/api/v1/customers/lookup', {
        params: { q, limit },
      })
      return Array.isArray(res.data) ? res.data : []
    },
    staleTime: 60_000,
  })
}

export function useKundenDetail(kundenNr: string | undefined, enabled = true) {
  return useQuery({
    queryKey: keys.detail(kundenNr ?? ''),
    queryFn: async () => {
      const res = await apiClient.get<KundenDetail>(
        `/api/v1/customers/lookup/${encodeURIComponent(kundenNr ?? '')}/detail`,
      )
      return res.data
    },
    enabled: Boolean(kundenNr?.trim()) && enabled,
  })
}

/**
 * Identitaetsbruecke (Phase 2D Schritt 5): loest zwischen business_partner_id,
 * kunden_nr und crm_customer_id auf. Erlaubt den BP-/crm-identitaetsgebundenen
 * Produktivmasken (Kundenstamm/Combobox), das Satelliten-Detail zu erreichen.
 */
export type KundenIdentitaet = {
  kunden_nr: string | null
  business_partner_id: string | null
  partner_number: string | null
  crm_customer_id: string | null
}

export type IdentityKey = {
  kundenNr?: string
  businessPartnerId?: string
  crmCustomerId?: string
}

export function useKundenIdentity(key: IdentityKey, enabled = true) {
  const params: Record<string, string> = {}
  if (key.kundenNr) params.kunden_nr = key.kundenNr
  if (key.businessPartnerId) params.business_partner_id = key.businessPartnerId
  if (key.crmCustomerId) params.crm_customer_id = key.crmCustomerId
  const hasKey = Object.keys(params).length > 0
  return useQuery({
    queryKey: ['kunden-lookup', 'resolve', params],
    queryFn: async () => {
      const res = await apiClient.get<KundenIdentitaet>('/api/v1/customers/lookup/resolve', { params })
      return res.data
    },
    enabled: hasKey && enabled,
  })
}

/** Satelliten-Detail ueber die business_partner_id (Bruecke -> kunden_nr -> Detail). */
export function useKundenDetailByPartner(businessPartnerId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: ['kunden-lookup', 'detail-by-partner', businessPartnerId ?? ''],
    queryFn: async () => {
      const res = await apiClient.get<KundenDetail>(
        `/api/v1/customers/by-partner/${encodeURIComponent(businessPartnerId ?? '')}/detail`,
      )
      return res.data
    },
    enabled: Boolean(businessPartnerId?.trim()) && enabled,
  })
}
