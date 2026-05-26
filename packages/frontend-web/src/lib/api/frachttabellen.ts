import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type FrachttabelleOut = {
  id: string
  tabelle_nr: string
  bezeichnung: string
  einheit?: string | null
  waehrung: string
  aktiv: boolean
  created_at?: string | null
}

export type FrachttabellePayload = {
  tabelle_nr: string
  bezeichnung: string
  einheit?: string | null
  waehrung?: string
}

export type FrachttabellePositionOut = {
  id: string
  tabelle_nr: string
  ab_menge: number
  frachtsatz_eur: number
  mindestfracht_eur?: number | null
  created_at?: string | null
}

export type FrachttabellePositionPayload = {
  ab_menge: number
  frachtsatz_eur: number
  mindestfracht_eur?: number | null
}

export async function listFrachttabellen(): Promise<FrachttabelleOut[]> {
  return (await apiClient.get<FrachttabelleOut[]>('/api/v1/logistik/frachttabellen')).data
}

export async function createFrachttabelle(payload: FrachttabellePayload): Promise<FrachttabelleOut> {
  return (await apiClient.post<FrachttabelleOut>('/api/v1/logistik/frachttabellen', payload)).data
}

export async function deleteFrachttabelle(tabelle_nr: string): Promise<void> {
  await apiClient.delete(`/api/v1/logistik/frachttabellen/${encodeURIComponent(tabelle_nr)}`)
}

export async function listFrachttabellePositionen(tabelle_nr: string): Promise<FrachttabellePositionOut[]> {
  return (
    await apiClient.get<FrachttabellePositionOut[]>(
      `/api/v1/logistik/frachttabellen/${encodeURIComponent(tabelle_nr)}/positionen`,
    )
  ).data
}

export async function createFrachttabellePosition(
  tabelle_nr: string,
  payload: FrachttabellePositionPayload,
): Promise<FrachttabellePositionOut> {
  return (
    await apiClient.post<FrachttabellePositionOut>(
      `/api/v1/logistik/frachttabellen/${encodeURIComponent(tabelle_nr)}/positionen`,
      payload,
    )
  ).data
}

export function useFrachttabellen() {
  return useQuery({
    queryKey: ['frachttabellen'],
    queryFn: listFrachttabellen,
  })
}

export function useCreateFrachttabelle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createFrachttabelle,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['frachttabellen'] }) },
  })
}

export function useDeleteFrachttabelle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (tabelle_nr: string) => deleteFrachttabelle(tabelle_nr),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['frachttabellen'] }) },
  })
}

export function useFrachttabellePositionen(tabelle_nr: string | null) {
  return useQuery({
    queryKey: ['frachttabelle-positionen', tabelle_nr],
    queryFn: () => listFrachttabellePositionen(tabelle_nr ?? ''),
    enabled: !!tabelle_nr,
  })
}

export function useCreateFrachttabellePosition(tabelle_nr: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: FrachttabellePositionPayload) =>
      createFrachttabellePosition(tabelle_nr ?? '', payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['frachttabelle-positionen', tabelle_nr] })
    },
  })
}
