/**
 * API-Client für DSGVO Art. 33 Datenpannen-Meldeprozess.
 * Slice-009.
 */
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/gdpr/art33'

export type BreachType = 'VERTRAULICHKEIT' | 'INTEGRITAET' | 'VERFUEGBARKEIT'
export type BreachStatus = 'ENTDECKT' | 'IN_BEARBEITUNG' | 'GEMELDET' | 'ABGESCHLOSSEN'
export type TrafficLight = 'RED' | 'ORANGE' | 'GREEN'

export interface DataBreach {
  id: string
  tenant_id: string
  breach_type: BreachType
  description: string
  data_categories: string[]
  persons_count_approx: number
  records_count_approx: number
  dpo_name: string
  dpo_contact: string
  likely_consequences: string
  measures_taken: string
  discovered_at: string
  status: BreachStatus
  internal_reference: string
  created_at: string
  updated_at: string
  notified_at: string | null
  notified_by: string | null
  authority_reference: string | null
}

export type DataBreachInput = Omit<DataBreach, 'id' | 'tenant_id' | 'created_at' | 'updated_at' | 'notified_at' | 'notified_by' | 'authority_reference'>

export interface DeadlineInfo {
  breach_id: string
  discovered_at: string
  deadline_at: string
  hours_remaining: number
  hours_elapsed: number
  is_overdue: boolean
  is_notified: boolean
  traffic_light: TrafficLight
}

export interface NotifyPayload {
  notified_by: string
  authority_reference?: string
}

export async function listBreaches(status?: string): Promise<DataBreach[]> {
  const params = status ? { status } : {}
  const res = await apiClient.get<DataBreach[]>(`${BASE}/breaches`, { params })
  return res.data
}

export async function createBreach(payload: DataBreachInput): Promise<DataBreach> {
  const res = await apiClient.post<DataBreach>(`${BASE}/breaches`, payload)
  return res.data
}

export async function getBreach(id: string): Promise<DataBreach> {
  const res = await apiClient.get<DataBreach>(`${BASE}/breaches/${id}`)
  return res.data
}

export async function updateBreach(id: string, payload: DataBreachInput): Promise<DataBreach> {
  const res = await apiClient.put<DataBreach>(`${BASE}/breaches/${id}`, payload)
  return res.data
}

export async function getDeadline(id: string): Promise<DeadlineInfo> {
  const res = await apiClient.get<DeadlineInfo>(`${BASE}/breaches/${id}/deadline`)
  return res.data
}

export async function notifyAuthority(id: string, payload: NotifyPayload): Promise<DataBreach> {
  const res = await apiClient.post<DataBreach>(`${BASE}/breaches/${id}/notify`, payload)
  return res.data
}
