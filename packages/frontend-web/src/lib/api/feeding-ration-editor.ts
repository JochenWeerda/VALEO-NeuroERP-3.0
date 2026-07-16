import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization'

export interface DraftComponent {
  feed_id: string
  name?: string
  kg_fm: number
}

export interface DraftDelta {
  metric: string
  actual: number
  target: number
  delta: number
}

export interface DraftFinding {
  code: string
  severity: 'blocker' | 'warning' | 'info'
  metric: string
  actual: number
  target?: number | null
  message: string
}

export interface DraftPosition {
  feed_id: string
  name: string
  kg_fm: number
  kg_tm: number
  cost_eur: number
  [nutrient: string]: string | number | null | undefined
}

export interface RationDraftEvaluation {
  group_id: string
  requirement_profile_id: string
  positions: DraftPosition[]
  totals: Record<string, number>
  coverage: Record<string, { complete: boolean; missing_feed_ids: string[] }>
  deltas: DraftDelta[]
  findings: DraftFinding[]
}

export async function evaluateRationDraft(input: {
  group_id: string
  requirement_profile_id?: string
  components: Array<{ feed_id: string; kg_fm: number }>
}): Promise<RationDraftEvaluation> {
  const response = await apiClient.post<RationDraftEvaluation>(`${BASE}/feeding/ration-drafts/evaluate`, input)
  return response.data
}

export interface CreatedRationVersion {
  id: string
  version_no: number
}

/** Append-only Speichern ueber den bestehenden Lifecycle-Vertrag (optimistische Revision). */
export async function createRationVersion(rationId: string, input: {
  snapshot: Record<string, unknown>
  expected_latest_version_no: number
  comment?: string
}): Promise<CreatedRationVersion> {
  const response = await apiClient.post<CreatedRationVersion>(
    `${BASE}/lifecycle/rations/${encodeURIComponent(rationId)}/versions`,
    { ...input, source: 'editor' },
  )
  return response.data
}

export interface ComponentDiff {
  feed_id: string
  name: string
  base_kg_fm: number | null
  variant_kg_fm: number | null
  delta_kg_fm: number | null
  change: 'added' | 'removed' | 'changed' | 'unchanged'
}

export interface MetricDiff {
  metric: string
  label: string
  base: number
  variant: number
  delta: number
}

export interface VersionComparison {
  group_id: string
  requirement_profile_id: string
  base: { version_id: string; ration_id: string; totals: Record<string, number> }
  variant: { version_id: string; ration_id: string; totals: Record<string, number> }
  component_diff: ComponentDiff[]
  metric_diff: MetricDiff[]
  base_findings: DraftFinding[]
  variant_findings: DraftFinding[]
}

export async function compareRationVersions(input: {
  base_version_id: string
  variant_version_id: string
}): Promise<VersionComparison> {
  const response = await apiClient.post<VersionComparison>(`${BASE}/feeding/ration-versions/compare`, input)
  return response.data
}
