import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding/plans'

export interface FeedingPlanInstruction {
  id: string
  sequence: number
  feed_id: string
  feed_name?: string | null
  kg_fm_per_animal: number | null
  raw_batch_kg: number | null
  target_batch_kg: number | null
  rounding_delta_kg: number | null
}

export interface FeedingPlanVersion {
  id: string
  plan_id: string
  group_id: string
  group_name: string
  name: string
  version_no: number
  source_ration_version_id: string
  animal_count: number
  dosing_step_kg: number
  rounding_mode: 'nearest' | 'up' | 'down'
  valid_from: string
  valid_until?: string | null
  reason: string
  published_by: string
  published_at: string
  plan_status: 'scheduled' | 'current' | 'stale'
  is_stale: boolean
  instructions: FeedingPlanInstruction[]
}

export async function fetchFeedingPlan(versionId: string): Promise<FeedingPlanVersion> {
  const response = await apiClient.get<FeedingPlanVersion>(`${BASE}/${versionId}`)
  return response.data
}

export async function fetchCurrentFeedingPlans(): Promise<FeedingPlanVersion[]> {
  const response = await apiClient.get<FeedingPlanVersion[]>(`${BASE}/current`)
  return response.data
}
