import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding'

export interface RationTemplate {
  id: string
  business_id: string
  group_id: string
  name: string
  description?: string | null
  source_ration_version_id: string
  source_ration_name: string
  source_version_no: number
  snapshot_checksum: string
  created_at: string
}

export interface BusinessRationSummary {
  id: string
  name: string
  group_id: string
  group_name: string
  version_id: string
  version_no: number
  status: string
  readiness_status: string
  readiness_blockers: number
  readiness_warnings: number
}

export async function fetchBusinessRations(businessId: string): Promise<BusinessRationSummary[]> {
  const response = await apiClient.get<BusinessRationSummary[]>(`${BASE}/businesses/${businessId}/rations`)
  return response.data
}

export async function fetchRationTemplates(businessId: string): Promise<RationTemplate[]> {
  const response = await apiClient.get<RationTemplate[]>(`${BASE}/businesses/${businessId}/ration-templates`)
  return response.data
}

export async function createRationTemplate(input: {
  name: string
  description?: string | null
  source_ration_version_id: string
}): Promise<RationTemplate> {
  const response = await apiClient.post<RationTemplate>(`${BASE}/ration-templates`, input)
  return response.data
}

export async function applyRationTemplate(templateId: string, input: {
  target_ration_id: string
  expected_latest_version_no: number
  reason: string
}): Promise<{ id: string; version_no: number }> {
  const response = await apiClient.post<{ id: string; version_no: number }>(`${BASE}/ration-templates/${templateId}/apply`, input)
  return response.data
}
