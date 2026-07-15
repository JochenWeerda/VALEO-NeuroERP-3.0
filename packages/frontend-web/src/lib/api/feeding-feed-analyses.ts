import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feed-analyses'

export type AnalysisStatus = 'uploaded' | 'mapped' | 'draft' | 'validated' | 'released' | 'superseded' | 'rejected'
export type AnalysisValueStatus = 'measured' | 'calculated' | 'estimated'

export interface FeedingAnalysisValueInput {
  nutrient_code: string
  original_value: string
  original_unit_code: string
  canonical_unit_code: string
  basis: 'fresh_matter' | 'dry_matter'
  value_status: AnalysisValueStatus
  method?: string
  source_ref?: string
}

export interface FeedingAnalysisDetail {
  id: string
  feed_id?: string | null
  bezeichnung: string
  probe_nr?: string | null
  labor?: string | null
  method?: string | null
  status: AnalysisStatus
  is_active: boolean
  revision: number
  findings: Array<{ severity: string; message: string }>
}

export interface FeedingAnalysisCreateInput {
  feed_id?: string
  bezeichnung: string
  probe_nr?: string
  probenart?: string
  labor?: string
  method?: string
  analyse_datum?: string
  quelle_datei?: string
  original_sha256?: string
  original_document_id?: string
  status?: 'uploaded' | 'mapped' | 'draft'
  values: FeedingAnalysisValueInput[]
}

export interface FeedingAnalysisImportPreview {
  filename: string
  sha256: string
  quarantine_status: 'preview_only'
  confidence: string
  warnings: string[]
  analysis: Partial<FeedingAnalysisCreateInput>
  values: FeedingAnalysisValueInput[]
}

export async function previewFeedingAnalysisImport(file: File): Promise<FeedingAnalysisImportPreview> {
  const form = new FormData()
  form.append('file', file)
  return (await apiClient.post<FeedingAnalysisImportPreview>(`${BASE}/import-preview`, form)).data
}

export async function createFeedingAnalysis(body: FeedingAnalysisCreateInput): Promise<FeedingAnalysisDetail> {
  const response = await apiClient.post<FeedingAnalysisDetail>(BASE, body)
  return response.data
}

export async function validateFeedingAnalysis(id: string, expectedRevision: number): Promise<FeedingAnalysisDetail> {
  const response = await apiClient.post<FeedingAnalysisDetail>(`${BASE}/${encodeURIComponent(id)}/validate`, {
    expected_revision: expectedRevision,
  })
  return response.data
}

export async function transitionFeedingAnalysis(
  id: string, targetStatus: 'released' | 'rejected', expectedRevision: number, reason: string,
): Promise<FeedingAnalysisDetail> {
  const response = await apiClient.post<FeedingAnalysisDetail>(`${BASE}/${encodeURIComponent(id)}/transition`, {
    target_status: targetStatus, expected_revision: expectedRevision, reason,
  })
  return response.data
}
