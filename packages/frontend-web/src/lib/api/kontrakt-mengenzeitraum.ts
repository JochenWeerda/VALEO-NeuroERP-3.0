/**
 * Kontrakt-Mengenzeiträume + Kontrakt-Zu-/Abschläge (Fachliche Vertiefung Wave 2).
 * TanStack-Query-Hooks für /api/v1/kontrakte/*.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/kontrakte'

// ── Typen ─────────────────────────────────────────────────────────────────────
export type Mengenzeitraum = {
  id: string
  kontrakt_nr: string
  zeitraum_von: string
  zeitraum_bis: string
  menge_t: number
  menge_bereits_geliefert_t: number
  menge_restmenge_t: number | null
  variante: string | null
  status: string
  bemerkung: string | null
  created_at: string
}

export type MengenzeitraumCreate = {
  kontrakt_nr: string
  zeitraum_von: string
  zeitraum_bis: string
  menge_t: number
  variante?: string | null
  bemerkung?: string | null
}

export type ZuAbschlagsGruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  typ: string
  aktiv?: boolean
  created_at?: string
}

export type ZuAbschlag = {
  id: string
  gruppe_id: string
  kontrakt_nr: string | null
  bezeichnung: string
  betrag_eur: number | null
  prozent: number | null
  einheit: string
  gueltig_ab: string | null
  gueltig_bis: string | null
  aktiv: boolean
  created_at: string
}

export type ZuAbschlagCreate = {
  gruppe_id: string
  kontrakt_nr?: string | null
  bezeichnung: string
  betrag_eur?: number | null
  prozent?: number | null
  einheit?: string
  gueltig_ab?: string | null
  gueltig_bis?: string | null
}

// ── Mengenzeiträume ───────────────────────────────────────────────────────────
export function useMengenzeitraeume(kontraktNr: string) {
  return useQuery({
    queryKey: ['kontrakt', 'mengenzeitraeume', kontraktNr],
    enabled: !!kontraktNr,
    queryFn: async () =>
      (await apiClient.get<Mengenzeitraum[]>(`${BASE}/${encodeURIComponent(kontraktNr)}/mengenzeitraeume`)).data,
  })
}

export function useCreateMengenzeitraum() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: MengenzeitraumCreate) =>
      (await apiClient.post<Mengenzeitraum>(`${BASE}/${encodeURIComponent(body.kontrakt_nr)}/mengenzeitraeume`, body)).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['kontrakt', 'mengenzeitraeume', v.kontrakt_nr] }),
  })
}

export function useDeleteMengenzeitraum() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ kontraktNr, id }: { kontraktNr: string; id: string }) =>
      (await apiClient.delete(`${BASE}/${encodeURIComponent(kontraktNr)}/mengenzeitraeume/${encodeURIComponent(id)}`)).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['kontrakt', 'mengenzeitraeume', v.kontraktNr] }),
  })
}

export function useGenerateMengenzeitraeume() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (v: { kontraktNr: string; von_datum: string; bis_datum: string; gesamt_menge_t: number; variante?: string }) =>
      (await apiClient.post(`${BASE}/${encodeURIComponent(v.kontraktNr)}/mengenzeitraeume/generieren`, null, {
        params: { von_datum: v.von_datum, bis_datum: v.bis_datum, gesamt_menge_t: v.gesamt_menge_t, variante: v.variante ?? 'monatl. lin. Abnahme' },
      })).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['kontrakt', 'mengenzeitraeume', v.kontraktNr] }),
  })
}

// ── Zu-/Abschlagsgruppen + Positionen ─────────────────────────────────────────
export function useZuAbschlagsgruppen() {
  return useQuery({
    queryKey: ['kontrakt', 'zuabschlagsgruppen'],
    queryFn: async () => (await apiClient.get<ZuAbschlagsGruppe[]>(`${BASE}/zuabschlagsgruppen`)).data,
  })
}

export function useCreateZuAbschlagsgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: { gruppe_nr: string; bezeichnung: string; typ: string }) =>
      (await apiClient.post<ZuAbschlagsGruppe>(`${BASE}/zuabschlagsgruppen`, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['kontrakt', 'zuabschlagsgruppen'] }),
  })
}

export function useZuAbschlaege(gruppeId: string) {
  return useQuery({
    queryKey: ['kontrakt', 'zuabschlaege', gruppeId],
    enabled: !!gruppeId,
    queryFn: async () =>
      (await apiClient.get<ZuAbschlag[]>(`${BASE}/zuabschlagsgruppen/${encodeURIComponent(gruppeId)}/positionen`)).data,
  })
}

export function useCreateZuAbschlag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: ZuAbschlagCreate) =>
      (await apiClient.post<ZuAbschlag>(`${BASE}/zuabschlagsgruppen/${encodeURIComponent(body.gruppe_id)}/positionen`, body)).data,
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ['kontrakt', 'zuabschlaege', v.gruppe_id] }),
  })
}
