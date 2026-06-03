import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * TAPI/Telefonie: eingehende Anrufe für das Click-to-Customer-Popup.
 * Ein lokaler TAPI-Bridge-Dienst meldet Anrufe per POST /incoming; das Frontend
 * pollt /pending und zeigt den erkannten Kunden, /ack quittiert.
 */

export type TapiCall = {
  id: string
  caller: string
  called: string | null
  richtung: string
  kunden_nr: string | null
  kunde_name: string | null
  status: string
  acked: boolean
  created_at: string
}

export function usePendingCalls(pollMs = 5000) {
  return useQuery({
    queryKey: ['tapi-pending'],
    queryFn: async () => {
      const res = await apiClient.get<TapiCall[]>('/api/v1/crm/tapi/pending')
      return Array.isArray(res.data) ? res.data : []
    },
    refetchInterval: pollMs,
    initialDataUpdatedAt: 0,
  })
}

export function useAckCall() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.post(`/api/v1/crm/tapi/${encodeURIComponent(id)}/ack`, {})
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['tapi-pending'] }) },
  })
}
