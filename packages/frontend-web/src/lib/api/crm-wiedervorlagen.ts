import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Wiedervorlagen/Aufgaben (DOM-CRM-004.4): offene Wiedervorlagen über alle Kunden
 * mit Überfälligkeits-Flag; Erledigen mit optionalem Serviceabschluss-Ergebnis.
 * Backend: app/api/v1/endpoints/crm_kontakte.py
 */

export type Wiedervorlage = {
  id: string
  kunden_nr: string
  kunde: string | null
  art: string | null
  richtung: string | null
  kurzinfo: string | null
  notiz: string | null
  wiedervorlage: string | null
  bediener: string | null
  ueberfaellig: boolean
}

export function useWiedervorlagen(tage = 365) {
  return useQuery({
    queryKey: ['crm-wiedervorlagen', tage],
    queryFn: async () => {
      const res = await apiClient.get<Wiedervorlage[]>('/api/v1/crm/kunden-kontakte/wiedervorlagen', { params: { tage } })
      return Array.isArray(res.data) ? res.data : []
    },
  })
}

export function useErledigen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { id: string; ergebnis?: string }) => {
      const res = await apiClient.post(`/api/v1/crm/kunden-kontakte/${encodeURIComponent(input.id)}/erledigt`,
        { ergebnis: input.ergebnis })
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['crm-wiedervorlagen'] }) },
  })
}
