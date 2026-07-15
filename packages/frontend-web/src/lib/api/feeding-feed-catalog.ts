import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feed-catalog'
export type FeedKind = 'forage' | 'concentrate' | 'mineral' | 'additive' | 'byproduct' | 'liquid' | 'other'
export type FeedApprovalStatus = 'draft' | 'approved' | 'blocked' | 'retired'

export interface FeedingFeedDetail {
  id: string
  artikel_nummer: string
  name: string
  art: string
  feed_kind: FeedKind
  species_scope?: string | null
  conservation_method?: string | null
  approval_status: FeedApprovalStatus
  valid_from: string
  valid_until?: string | null
  revision: number
  trockensubstanz?: string | null
  protein?: string | null
  energie?: string | null
  preis_pro_t?: string | null
}

export interface FeedingFeedUpdate {
  expected_revision: number
  reason: string
  name?: string
  art?: string
  feed_kind?: FeedKind
  approval_status?: FeedApprovalStatus
  valid_until?: string | null
  trockensubstanz?: string | null
}

export async function updateFeedingFeed(feedId: string, input: FeedingFeedUpdate): Promise<FeedingFeedDetail> {
  return (await apiClient.patch<FeedingFeedDetail>(`${BASE}/feeds/${feedId}`, input)).data
}
