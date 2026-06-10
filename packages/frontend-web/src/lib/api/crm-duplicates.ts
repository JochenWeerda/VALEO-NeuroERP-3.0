import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kunden-Dubletten (DOM-CRM-004): erkennt wahrscheinliche Doppelanlagen über
 * E-Mail/Telefon/Name+PLZ. Read-only; Zusammenführung folgt als eigener Slice.
 * Backend: app/api/v1/endpoints/crm_duplicates.py
 */

export type DuplicateMember = {
  kunden_nr: string
  name1: string | null
  plz: string | null
  ort: string | null
  tel: string | null
  email: string | null
}

export type DuplicateReason = { typ: string; wert: string }

export type DuplicateGroup = {
  id: string
  mitglieder: DuplicateMember[]
  anzahl: number
  gruende: DuplicateReason[]
  grund_typen: string[]
  score: number
  konfidenz: 'hoch' | 'mittel' | string
}

export type DuplicatesResponse = { groups: DuplicateGroup[]; total: number; geprueft: number }

export function useDuplicates(limit = 100) {
  return useQuery({
    queryKey: ['crm-duplicates', limit],
    queryFn: async () => {
      const res = await apiClient.get<DuplicatesResponse>('/api/v1/crm/duplicates', { params: { limit } })
      return res.data ?? { groups: [], total: 0, geprueft: 0 }
    },
    staleTime: 60_000,
  })
}

export type MergeResult = { ok: boolean; verschoben?: Record<string, number>; summe_datensaetze?: number }

export function useMergeCustomers() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { masterNr: string; duplicateNr: string }) =>
      (await apiClient.post<MergeResult>('/api/v1/crm/duplicates/merge', input)).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['crm-duplicates'] }) },
  })
}
