import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding/actuals'

export type ActualCause = 'normal' | 'stock_substitution' | 'dosing_error' | 'feed_quality' | 'animal_intake' | 'technical' | 'other'

export interface ActualComponent {
  id: string
  feed_id: string
  feed_name: string | null
  target_kg: number
  actual_kg: number
  delta_kg: number
  delta_pct: number | null
  value_consequences: {
    cost: { delta_eur: string } | null
    missing: string[]
    nutrients: Array<{ code: string; delta: string; result_unit: string }>
  }
}

export interface ActualFeedingRecord {
  id: string
  plan_version_id: string
  group_id: string
  feeding_at: string
  cause_class: ActualCause
  comment: string | null
  context: Record<string, unknown>
  components: ActualComponent[]
}

export async function fetchActualFeedings(): Promise<ActualFeedingRecord[]> {
  const response = await apiClient.get<ActualFeedingRecord[]>(BASE)
  return response.data
}

export async function recordActualFeeding(payload: {
  plan_version_id: string
  feeding_at: string
  source: 'manual'
  source_ref: string
  cause_class: ActualCause
  comment: string | null
  context: Record<string, unknown>
  supersedes_id: string | null
  idempotency_key: string
  components: Array<{ feed_id: string; actual_kg: number }>
}): Promise<ActualFeedingRecord> {
  const response = await apiClient.post<ActualFeedingRecord>(BASE, payload)
  return response.data
}

export async function exportActualFeedingsCsv(): Promise<Blob> {
  const response = await apiClient.get(`${BASE}/export.csv`, { responseType: 'blob' })
  return response.data as Blob
}
