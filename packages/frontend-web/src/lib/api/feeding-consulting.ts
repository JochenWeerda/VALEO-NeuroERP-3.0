import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding'

export type CaseType = 'visit' | 'remote'
export type CaseStatus = 'open' | 'closed'

export interface ConsultingCase {
  id: string
  case_type: CaseType
  title: string
  status: CaseStatus
  business_id?: string | null
  group_id?: string | null
  initial_situation?: string | null
  closing_summary?: string | null
  created_by: string
  created_at: string
  updated_at: string
  observation_count?: number | null
}

export interface ConsultingObservation {
  id: string
  case_id: string
  category: string
  text: string
  photo_document_refs: string[]
  ration_id?: string | null
  analysis_ref?: string | null
  observation_date?: string | null
  client_ref: string
  created_by: string
  created_at: string
  duplicate?: boolean | null
}

export interface ConsultingCaseDetail extends ConsultingCase {
  observations: ConsultingObservation[]
}

export interface ConsultingMeasure {
  measure_id: string
  title: string
  version: number
  status: 'open' | 'in_progress' | 'review_due' | 'completed' | 'cancelled'
  owner_subject: string
  due_date: string
  reminder_date?: string | null
  escalation_status: 'none' | 'attention' | 'escalated'
  effectiveness?: 'effective' | 'partial' | 'ineffective' | null
  effectiveness_result?: string | null
}

export interface ConsultingReportDraft {
  id: string
  case_id: string
  version: number
  content_hash: string
  content: Record<string, unknown>
}

export async function listConsultingCases(status?: CaseStatus): Promise<ConsultingCase[]> {
  const response = await apiClient.get<ConsultingCase[]>(`${BASE}/consulting-cases`, {
    params: status ? { status } : undefined,
  })
  return response.data
}

export async function getConsultingCase(caseId: string): Promise<ConsultingCaseDetail> {
  const response = await apiClient.get<ConsultingCaseDetail>(
    `${BASE}/consulting-cases/${encodeURIComponent(caseId)}`)
  return response.data
}

export async function createConsultingCase(input: {
  title: string
  case_type: CaseType
  business_id?: string
  group_id?: string
  initial_situation?: string
}): Promise<ConsultingCase> {
  const response = await apiClient.post<ConsultingCase>(`${BASE}/consulting-cases`, input)
  return response.data
}

export async function addConsultingObservation(caseId: string, input: {
  category: string
  text: string
  client_ref: string
  photo_document_refs?: string[]
  ration_id?: string
  observation_date?: string
}): Promise<ConsultingObservation> {
  const response = await apiClient.post<ConsultingObservation>(
    `${BASE}/consulting-cases/${encodeURIComponent(caseId)}/observations`, input)
  return response.data
}

export async function closeConsultingCase(caseId: string, summary: string): Promise<ConsultingCase> {
  const response = await apiClient.post<ConsultingCase>(
    `${BASE}/consulting-cases/${encodeURIComponent(caseId)}/close`, { summary })
  return response.data
}

export async function listCaseMeasures(caseId: string): Promise<ConsultingMeasure[]> {
  const response = await apiClient.get<ConsultingMeasure[]>(
    `${BASE}/consulting-cases/${encodeURIComponent(caseId)}/measures`)
  return response.data
}

export async function transitionFeedingMeasure(measureId: string, input: {
  expected_version: number
  target_status: 'in_progress' | 'review_due' | 'completed' | 'cancelled'
  reason: string
  effectiveness?: 'effective' | 'partial' | 'ineffective'
  effectiveness_result?: string
}): Promise<ConsultingMeasure> {
  const response = await apiClient.post<ConsultingMeasure>(
    `${BASE}/measures/${encodeURIComponent(measureId)}/transitions`, input)
  return response.data
}

export async function createConsultingReportDraft(
  caseId: string,
  reason: string,
): Promise<ConsultingReportDraft> {
  const response = await apiClient.post<ConsultingReportDraft>(
    `${BASE}/consulting-cases/${encodeURIComponent(caseId)}/report-drafts`, { reason })
  return response.data
}
