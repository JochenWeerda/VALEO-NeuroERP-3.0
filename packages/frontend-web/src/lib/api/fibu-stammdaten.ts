/**
 * FIBU Zusatzstammdaten API Client
 * TanStack Query Hooks für /api/v1/fibu/stammdaten
 * Entitäten: Zahlungsformulare [FIZAF], Zinsgruppen, Leergutarten
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Formularklasse = 'eingang' | 'ausgang'
export type Zinsmethode = 'act_act' | 'act_360' | 'act_365' | '30_360'
export type LeergutTyp = 'palette' | 'bigbag' | 'fass' | 'flasche' | 'behaelter' | 'sonstige'

export type Zahlungsformular = {
  id: string
  formular_nr: string
  bezeichnung: string
  formularklasse: Formularklasse
  bank_blz: string | null
  bank_iban: string | null
  formulareinrichtung: string | null
  aktiv: boolean
  created_at: string
}

export type Zinsgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  zinssatz: number
  zinsmethode: Zinsmethode
  schwellwert_tage: number
  konto_zinsen: string | null
  konto_zinsabschlagsteuer: string | null
  aktiv: boolean
  created_at: string
}

export type LeergutArt = {
  id: string
  art_nr: string
  bezeichnung: string
  leergut_typ: LeergutTyp
  pfandwert: number | null
  konto_leergut: string | null
  aktiv: boolean
  created_at: string
}

// ========== QUERY KEYS ==========

export const FIBU_STAMM_KEYS = {
  zahlungsformulare: (klasse?: Formularklasse) =>
    ['fibu-zahlungsformulare', klasse ?? 'all'] as const,
  zinsgruppen: () => ['fibu-zinsgruppen'] as const,
  leergutarten: () => ['fibu-leergutarten'] as const,
}

const BASE = '/api/v1/fibu/stammdaten'

// ========== ZAHLUNGSFORMULARE ==========

export function useZahlungsformulare(formularklasse?: Formularklasse) {
  return useQuery({
    queryKey: FIBU_STAMM_KEYS.zahlungsformulare(formularklasse),
    queryFn: async () => {
      const params = formularklasse ? `?formularklasse=${formularklasse}` : ''
      const res = await apiClient.get<Zahlungsformular[]>(
        `${BASE}/zahlungsformulare${params}`
      )
      return res.data
    },
  })
}

export function useCreateZahlungsformular() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      formular_nr: string
      bezeichnung: string
      formularklasse: Formularklasse
      bank_blz?: string | null
      bank_iban?: string | null
      formulareinrichtung?: string | null
    }) => apiClient.post<Zahlungsformular>(`${BASE}/zahlungsformulare`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fibu-zahlungsformulare'] })
    },
  })
}

export function useDeleteZahlungsformular() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (formular_nr: string) =>
      apiClient.delete(`${BASE}/zahlungsformulare/${formular_nr}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fibu-zahlungsformulare'] })
    },
  })
}

// ========== ZINSGRUPPEN ==========

export function useZinsgruppen() {
  return useQuery({
    queryKey: FIBU_STAMM_KEYS.zinsgruppen(),
    queryFn: async () => {
      const res = await apiClient.get<Zinsgruppe[]>(`${BASE}/zinsgruppen`)
      return res.data
    },
  })
}

export function useCreateZinsgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      gruppe_nr: string
      bezeichnung: string
      zinssatz: number
      zinsmethode: Zinsmethode
      schwellwert_tage?: number
      konto_zinsen?: string | null
      konto_zinsabschlagsteuer?: string | null
    }) => apiClient.post<Zinsgruppe>(`${BASE}/zinsgruppen`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FIBU_STAMM_KEYS.zinsgruppen() })
    },
  })
}

export function useDeleteZinsgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (gruppe_nr: string) =>
      apiClient.delete(`${BASE}/zinsgruppen/${gruppe_nr}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FIBU_STAMM_KEYS.zinsgruppen() })
    },
  })
}

// ========== LEERGUTARTEN ==========

export function useLeergutarten() {
  return useQuery({
    queryKey: FIBU_STAMM_KEYS.leergutarten(),
    queryFn: async () => {
      const res = await apiClient.get<LeergutArt[]>(`${BASE}/leergutarten`)
      return res.data
    },
  })
}

export function useCreateLeergutart() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      art_nr: string
      bezeichnung: string
      leergut_typ: LeergutTyp
      pfandwert?: number | null
      konto_leergut?: string | null
    }) => apiClient.post<LeergutArt>(`${BASE}/leergutarten`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FIBU_STAMM_KEYS.leergutarten() })
    },
  })
}

export function useDeleteLeergutart() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (art_nr: string) =>
      apiClient.delete(`${BASE}/leergutarten/${art_nr}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FIBU_STAMM_KEYS.leergutarten() })
    },
  })
}
