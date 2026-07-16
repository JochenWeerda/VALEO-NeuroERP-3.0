import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding'

export interface FeedingBusiness {
  id: string
  business_partner_id?: string | null
  name: string
  production_type?: string | null
  husbandry_form?: string | null
  feeding_system?: string | null
  milking_system?: string | null
  advisory_status: string
  active: boolean
  herd_count?: number
  group_count?: number
  updated_at: string
}

export interface FeedingBusinessOverview extends FeedingBusiness {
  ration_count: number
  template_count: number
  active_ration_count: number
  readiness_unknown_count: number
  readiness_blocked_count: number
  data_status: 'empty' | 'incomplete' | 'available'
}

export async function fetchFeedingBusinessOverview(id: string): Promise<FeedingBusinessOverview> {
  const response = await apiClient.get<FeedingBusinessOverview>(`${BASE}/businesses/${id}/overview`)
  return response.data
}

export interface CreateFeedingBusiness {
  name: string
  production_type?: string | null
  feeding_system?: string | null
}

export async function createFeedingBusiness(input: CreateFeedingBusiness): Promise<FeedingBusiness> {
  const response = await apiClient.post<FeedingBusiness>(`${BASE}/businesses`, input)
  return response.data
}

export async function fetchFeedingBusinesses(): Promise<FeedingBusiness[]> {
  const response = await apiClient.get<FeedingBusiness[]>(`${BASE}/businesses`)
  return response.data
}
