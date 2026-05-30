/**
 * Individuelle Artikelnummern — TanStack Query Hooks für /api/v1/artikel/individuelle-nummern
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type IndivArtikelNr = {
  id: string
  artikel_nr: string
  partner_nr: string
  partner_typ: 'kunden' | 'lieferanten'
  indiv_artikel_nr: string
  indiv_bezeichnung: string | null
  gueltig_von: string | null
  gueltig_bis: string | null
  aktiv: boolean
  created_at: string
}

export type IndivArtikelNrCreate = {
  artikel_nr: string
  partner_nr: string
  partner_typ?: 'kunden' | 'lieferanten'
  indiv_artikel_nr: string
  indiv_bezeichnung?: string | null
  gueltig_von?: string | null
  gueltig_bis?: string | null
}

/** Tatsächliche Lookup-Response (weicht vom Backend-Deklarationsmodell ab). */
export type IndivArtikelNrLookupResult = {
  interne_artikel_nr: string
  indiv_bezeichnung: string | null
}

export type IndivArtikelNrListFilters = {
  partner_nr?: string
  partner_typ?: 'kunden' | 'lieferanten'
  artikel_nr?: string
}

// ========== QUERY KEYS ==========

export const ianKeys = {
  list: (filters?: IndivArtikelNrListFilters) => ['individuelle-artikelnummern', filters ?? {}] as const,
}

const BASE = '/api/v1/artikel/individuelle-nummern'

function buildListParams(filters?: IndivArtikelNrListFilters): string {
  const params = new URLSearchParams()
  if (filters?.partner_nr) params.set('partner_nr', filters.partner_nr)
  if (filters?.partner_typ) params.set('partner_typ', filters.partner_typ)
  if (filters?.artikel_nr) params.set('artikel_nr', filters.artikel_nr)
  const qs = params.toString()
  return qs ? `${BASE}?${qs}` : BASE
}

// ========== HOOKS ==========

export function useIndividuelleArtikelnummern(filters?: IndivArtikelNrListFilters) {
  return useQuery({
    queryKey: ianKeys.list(filters),
    queryFn: async () => {
      const res = await apiClient.get<IndivArtikelNr[]>(buildListParams(filters))
      return res.data
    },
  })
}

export function useCreateIndividuelleArtikelnummer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: IndivArtikelNrCreate) => {
      const res = await apiClient.post<IndivArtikelNr>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['individuelle-artikelnummern'] })
    },
  })
}

export function useDeleteIndividuelleArtikelnummer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${BASE}/${encodeURIComponent(id)}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['individuelle-artikelnummern'] })
    },
  })
}

export function useLookupIndividuelleArtikelnummer() {
  return useMutation({
    mutationFn: async (params: {
      partner_nr: string
      indiv_artikel_nr: string
      partner_typ?: 'kunden' | 'lieferanten'
    }) => {
      const qs = new URLSearchParams({
        partner_nr: params.partner_nr,
        indiv_artikel_nr: params.indiv_artikel_nr,
        partner_typ: params.partner_typ ?? 'kunden',
      })
      const res = await apiClient.get<IndivArtikelNrLookupResult>(`${BASE}/lookup?${qs.toString()}`)
      return res.data
    },
  })
}
