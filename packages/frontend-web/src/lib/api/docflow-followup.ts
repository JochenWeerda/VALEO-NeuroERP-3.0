import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Bescheid/Rückmeldung & Wiedervorlage (DOM-DOC-004.3).
 * Backend: app/api/v1/endpoints/docflow_followup.py
 */

export type Followup = {
  followup_id: string
  art: 'bescheid' | 'rueckmeldung' | 'wiedervorlage' | string
  betreff: string | null
  text: string | null
  faellig_am: string | null
  status: 'offen' | 'erledigt' | string
  ueberfaellig: boolean
  erledigt_at: string | null
  erledigt_von: string | null
  created_at: string | null
  created_by: string | null
}

export type FollowupList = {
  found: boolean
  detail?: string
  doc_number?: string
  followups?: Followup[]
  summary?: { anzahl: number; offen: number; ueberfaellig: number }
}

export type WiedervorlageRow = {
  followup_id: string
  doc_number: string
  betreff: string | null
  faellig_am: string | null
  bediener: string | null
  ueberfaellig: boolean
}

const BASE = '/api/v1/docflow/evidence'

export function useWiedervorlagen() {
  return useQuery({
    queryKey: ['docflow-followup', 'wiedervorlagen'],
    queryFn: async () => (await apiClient.get<{ items: WiedervorlageRow[] }>(`${BASE}/wiedervorlagen`)).data?.items ?? [],
  })
}

export function useFollowups(doc: string | null) {
  return useQuery({
    queryKey: ['docflow-followup', 'list', doc],
    enabled: !!doc,
    queryFn: async () => (await apiClient.get<FollowupList>(`${BASE}/followups`, { params: { doc } })).data,
  })
}

export type FollowupInput = { doc: string; art: string; betreff: string; text?: string; faelligAm?: string }

export function useCreateFollowup() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: FollowupInput) =>
      (await apiClient.post<{ ok: boolean; followup_id: string }>(`${BASE}/followups`, input)).data,
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: ['docflow-followup', 'list', vars.doc] })
      void qc.invalidateQueries({ queryKey: ['docflow-followup', 'wiedervorlagen'] })
    },
  })
}

export function useCompleteFollowup() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (followupId: string) =>
      (await apiClient.post<{ ok: boolean; status: string }>(`${BASE}/followups/${encodeURIComponent(followupId)}/complete`, {})).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['docflow-followup'] }) },
  })
}
