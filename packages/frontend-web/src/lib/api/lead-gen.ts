import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/** CRM Lead-Generierung: region-universale Lead-Kandidaten aus GAP/LKV. */

export type LeadKandidat = {
  name: string
  plz: string | null
  ort: string | null
  strasse: string | null
  score: number | null
  quelle: 'gap' | 'lkv'
  score_label: string
}

export type LeadPreview = {
  quelle: string
  plz_min: string | null
  plz_max: string | null
  top_pct: number
  anzahl: number
  kandidaten: LeadKandidat[]
}

export type LeadGenParams = {
  quelle: 'gap' | 'lkv' | 'beide'
  plzMin?: string
  plzMax?: string
  topPct: number
  maxLeads: number
}

export function useLeadPreview(params: LeadGenParams, enabled: boolean) {
  return useQuery({
    queryKey: ['lead-gen', 'preview', params],
    queryFn: async () => {
      const q: Record<string, string | number> = {
        quelle: params.quelle,
        top_pct: params.topPct,
        max_leads: params.maxLeads,
      }
      if (params.plzMin) q.plz_min = params.plzMin
      if (params.plzMax) q.plz_max = params.plzMax
      const res = await apiClient.get<LeadPreview>('/api/v1/crm/lead-generierung/preview', { params: q })
      return res.data
    },
    enabled,
    staleTime: 30_000,
  })
}
