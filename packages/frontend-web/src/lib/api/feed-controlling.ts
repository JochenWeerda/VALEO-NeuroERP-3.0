import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/controlling'

export interface DailyFeedingObservationInput {
  group_id: string
  observation_date: string
  source: 'manual' | 'mixing_wagon' | 'herd_data' | 'import'
  source_ref: string
  cow_count?: number
  actual_dmi_kg_cow?: number
  actual_cost_eur_cow?: number
  milk_price_eur_kg?: number
  actual_milk_kg_cow?: number
  actual_fat_pct?: number
  actual_protein_pct?: number
  feed_n_kg_cow?: number
  actual_methane_kg_cow?: number
  methane_estimated?: boolean
}

export async function recordDailyFeedingObservation(input: DailyFeedingObservationInput): Promise<Record<string, unknown>> {
  const response = await apiClient.post<Record<string, unknown>>(`${BASE}/observations`, input)
  return response.data
}

/** Ein Tagespunkt der Soll-Ist-Reihe; unbekannte Messwerte sind fachlich `null`, nie 0. */
export interface ControllingSeriesPoint {
  group_id: string
  group_name: string
  observation_date: string
  version_no?: number | null
  feeding_plan_version_id?: string | null
  plan_version_no?: number | null
  cow_count?: number | null
  target_dmi_kg_cow?: number | null
  actual_dmi_kg_cow?: number | null
  target_cost_eur_cow?: number | null
  actual_cost_eur_cow?: number | null
  target_milk_kg_cow?: number | null
  actual_milk_kg_cow?: number | null
  actual_ecm_kg_cow?: number | null
  milk_price_eur_kg?: number | null
  milk_revenue_eur_cow?: number | null
  iofc_eur_cow?: number | null
  nitrogen_efficiency_pct?: number | null
  target_methane_kg_cow?: number | null
  actual_methane_kg_cow?: number | null
  methane_estimated?: boolean
  dmi_deviation_kg?: number | null
  cost_deviation_eur?: number | null
  milk_deviation_kg?: number | null
}

export interface ControllingSeriesQuery {
  groupId?: string
  dateFrom?: string
  dateTo?: string
}

export async function fetchControllingSeries(query: ControllingSeriesQuery = {}): Promise<ControllingSeriesPoint[]> {
  const params: Record<string, string> = {}
  if (query.groupId) params.group_id = query.groupId
  if (query.dateFrom) params.date_from = query.dateFrom
  if (query.dateTo) params.date_to = query.dateTo
  const response = await apiClient.get<ControllingSeriesPoint[]>(`${BASE}/series`, { params })
  return response.data ?? []
}
