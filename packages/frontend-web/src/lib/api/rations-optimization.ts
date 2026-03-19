/**
 * Rationsoptimierung API
 * Proxy zum Rationsoptimierungs-Microservice (GfE-2023, PuLP)
 */

import { apiClient } from '../api-client'

const BASE = '/api/v1/agrar/rations-optimization'

export interface CowProfile {
  breed: string
  body_weight_kg: number
  milk_kg_day?: number
  milk_fat_pct?: number
  milk_protein_pct?: number
  lactation_stage_days?: number
  parity?: number
  target_dmi_kg?: number
}

export interface FeedIngredient {
  id: string
  name: string
  group: string
  dm_frac: number
  price_eur_kgdm: number
  me_mj_kgdm: number
  sidp_g_kgdm: number
  andfom_g_kgdm: number
  starch_g_kgdm: number
  sugar_g_kgdm: number
  fat_g_kgdm: number
  ca_g_kgdm: number
  p_g_kgdm: number
  na_g_kgdm: number
  min_kgdm: number
  max_kgdm: number
  active: boolean
}

export interface RationItem {
  feed_id: string
  name: string
  kgdm: number
  kgfm: number
  unit_cost: number
  total_cost: number
}

export interface NutrientSupply {
  dmi_kg: number
  me_mj: number
  sidp_g: number
  andfom_g: number
  starch_g: number
  sugar_g: number
  fat_g: number
  ca_g: number
  p_g: number
  na_g: number
  forage_share_pct: number
}

export interface ConstraintReportItem {
  name: string
  target: number
  actual: number
  difference: number
  fulfilled: boolean
  status: string
}

export interface OptimizationResult {
  status: 'optimal' | 'infeasible' | 'unbounded' | 'error'
  objective_value?: number
  total_cost_eur_day?: number
  ration_items: RationItem[]
  nutrient_supply: NutrientSupply
  constraint_report: ConstraintReportItem[]
  warnings: string[]
  metadata?: Record<string, unknown>
}

export async function fetchRationsHealth(): Promise<{ success: boolean; configured?: boolean }> {
  const { data } = await apiClient.get<{ success: boolean; configured?: boolean }>(`${BASE}/health`)
  return data
}

export async function fetchFeeds(group?: string): Promise<FeedIngredient[]> {
  const params = group ? { group } : {}
  const { data } = await apiClient.get<FeedIngredient[]>(`${BASE}/feeds`, { params })
  return data
}

export async function optimizeFromProfile(
  cowProfile: CowProfile,
  feedIds?: string[]
): Promise<OptimizationResult> {
  const { data } = await apiClient.post<OptimizationResult>(`${BASE}/optimize/from-profile`, {
    cow_profile: cowProfile,
    feeds: feedIds,
  })
  return data
}

export async function optimizeDemo(): Promise<OptimizationResult> {
  const { data } = await apiClient.post<OptimizationResult>(`${BASE}/optimize/demo`)
  return data
}

export async function calculateRequirements(cowProfile: CowProfile): Promise<Record<string, number>> {
  const { data } = await apiClient.post<Record<string, number>>(`${BASE}/requirements/calculate`, cowProfile)
  return data
}

export async function validateFeeds(feeds: FeedIngredient[]): Promise<{ valid: boolean; errors: string[] }> {
  const { data } = await apiClient.post<{ valid: boolean; errors: string[] }>(`${BASE}/feeds/validate`, { feeds })
  return data
}
