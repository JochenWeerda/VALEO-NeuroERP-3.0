/**
 * Geschäftsjahre [JAHR] und Zahlungsmeldungen [KASSZAME]
 * TanStack Query Hooks für /api/v1/fibu/geschaeftsjahre und /api/v1/fibu/zahlungsmeldungen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type GeschaeftsjahreStatus = 'offen' | 'gesperrt' | 'abgeschlossen'

export type Geschaeftsjahr = {
  id: string
  jahr_nr: number
  bezeichnung: string
  datum_beginn: string
  datum_ende: string
  anzahl_perioden_ware: number
  anzahl_perioden_fibu: number
  journal_nummernkreis: string | null
  status: GeschaeftsjahreStatus
  created_at: string
}

export type GeschaeftsjahreCreate = {
  jahr_nr: number
  bezeichnung: string
  datum_beginn: string
  datum_ende: string
  anzahl_perioden_ware?: number
  anzahl_perioden_fibu?: number
  journal_nummernkreis?: string | null
}

export type FibuPeriode = {
  id: string
  jahr_nr: number
  periode_nr: number
  bezeichnung: string
  datum_von: string
  datum_bis: string
  typ: string
  gesperrt: boolean
  created_at: string
}

export type ZahlungsmeldungStatus = 'eingegangen' | 'verarbeitet' | 'abgewiesen'

export type Zahlungsmeldung = {
  id: string
  meldungs_nr: string
  kunden_nr: string
  rechnungs_nr: string | null
  zahlungsdatum: string
  zahlungsbetrag_eur: number
  skonto_betrag_eur: number
  skonto_erlaubt: boolean
  teilzahlung: boolean
  aus_fibu: boolean
  status: ZahlungsmeldungStatus
  verarbeitet_am: string | null
  created_at: string
}

export type ZahlungsmeldungCreate = {
  kunden_nr: string
  zahlungsdatum: string
  zahlungsbetrag_eur: number
  skonto_betrag_eur?: number
  skonto_erlaubt: boolean
  teilzahlung: boolean
  aus_fibu: boolean
  rechnungs_nr?: string | null
}

// ========== QUERY KEYS ==========

export const gjKeys = {
  list: () => ['fibu', 'geschaeftsjahre'] as const,
  perioden: (jahr_nr: number) => ['fibu', 'geschaeftsjahre', jahr_nr, 'perioden'] as const,
}

export const zmKeys = {
  list: (params?: Record<string, string>) =>
    ['fibu', 'zahlungsmeldungen', params ?? {}] as const,
}

const GJ_BASE = '/api/v1/fibu/geschaeftsjahre'
const ZM_BASE = '/api/v1/fibu/zahlungsmeldungen'

// ========== GESCHÄFTSJAHRE ==========

export function useGeschaeftsjahre() {
  return useQuery({
    queryKey: gjKeys.list(),
    queryFn: async () => {
      const res = await apiClient.get<Geschaeftsjahr[]>(GJ_BASE)
      return res.data
    },
  })
}

export function useCreateGeschaeftsjahr() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: GeschaeftsjahreCreate) => {
      const res = await apiClient.post<Geschaeftsjahr>(GJ_BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: gjKeys.list() })
    },
  })
}

export function useDeleteGeschaeftsjahr() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (jahr_nr: number) => {
      await apiClient.delete(`${GJ_BASE}/${encodeURIComponent(String(jahr_nr))}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: gjKeys.list() })
    },
  })
}

export function useFibuPerioden(jahr_nr: number | null) {
  return useQuery({
    queryKey: gjKeys.perioden(jahr_nr ?? 0),
    queryFn: async () => {
      const res = await apiClient.get<FibuPeriode[]>(
        `${GJ_BASE}/${encodeURIComponent(String(jahr_nr))}/perioden`
      )
      return res.data
    },
    enabled: jahr_nr !== null,
  })
}

// ========== ZAHLUNGSMELDUNGEN ==========

export function useZahlungsmeldungen(params?: {
  kunden_nr?: string
  status?: ZahlungsmeldungStatus
  von_datum?: string
  bis_datum?: string
}) {
  return useQuery({
    queryKey: zmKeys.list(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Zahlungsmeldung[]>(ZM_BASE, { params: params ?? {} })
      return res.data
    },
  })
}

export function useCreateZahlungsmeldung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ZahlungsmeldungCreate) => {
      const res = await apiClient.post<Zahlungsmeldung>(ZM_BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fibu', 'zahlungsmeldungen'] })
    },
  })
}

export function useDeleteZahlungsmeldung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${ZM_BASE}/${encodeURIComponent(id)}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fibu', 'zahlungsmeldungen'] })
    },
  })
}

export function useVerarbeitenZahlungsmeldung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post<Zahlungsmeldung>(
        `${ZM_BASE}/${encodeURIComponent(id)}/verarbeiten`
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fibu', 'zahlungsmeldungen'] })
    },
  })
}
