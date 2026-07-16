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

export interface DeviationFinding {
  actual_component_id: string
  actual_record_id: string
  plan_version_id: string
  group_id: string
  feed_id: string
  feed_name: string | null
  severity: 'warning' | 'critical' | 'unconfigured'
  message: string
  delta_kg?: number
  delta_pct?: number
  threshold_pct?: number
  feed_class: string
  policy_version?: number
  remedy?: string
}

export interface ActualMeasure {
  id: string
  actual_component_id: string
  title: string
  owner_subject: string
  due_date: string
  status: 'open'
  reason: string
  finding: DeviationFinding
}

export async function fetchDeviationFindings(): Promise<DeviationFinding[]> {
  const response = await apiClient.get<DeviationFinding[]>(`${BASE}/findings`)
  return response.data
}

export async function fetchActualMeasures(): Promise<ActualMeasure[]> {
  const response = await apiClient.get<ActualMeasure[]>(`${BASE}/measures`)
  return response.data
}

export async function createActualMeasure(payload: {
  actual_component_id: string
  title: string
  owner_subject: string
  due_date: string
  reason: string
  idempotency_key: string
}): Promise<ActualMeasure> {
  const response = await apiClient.post<ActualMeasure>(`${BASE}/measures`, payload)
  return response.data
}

export interface DeviationPolicy {
  id: string
  feed_class: string
  version: number
  warning_pct: number
  critical_pct: number
  valid_from: string
  reason: string
}

export async function fetchDeviationPolicies(): Promise<DeviationPolicy[]> {
  const response = await apiClient.get<DeviationPolicy[]>(`${BASE}/deviation-policies`)
  return response.data
}

export async function createDeviationPolicy(payload: {
  feed_class: string
  warning_pct: number
  critical_pct: number
  valid_from: string
  reason: string
}): Promise<DeviationPolicy> {
  const response = await apiClient.post<DeviationPolicy>(`${BASE}/deviation-policies`, payload)
  return response.data
}
