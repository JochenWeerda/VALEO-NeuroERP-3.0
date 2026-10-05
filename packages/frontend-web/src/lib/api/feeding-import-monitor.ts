import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding'

export type ImportAdapter = 'agrirouter' | 'icar-ade' | 'laboratory'
export type ImportJobStatus = 'validated' | 'quarantined' | 'accepted' | 'rejected'

export interface ImportFinding {
  severity: string
  message: string
}

export interface ImportJob {
  id: string
  adapter: ImportAdapter
  status: ImportJobStatus
  findings: ImportFinding[]
  mapped_excerpt: Record<string, unknown>
  result_ref?: string | null
  decision_reason?: string | null
  decided_by?: string | null
  decided_at?: string | null
  created_by: string
  created_at: string
}

export async function listImportJobs(status?: ImportJobStatus): Promise<ImportJob[]> {
  const response = await apiClient.get<ImportJob[]>(`${BASE}/imports`, {
    params: status ? { status } : undefined,
  })
  return response.data
}

export async function acceptImportJob(jobId: string): Promise<ImportJob> {
  const response = await apiClient.post<ImportJob>(
    `${BASE}/imports/${encodeURIComponent(jobId)}/accept`, {})
  return response.data
}

export async function rejectImportJob(jobId: string, reason: string): Promise<ImportJob> {
  const response = await apiClient.post<ImportJob>(
    `${BASE}/imports/${encodeURIComponent(jobId)}/reject`, { reason })
  return response.data
}
