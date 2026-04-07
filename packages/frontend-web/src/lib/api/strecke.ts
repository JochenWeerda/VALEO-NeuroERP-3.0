import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ── Speditionen / Frachttarife nach PLZ ──────────────────────────────────

export type SpeditionFrachttarif = {
  id: string
  plz_von: string
  plz_bis: string
  spediteur: string
  preis_eur_t: number
  aktiv: boolean
  notiz?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type SpeditionFrachttarifPayload = Omit<SpeditionFrachttarif, 'id' | 'created_at' | 'updated_at'>

export async function listFrachttarife(params?: { aktiv_only?: boolean }): Promise<SpeditionFrachttarif[]> {
  const q = params?.aktiv_only ? '?aktiv_only=true' : ''
  return (await apiClient.get<SpeditionFrachttarif[]>(`/api/v1/strecke/speditionen/frachttarife${q}`)).data
}

export async function getFrachttarif(id: string): Promise<SpeditionFrachttarif> {
  return (await apiClient.get<SpeditionFrachttarif>(`/api/v1/strecke/speditionen/frachttarife/${id}`)).data
}

export async function createFrachttarif(payload: SpeditionFrachttarifPayload): Promise<SpeditionFrachttarif> {
  return (await apiClient.post<SpeditionFrachttarif>('/api/v1/strecke/speditionen/frachttarife', payload)).data
}

export async function updateFrachttarif(
  id: string,
  payload: SpeditionFrachttarifPayload,
): Promise<SpeditionFrachttarif> {
  return (await apiClient.patch<SpeditionFrachttarif>(`/api/v1/strecke/speditionen/frachttarife/${id}`, payload)).data
}

export async function deleteFrachttarif(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/strecke/speditionen/frachttarife/${id}`)
}

// ── Strecke Tours ─────────────────────────────────────────────────────────

export type StreckeTour = {
  id: string
  tour_no: string
  date: string
  week?: string | null
  type: string
  status: string
  notes?: string | null
}

export type StreckeCreateTourPayload = {
  date: string
  type?: string
  planned_departure_at?: string | null
  notes?: string | null
}

export async function listStreckeTouren(): Promise<StreckeTour[]> {
  return (await apiClient.get<StreckeTour[]>('/api/v1/tours')).data
}

export async function createStreckeTour(payload: StreckeCreateTourPayload): Promise<StreckeTour> {
  return (await apiClient.post<StreckeTour>('/api/v1/tours', payload)).data
}

export async function deleteStreckeTour(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/tours/${id}`)
}

// ── Streckengeschaefte ──────────────────────────────────────────────────────

export type Streckengeschaeft = {
  id: string
  strecke_nr: string
  datum: string
  niederlassung: string
  partie_nr: string
  kostenstelle: string
  lagerhalle: string
  nls_nr: string
  erledigt: boolean
  lieferant_name: string
  lieferant_nr: string
  kontrakt_nr: string
  artikel: string
  netto: number
  mwst: number
  brutto: number
  rechnungsnr: string
  bediener: string
  notiz: string
  erstellt: string
}

export type StreckengeschaeftCreate = Omit<Streckengeschaeft, 'id' | 'strecke_nr' | 'erstellt'>

export type StreckengeschaeftUpdate = Partial<StreckengeschaeftCreate>

export async function listStreckengeschaefte(params?: { erledigt?: boolean }): Promise<Streckengeschaeft[]> {
  const q = params?.erledigt !== undefined ? `?erledigt=${params.erledigt}` : ''
  return (await apiClient.get<Streckengeschaeft[]>(`/api/v1/strecke/streckengeschaefte${q}`)).data
}

export async function getStreckengeschaeft(id: string): Promise<Streckengeschaeft> {
  return (await apiClient.get<Streckengeschaeft>(`/api/v1/strecke/streckengeschaefte/${id}`)).data
}

export async function createStreckengeschaeft(payload: StreckengeschaeftCreate): Promise<Streckengeschaeft> {
  return (await apiClient.post<Streckengeschaeft>('/api/v1/strecke/streckengeschaefte', payload)).data
}

export async function updateStreckengeschaeft(id: string, payload: StreckengeschaeftUpdate): Promise<Streckengeschaeft> {
  return (await apiClient.patch<Streckengeschaeft>(`/api/v1/strecke/streckengeschaefte/${id}`, payload)).data
}

export async function deleteStreckengeschaeft(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/strecke/streckengeschaefte/${id}`)
}

export function useStreckengeschaefte(params?: { erledigt?: boolean }) {
  return useQuery({
    queryKey: ['strecke', 'geschaefte', params],
    queryFn: () => listStreckengeschaefte(params),
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useStreckengeschaeft(id: string | null) {
  return useQuery({
    queryKey: ['strecke', 'geschaeft', id],
    queryFn: async () => {
      if (!id) {
        throw new Error('Streckengeschaeft ID is required')
      }
      return getStreckengeschaeft(id)
    },
    enabled: !!id,
    staleTime: 60 * 1000,
  })
}

export function useCreateStreckengeschaeft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createStreckengeschaeft,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['strecke', 'geschaefte'] }),
  })
}

export function useUpdateStreckengeschaeft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StreckengeschaeftUpdate }) => updateStreckengeschaeft(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['strecke'] }),
  })
}

export function useDeleteStreckengeschaeft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteStreckengeschaeft,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['strecke', 'geschaefte'] }),
  })
}
