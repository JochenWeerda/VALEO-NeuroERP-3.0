import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kunden-Ownership (DOM-CRM-004.3): Außendienst (salesRep) / Innendienst
 * (dispatcher) je Kunde zuordnen/übergeben; „ohne Zuordnung"-Worklist.
 * Backend: app/api/v1/endpoints/crm_ownership.py
 */

export type UnassignedCustomer = { kunden_nr: string; name1: string | null; plz: string | null; ort: string | null }
export type UnassignedResponse = { items: UnassignedCustomer[]; total: number }

export function useUnassigned(limit = 200) {
  return useQuery({
    queryKey: ['crm-ownership', 'unassigned', limit],
    queryFn: async () => {
      const res = await apiClient.get<UnassignedResponse>('/api/v1/crm/ownership/unassigned', { params: { limit } })
      return res.data ?? { items: [], total: 0 }
    },
  })
}

export function useSetOwnership() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { kundenNr: string; salesRep?: string; dispatcher?: string; grund?: string }) => {
      const { kundenNr, ...body } = input
      const res = await apiClient.put(`/api/v1/crm/${encodeURIComponent(kundenNr)}/ownership`, body)
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['crm-ownership'] }) },
  })
}
