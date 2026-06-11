import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3).
 * Engagement = offene Menge je Artikel (Netto) / je Partei; Kontraktmahnung = überfällige
 * untererfüllte Kontrakte + Mahnung erfassen.
 * Backend: app/api/v1/endpoints/contract_engagement.py
 */

export type EngagementArticle = {
  artikel: string
  einkauf_offen: number
  verkauf_offen: number
  netto: number
  kontrakte: number
}

export type EngagementParty = { party_id: string; offen: number; kontrakte: number }

export type Engagement = {
  by_article: EngagementArticle[]
  by_party: EngagementParty[]
  summary: { einkauf_offen: number; verkauf_offen: number; netto: number; artikel_anzahl: number; parteien_anzahl: number }
}

export type DunningCandidate = {
  contract_no: string
  typ: string
  party_id: string | null
  einheit: string | null
  valid_to: string | null
  tage_ueberfaellig: number | null
  offen: number
  letzte_mahnstufe: number | null
  naechste_mahnstufe: number
}

export type Reminder = { mahnstufe: number; offen: number | null; text: string | null; bediener: string | null; datum: string | null }

const BASE = '/api/v1/contracts'

export function useEngagement() {
  return useQuery({
    queryKey: ['contract-engagement', 'engagement'],
    queryFn: async () => (await apiClient.get<Engagement>(`${BASE}/engagement`)).data,
  })
}

export function useDunningCandidates() {
  return useQuery({
    queryKey: ['contract-engagement', 'dunning', 'candidates'],
    queryFn: async () => (await apiClient.get<{ items: DunningCandidate[] }>(`${BASE}/dunning/candidates`)).data?.items ?? [],
  })
}

export function useReminders(kontrakt: string | null) {
  return useQuery({
    queryKey: ['contract-engagement', 'dunning', 'list', kontrakt],
    enabled: !!kontrakt,
    queryFn: async () => (await apiClient.get<{ items: Reminder[] }>(`${BASE}/dunning/list`, { params: { kontrakt } })).data?.items ?? [],
  })
}

export function useCreateReminder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { kontrakt: string; text?: string; mahnstufe?: number }) =>
      (await apiClient.post<{ ok: boolean; mahnstufe: number; offen: number }>(`${BASE}/dunning`, input)).data,
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: ['contract-engagement', 'dunning', 'candidates'] })
      void qc.invalidateQueries({ queryKey: ['contract-engagement', 'dunning', 'list', vars.kontrakt] })
    },
  })
}
