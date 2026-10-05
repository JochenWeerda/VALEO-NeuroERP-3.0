import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/reference-data'

export type MatterBasis = 'fresh_matter' | 'dry_matter'
export type BasisValueKind = 'quantity' | 'concentration'
export type RoundingMode = 'half_up' | 'half_even' | 'down' | 'up'

export interface NutrientDefinition {
  id: string
  tenant_id: string | null
  code: string
  display_name: string
  canonical_unit_code: string
  default_basis: MatterBasis
  value_kind: BasisValueKind
  minimum_value: string | null
  maximum_value: string | null
  sort_order: number
  revision: number
  source: string
  active: boolean
  updated_at: string
}

export interface FeedingUnitDefinition {
  id: string
  tenant_id: string | null
  code: string
  display_name: string
  dimension: string
  factor_to_base: string
  precision: number
  revision: number
  source: string
  active: boolean
  updated_at: string
}

export interface BasisConversionInput {
  value: string
  from_basis: MatterBasis
  to_basis: MatterBasis
  dry_matter_pct: string
  kind: BasisValueKind
  precision?: number
  rounding_mode?: RoundingMode
}

export interface BasisConversionResult extends BasisConversionInput {
  unrounded_value: string
  precision: number
  rounding_mode: RoundingMode
}

export async function fetchNutrientDefinitions(): Promise<NutrientDefinition[]> {
  return (await apiClient.get<NutrientDefinition[]>(`${BASE}/nutrients`)).data
}

export async function fetchFeedingUnitDefinitions(): Promise<FeedingUnitDefinition[]> {
  return (await apiClient.get<FeedingUnitDefinition[]>(`${BASE}/units`)).data
}

export async function convertFeedingMatterBasis(input: BasisConversionInput): Promise<BasisConversionResult> {
  return (await apiClient.post<BasisConversionResult>(`${BASE}/convert-basis`, input)).data
}
