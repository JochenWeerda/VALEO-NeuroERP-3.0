/**
 * API-Client für DSGVO Art. 30 Verarbeitungsverzeichnis (RoPA).
 * Slice-008.
 */
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/gdpr/art30'

export interface ThirdCountryTransfer {
  country: string
  guarantee: string
}

export interface ProcessingActivity {
  id: string
  tenant_id: string
  controller_name: string
  controller_contact: string
  purpose: string
  subject_categories: string[]
  data_categories: string[]
  recipients: string[]
  third_country_transfers: ThirdCountryTransfer[]
  retention_period: string
  toms: string
  legal_basis: string
  system_or_tool: string
  status: 'AKTIV' | 'INAKTIV' | 'ENTWURF'
  created_at: string
  updated_at: string
}

export type ProcessingActivityInput = Omit<ProcessingActivity, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>

export async function listActivities(status?: string): Promise<ProcessingActivity[]> {
  const params = status ? { status } : {}
  const res = await apiClient.get<ProcessingActivity[]>(`${BASE}/activities`, { params })
  return res.data
}

export async function createActivity(payload: ProcessingActivityInput): Promise<ProcessingActivity> {
  const res = await apiClient.post<ProcessingActivity>(`${BASE}/activities`, payload)
  return res.data
}

export async function getActivity(id: string): Promise<ProcessingActivity> {
  const res = await apiClient.get<ProcessingActivity>(`${BASE}/activities/${id}`)
  return res.data
}

export async function updateActivity(id: string, payload: ProcessingActivityInput): Promise<ProcessingActivity> {
  const res = await apiClient.put<ProcessingActivity>(`${BASE}/activities/${id}`, payload)
  return res.data
}

export async function deleteActivity(id: string): Promise<void> {
  await apiClient.delete(`${BASE}/activities/${id}`)
}

export async function downloadExportJson(): Promise<void> {
  const res = await apiClient.get<Blob>(`${BASE}/activities/export/json`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'art30-verarbeitungsverzeichnis.json'
  a.click()
  URL.revokeObjectURL(url)
}
