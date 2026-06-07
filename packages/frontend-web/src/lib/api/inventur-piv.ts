/**
 * Permanente Inventur (PIV) — Fachliche Vertiefung Wave 3.
 * TanStack-Query-Hooks für /api/v1/inventur/piv.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/inventur/piv'

export type PIVAbschluss = {
  id: string
  abschluss_datum: string
  inventurgruppe_nr: string | null
  lager_nr: string | null
  status: string
  erfasst_von: string | null
  abgeschlossen_von: string | null
  abgeschlossen_am: string | null
  anzahl_positionen: number
  differenzwert_eur: number | null
  bemerkung: string | null
  created_at: string
}

export type PIVAbschlussCreate = {
  abschluss_datum: string
  inventurgruppe_nr?: string | null
  lager_nr?: string | null
  bemerkung?: string | null
}

export type PIVPosition = {
  id: string
  abschluss_id: string
  artikel_nr: string
  lagerplatz: string | null
  buchbestand: number
  zaehlmenge: number | null
  differenz: number | null
  bewertungspreis_eur: number | null
  differenzwert_eur: number | null
  erfasst: boolean
  ignoriert: boolean
  created_at: string
}

export type PIVPositionCreate = {
  artikel_nr: string
  lagerplatz?: string | null
  buchbestand: number
  bewertungspreis_eur?: number | null
}

export function usePIVAbschluesse() {
  return useQuery({
    queryKey: ['piv', 'abschluesse'],
    queryFn: async () => (await apiClient.get<PIVAbschluss[]>(BASE)).data,
  })
}

export function useCreatePIVAbschluss() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: PIVAbschlussCreate) => (await apiClient.post<PIVAbschluss>(BASE, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['piv', 'abschluesse'] }),
  })
}

export function usePIVPositionen(abschlussId: string) {
  return useQuery({
    queryKey: ['piv', 'positionen', abschlussId],
    enabled: !!abschlussId,
    queryFn: async () => (await apiClient.get<PIVPosition[]>(`${BASE}/${encodeURIComponent(abschlussId)}/positionen`)).data,
  })
}

export function useCreatePIVPosition() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ abschlussId, body }: { abschlussId: string; body: PIVPositionCreate }) =>
      (await apiClient.post<PIVPosition>(`${BASE}/${encodeURIComponent(abschlussId)}/positionen`, body)).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['piv', 'positionen', v.abschlussId] }),
  })
}

export function useZaehlen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ abschlussId, posId, zaehlmenge, ignoriert }: { abschlussId: string; posId: string; zaehlmenge: number; ignoriert?: boolean }) =>
      (await apiClient.patch<PIVPosition>(`${BASE}/${encodeURIComponent(abschlussId)}/positionen/${encodeURIComponent(posId)}/zaehlen`, { zaehlmenge, ignoriert: ignoriert ?? false })).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['piv', 'positionen', v.abschlussId] }),
  })
}

export function useAbschliessen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (abschlussId: string) =>
      (await apiClient.post<PIVAbschluss>(`${BASE}/${encodeURIComponent(abschlussId)}/abschliessen`, {})).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['piv'] }),
  })
}
