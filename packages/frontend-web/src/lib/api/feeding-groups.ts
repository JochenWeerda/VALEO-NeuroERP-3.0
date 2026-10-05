import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/lifecycle/groups'

export type GroupProfile = 'custom' | 'fresh_cow' | 'high_yield_cow' | 'mid_lactation_cow' | 'late_lactation_cow' | 'dry_far_off' | 'dry_close_up' | 'heifer' | 'calf' | 'beef_cattle'
export type PregnancyStatus = 'unknown' | 'open' | 'pregnant'
export type GroupRiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface FeedingGroupDetail {
  id: string
  name: string
  revision: number
  profile_code: GroupProfile
  pregnancy_status: PregnancyStatus
  gestation_day?: number | null
  animal_count: number
  risk_level: GroupRiskLevel
  valid_from: string
  valid_until?: string | null
}

export interface FeedingGroupUpdate {
  expected_revision: number
  reason: string
  name?: string
  profile_code?: GroupProfile
  pregnancy_status?: PregnancyStatus
  gestation_day?: number | null
  animal_count?: number
  risk_level?: GroupRiskLevel
  valid_from?: string
  valid_until?: string | null
}

export async function updateFeedingGroup(groupId: string, input: FeedingGroupUpdate): Promise<FeedingGroupDetail> {
  const response = await apiClient.patch<FeedingGroupDetail>(`${BASE}/${encodeURIComponent(groupId)}`, input)
  return response.data
}
