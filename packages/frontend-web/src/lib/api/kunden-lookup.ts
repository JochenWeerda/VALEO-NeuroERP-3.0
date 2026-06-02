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
