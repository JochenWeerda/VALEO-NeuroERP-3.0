import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type KundenBankverbindung = {
  id: string
  kunden_nr: string
  bezeichnung: string | null
  iban: string
  iban_masked: string
  bic: string | null
  bank_name: string | null
  kontoinhaber: string | null
  sepa_mandat_ref: string | null
  sepa_mandat_datum: string | null
  standard: boolean
  aktiv: boolean
  created_at: string
}

export type KundenBankverbindungCreate = {
  bezeichnung?: string | null
  iban: string
  bic?: string | null
  bank_name?: string | null
  kontoinhaber?: string | null
  sepa_mandat_ref?: string | null
  sepa_mandat_datum?: string | null
  standard?: boolean
}

const keys = {
  list: (kundenNr: string) => ['kundenbanken', kundenNr] as const,
}

export function useKundenBankverbindungen(kundenNr: string | undefined, enabled = true) {
  return useQuery({
    queryKey: keys.list(kundenNr ?? ''),
    queryFn: async () => {
      if (!kundenNr?.trim()) {
        return []
      }
      const res = await apiClient.get<KundenBankverbindung[]>(
        `/api/v1/kunden/${encodeURIComponent(kundenNr)}/bankverbindungen`,
      )
      return res.data
    },
    enabled: Boolean(kundenNr?.trim()) && enabled,
  })
}

export function useCreateKundenBankverbindung(kundenNr: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: KundenBankverbindungCreate) => {
      const res = await apiClient.post<KundenBankverbindung>(
        `/api/v1/kunden/${encodeURIComponent(kundenNr)}/bankverbindungen`,
        payload,
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.list(kundenNr) })
    },
  })
}

export function useSetStandardKundenBankverbindung(kundenNr: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (bvId: string) => {
      await apiClient.patch(
        `/api/v1/kunden/${encodeURIComponent(kundenNr)}/bankverbindungen/${bvId}/standard`,
      )
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.list(kundenNr) })
    },
  })
}

export function useDeleteKundenBankverbindung(kundenNr: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (bvId: string) => {
      await apiClient.delete(
        `/api/v1/kunden/${encodeURIComponent(kundenNr)}/bankverbindungen/${bvId}`,
      )
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.list(kundenNr) })
    },
  })
}
