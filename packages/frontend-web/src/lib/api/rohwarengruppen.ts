import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type RohwarengruppeOut = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  artikel_nr?: string | null
  ek_aktiv: boolean
  vk_aktiv: boolean
  waehrung: string
  mengeneinheit?: string | null
  aktiv: boolean
  created_at?: string | null
}

export type RohwarengruppePayload = {
  gruppe_nr: string
  bezeichnung: string
  artikel_nr?: string | null
  ek_aktiv?: boolean
  vk_aktiv?: boolean
  waehrung?: string
  mengeneinheit?: string | null
}

export type AbrechnungsschemaOut = {
  id: string
  schema_nr: string
  bezeichnung: string
  gruppe_id: string
}

export async function listRohwarengruppen(): Promise<RohwarengruppeOut[]> {
  return (await apiClient.get<RohwarengruppeOut[]>('/api/v1/rohware/gruppen')).data
}

export async function createRohwarengruppe(payload: RohwarengruppePayload): Promise<RohwarengruppeOut> {
  return (await apiClient.post<RohwarengruppeOut>('/api/v1/rohware/gruppen', payload)).data
}

export async function deleteRohwarengruppe(gruppe_nr: string): Promise<void> {
  await apiClient.delete(`/api/v1/rohware/gruppen/${encodeURIComponent(gruppe_nr)}`)
}

export async function listAbrechnungsschemata(gruppe_id: string): Promise<AbrechnungsschemaOut[]> {
  return (
    await apiClient.get<AbrechnungsschemaOut[]>(
      `/api/v1/rohware/gruppen/${encodeURIComponent(gruppe_id)}/schemata`,
    )
  ).data
}

export function useRohwarengruppen() {
  return useQuery({
    queryKey: ['rohwarengruppen'],
    queryFn: listRohwarengruppen,
  })
}

export function useCreateRohwarengruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createRohwarengruppe,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['rohwarengruppen'] }) },
  })
}

export function useDeleteRohwarengruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (gruppe_nr: string) => deleteRohwarengruppe(gruppe_nr),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['rohwarengruppen'] }) },
  })
}

export function useAbrechnungsschemata(gruppe_id: string | null) {
  return useQuery({
    queryKey: ['abrechnungsschemata', gruppe_id],
    queryFn: () => listAbrechnungsschemata(gruppe_id ?? ''),
    enabled: !!gruppe_id,
  })
}
