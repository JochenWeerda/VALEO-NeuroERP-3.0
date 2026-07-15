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

export interface CreateFeedingBusiness {
  name: string
  production_type?: string | null
  feeding_system?: string | null
}

export async function createFeedingBusiness(input: CreateFeedingBusiness): Promise<FeedingBusiness> {
  const response = await apiClient.post<FeedingBusiness>(`${BASE}/businesses`, input)
  return response.data
}
