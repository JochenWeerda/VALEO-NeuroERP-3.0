export type LeadSourceSystem =
  | 'gap_de'
  | 'cap_eu'
  | 'bvk_bio'
  | 'qs'
  | 'qm_milk'
  | 'naturland'
  | 'other'

export type LeadSegment = 'A' | 'B' | 'C'

export type LeadPriority = 'high' | 'medium' | 'low'

export interface LeadCandidate {
  ref_year: number
  source_system: LeadSourceSystem

  prospect_name: string
  postal_code: string
  city: string

  estimated_area_ha: number | null
  estimated_potential_eur: number | null
  segment: LeadSegment | null
  region_cluster: string | null
  lead_priority: LeadPriority

  is_existing_customer: boolean
  matched_customer_id: string | null

  is_core_customer: boolean
  is_locked_by_sales: boolean

  has_bio: boolean
  has_qs: boolean
  has_qm_milk: boolean

  suggested_owner_id: string | null
}
