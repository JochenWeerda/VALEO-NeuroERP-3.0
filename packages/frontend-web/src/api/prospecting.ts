import { apiClient } from '@/lib/api-client'
import type { LeadCandidate, LeadSegment, LeadSourceSystem } from '@/types/prospecting'

export interface LeadCandidateQuery {
  refYear: number
  minPotential?: number
  // region removed in favor of zipCode range
  zipCodeStart?: string
  zipCodeEnd?: string
  source?: LeadSourceSystem
  segment?: LeadSegment
  onlyNewProspects?: boolean
  onlyHighPriority?: boolean
  limit?: number
}

export async function fetchLeadCandidates(params: LeadCandidateQuery): Promise<LeadCandidate[]> {
  const searchParams = new URLSearchParams()
  searchParams.set('ref_year', String(params.refYear))

  if (params.minPotential !== undefined) {
    searchParams.set('min_potential', String(params.minPotential))
  }
  if (params.zipCodeStart) {
    searchParams.set('zip_code_start', params.zipCodeStart)
  }
  if (params.zipCodeEnd) {
    searchParams.set('zip_code_end', params.zipCodeEnd)
  }
  if (params.source) {
    searchParams.set('source', params.source)
  }
  if (params.segment) {
    searchParams.set('segment', params.segment)
  }
  if (params.onlyNewProspects !== undefined) {
    searchParams.set('only_new_prospects', params.onlyNewProspects ? 'true' : 'false')
  }
  if (params.onlyHighPriority !== undefined) {
    searchParams.set('only_high_priority', params.onlyHighPriority ? 'true' : 'false')
  }
  if (params.limit !== undefined) {
    searchParams.set('limit', String(params.limit))
  }

  const url = `/api/v1/prospecting/lead-candidates?${searchParams.toString()}`
  const response = await apiClient.get<LeadCandidate[]>(url)
  return response.data
}
