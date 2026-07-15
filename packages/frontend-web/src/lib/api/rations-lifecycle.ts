import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/lifecycle'
const READINESS_BASE = '/api/v1/agrar/rations-optimization/readiness'

export interface FeedReadiness {
  as_of: string
  status: 'ready' | 'warning' | 'blocked'
  blocker_count: number
  warning_count: number
  materials: Array<Record<string, unknown>>
}

export async function evaluateFeedReadiness(snapshot: Record<string, unknown>): Promise<FeedReadiness> {
  return apiClient.post<FeedReadiness>(`${READINESS_BASE}/evaluate`, { snapshot })
}

export type RationStatus = 'draft' | 'in_review' | 'approved' | 'scheduled' | 'active' | 'retired' | 'archived'

export interface FeedingGroup {
  id: string
  business_id?: string | null
  herd_id?: string | null
  external_ref?: string | null
  name: string
  animal_count: number
  body_mass_kg?: number | null
  days_in_milk?: number | null
  lactation_number?: number | null
  target_milk_kg?: number | null
  feeding_system: string
  location?: string | null
  active: boolean
}

export interface RationVersion {
  id: string
  version_no: number
  status: RationStatus
  feeding_start?: string | null
  snapshot: Record<string, unknown>
  snapshot_checksum: string
}

export interface RationDetail {
  id: string
  group_id: string
  group_name: string
  name: string
  description?: string | null
  latest_version_id: string
  latest_version_no: number
  latest_status: RationStatus
  latest_feeding_start?: string | null
  latest_readiness_status?: 'ready' | 'warning' | 'blocked' | 'not_checked'
  latest_readiness_blockers?: number
  latest_readiness_warnings?: number
  versions: RationVersion[]
  audit: Array<Record<string, unknown>>
}

export async function fetchFeedingGroups(): Promise<FeedingGroup[]> {
  const response = await apiClient.get<FeedingGroup[]>(`${BASE}/groups`)
  return response.data
}

export async function createFeedingGroup(input: Omit<FeedingGroup, 'id' | 'active'> & { active?: boolean }): Promise<FeedingGroup> {
  const response = await apiClient.post<FeedingGroup>(`${BASE}/groups`, input)
  return response.data
}

export async function createRationDraft(input: {
  group_id: string
  name: string
  description?: string
  snapshot: Record<string, unknown>
  source?: 'solver' | 'manual' | 'import'
  comment?: string
}): Promise<RationDetail> {
  const response = await apiClient.post<RationDetail>(`${BASE}/rations`, input)
  return response.data
}

export async function fetchRationDetail(rationId: string): Promise<RationDetail> {
  const response = await apiClient.get<RationDetail>(`${BASE}/rations/${encodeURIComponent(rationId)}`)
  return response.data
}

export async function fetchActiveRations(): Promise<Array<{
  ration_id: string
  version_id: string
  group_id: string
  group_name: string
  snapshot: { mobile?: Record<string, unknown> }
}>> {
  const response = await apiClient.get(`${BASE}/active-rations`)
  return response.data as Array<{
    ration_id: string
    version_id: string
    group_id: string
    group_name: string
    snapshot: { mobile?: Record<string, unknown> }
  }>
}

export async function transitionRationVersion(input: {
  versionId: string
  expectedStatus: RationStatus
  targetStatus: RationStatus
  reason?: string
  feedingStart?: string
}): Promise<Record<string, unknown>> {
  const response = await apiClient.post(`${BASE}/versions/${encodeURIComponent(input.versionId)}/transitions`, {
    expected_status: input.expectedStatus,
    target_status: input.targetStatus,
    reason: input.reason,
    feeding_start: input.feedingStart,
  })
  return response.data as Record<string, unknown>
}

export async function ensureFeedingGroup(input: Omit<FeedingGroup, 'id' | 'active'>): Promise<FeedingGroup> {
  const groups = await fetchFeedingGroups()
  const existing = groups.find((group) =>
    (input.external_ref && group.external_ref === input.external_ref) || group.name === input.name,
  )
  if (existing) return existing
  return createFeedingGroup({ ...input, active: true })
}
