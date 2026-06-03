import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Einheitliche Partner-Suche über Kunden, Lieferanten und Leads (Multi-Rolle).
 * Ein Partner kann mehrere Rollen tragen (z. B. Kunde für Dünger UND Lieferant
 * für Weizen) — `rollen` enthält dann mehrere Einträge.
 */

export type PartnerRolle = 'kunde' | 'lieferant' | 'lead'

export type PartnerTreffer = {
  name: string
  kunden_nr: string | null
  lieferanten_id: string | null
  lead_id: string | null
  business_partner_id: string | null
  plz: string | null
  ort: string | null
  rollen: PartnerRolle[]
}

export function usePartnerSuche(q: string, limit = 50) {
  return useQuery({
    queryKey: ['partner-suche', q, limit],
    queryFn: async () => {
      const res = await apiClient.get<PartnerTreffer[]>('/api/v1/crm/partner-suche', { params: { q, limit } })
      return Array.isArray(res.data) ? res.data : []
    },
    enabled: q.trim().length >= 2,
    staleTime: 60_000,
  })
}
