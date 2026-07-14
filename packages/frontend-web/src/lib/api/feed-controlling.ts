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
