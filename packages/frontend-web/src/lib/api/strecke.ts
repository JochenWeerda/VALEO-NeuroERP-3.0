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
