import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type RezepturGruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  tierart: string | null
  nutzungsrichtung: string | null
  aktiv: boolean
  created_at: string | null
}

export type RezepturGruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
  tierart?: string | null
  nutzungsrichtung?: string | null
}

const BASE = '/api/v1/produktion/mischfutter/rezepturgruppen'

export function useRezepturgruppen() {
  return useQuery({
    queryKey: ['rezepturgruppen'],
    queryFn: async () => {
      const res = await apiClient.get<RezepturGruppe[]>(BASE)
      return res.data
    },
  })
}

export function useCreateRezepturgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RezepturGruppeCreate) => {
      const res = await apiClient.post<RezepturGruppe>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['rezepturgruppen'] })
    },
  })
}

export function useDeleteRezepturgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (gruppe_nr: string) => {
      await apiClient.delete(`${BASE}/${encodeURIComponent(gruppe_nr)}`)
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['rezepturgruppen'] })
    },
  })
}
