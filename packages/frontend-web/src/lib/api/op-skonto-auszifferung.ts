/**
 * OP Skonto-Auszifferung (Fachliche Vertiefung Wave 3).
 * TanStack-Query-Hooks für /api/v1/fibu/op-auszifferung.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/fibu/op-auszifferung'

export type SkontoAuszifferung = {
  id: string
  op_id: string
  rechnungsnr: string | null
  zahlungsdatum: string
  zahlungsbetrag_eur: number
  skonto_betrag_eur: number
  skonto_prozent: number | null
  gesamtbetrag_eur: number
  zahlungsart: string | null
  buchungstext: string | null
  fibu_konto: string | null
  skonto_konto: string | null
  status: string
  storniert: boolean
  created_at: string
}

export type SkontoAuszifferungCreate = {
  op_id: string
  rechnungsnr?: string | null
  zahlungsdatum: string
  zahlungsbetrag_eur: number
  skonto_betrag_eur?: number
  zahlungsart?: string | null
  buchungstext?: string | null
  fibu_konto?: string | null
  skonto_konto?: string | null
}

export type SkontoBerechnung = {
  rechnungsbetrag_eur: number
  skonto_prozent: number
  zahlungsdatum: string
  skonto_bis?: string | null
}

export type SkontoBerechnungResult = {
  rechnungsbetrag_eur: number
  skonto_prozent: number
  skonto_gueltig: boolean
  skontobetrag_eur: number
  zahlungsbetrag_eur: number
  hinweis: string | null
}

export function useAuszifferungen() {
  return useQuery({
    queryKey: ['op-auszifferung', 'list'],
    queryFn: async () => (await apiClient.get<SkontoAuszifferung[]>(BASE)).data,
  })
}

export function useCreateAuszifferung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: SkontoAuszifferungCreate) => (await apiClient.post<SkontoAuszifferung>(BASE, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['op-auszifferung'] }),
  })
}

export function useStornoAuszifferung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => (await apiClient.post<SkontoAuszifferung>(`${BASE}/${encodeURIComponent(id)}/stornieren`, {})).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['op-auszifferung'] }),
  })
}

export function useBerechneSkonto() {
  return useMutation({
    mutationFn: async (body: SkontoBerechnung) => (await apiClient.post<SkontoBerechnungResult>(`${BASE}/berechnen`, body)).data,
  })
}
