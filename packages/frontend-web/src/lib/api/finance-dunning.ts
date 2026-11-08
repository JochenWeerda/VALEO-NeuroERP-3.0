import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2).
 * Backend: app/api/v1/endpoints/finance_dunning.py
 */

export type DunningCandidate = {
  op_id: string
  rechnungsnr: string | null
  partner: string | null
  faelligkeit: string | null
  tage_ueberfaellig: number
  offen: number
  aktuelle_stufe: number
  naechste_stufe: number
  dunning_fee: number
  interest: number
  total_amount: number
}

export type DunningNotice = {
  id: string
  /** Wie die Mahnung hinausging; leer, solange sie nicht versendet ist. */
  versand_art: 'email' | 'post' | null
  empfaenger: string | null
  versendet_am: string | null
  stufe: number
  datum: string | null
  offen: number | null
  gebuehr: number | null
  zinsen: number | null
  gesamt: number | null
  frist: string | null
  status: string | null
  rechnungsnr: string | null
  partner: string | null
}

const BASE = '/api/v1/finance/mahnlauf'

export function useDunningCandidates() {
  return useQuery({
    queryKey: ['finance-dunning', 'candidates'],
    queryFn: async () => (await apiClient.get<{ items: DunningCandidate[] }>(`${BASE}/candidates`)).data?.items ?? [],
  })
}

export function useDunningNotices() {
  return useQuery({
    queryKey: ['finance-dunning', 'notices'],
    queryFn: async () => (await apiClient.get<{ items: DunningNotice[] }>(`${BASE}/notices`)).data?.items ?? [],
  })
}

export function useRunDunning() {
  const qc = useQueryClient()
  return useMutation({
    // Ohne Angabe laufen alle ueberfaelligen Posten; `rechnungsnrn` begrenzt auf eine Auswahl.
    mutationFn: async (input: { rechnungsnr?: string; rechnungsnrn?: string[] } = {}) =>
      (await apiClient.post<{ ok: boolean; erzeugt: number }>(`${BASE}/run`, input)).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['finance-dunning'] })
    },
  })
}

/**
 * Versendet eine Mahnung per E-Mail (Postfach "fibu") oder haelt den Postversand fest.
 * Der Server setzt "versendet" erst nach Annahme durch den Mailserver; ohne Adresse,
 * Postfach oder Freigabe kommt ein Fehler mit Grund.
 */
export function useSendDunning() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { id: string; versandArt: 'email' | 'post' }) =>
      (await apiClient.put<{ status: string }>(
        `/api/v1/finance/dunning/${encodeURIComponent(input.id)}/send`, null, { params: { versand_art: input.versandArt } },
      )).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['finance-dunning', 'notices'] })
    },
  })
}
