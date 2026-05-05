/**
 * Rationsoptimierung API
 * Proxy zum Rationsoptimierungs-Microservice (GfE-2023, PuLP)
 */

import { apiClient } from '../api-client'

const BASE = '/api/v1/agrar/rations-optimization'

/**
 * Lesbare Fehlermeldung aus FastAPI/Axios (HTTP 400+): `detail` als String oder Validierungsliste.
 */
export function getRationsApiErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const ax = error as {
      response?: { status?: number; data?: { detail?: unknown; message?: string } }
      message?: string
    }
    const status = ax.response?.status
    if (status !== undefined && status > 0 && status < 400) {
      return fallback
    }
    const detail = ax.response?.data?.detail
    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }
    if (Array.isArray(detail)) {
      const parts = detail.map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg?: string }).msg ?? item)
        }
        return JSON.stringify(item)
      })
      const joined = parts.filter(Boolean).join('; ')
      if (joined) return joined
    }
    const msg = ax.response?.data?.message
    if (typeof msg === 'string' && msg.trim()) return msg
    if (ax.message) return ax.message
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}

export interface CowProfile {
  breed: string
  body_weight_kg: number
  milk_kg_day?: number
  milk_fat_pct?: number
  milk_protein_pct?: number
  lactation_stage_days?: number
  parity?: number
  target_dmi_kg?: number
  /** Schritt 3: harte TM-Grenzen für den Solver (kg/Tag), optional zur Standardbandberechnung */
  wizard_dmi_min_kg?: number
  wizard_dmi_max_kg?: number
  feeding_type?: 'TMR' | 'PMR' | 'PMR+Weide'
  season_profile?: SeasonProfile | null
}

export type FeedingMode = 'TMR' | 'PMR' | 'PMR+Weide'

/** Entspricht Backend `FeedingSystemConfig` (Slice 1h, snake_case im JSON). */
export type FeedingSystemKind = 'TMR' | 'PMR_stall' | 'PMR_pasture'

export type ConcentrateDistribution =
  | 'included_in_tmr'
  | 'transponder'
  | 'ams'
  | 'milkparlor'

export interface ConcentrateRecipeProfile {
  starch_breakdown_class?: 'slow' | 'mixed' | 'rapid'
  mill_byproduct_share?: number | null
  slow_starch_share?: number | null
  rumen_buffer_present?: boolean
  source?: 'declared' | 'scanned_ocr' | 'manual_estimate' | 'default'
}

export interface FeedingSystemConfig {
  system: FeedingSystemKind
  concentrate_distribution: ConcentrateDistribution
  concentrate_max_per_serving_kg?: number | null
  concentrate_max_per_day_kg?: number | null
  concentrate_servings_per_day?: number | null
  treat_as_primiparous?: boolean
  default_concentrate_recipe?: ConcentrateRecipeProfile | null
}

export interface FeedBlockAssignment {
  feed_id: string
  block: 'pasture' | 'tmr' | 'concentrate_staged'
  concentrate_recipe?: ConcentrateRecipeProfile | null
}

/** Ableitung aus Wizard-Fuetterungstyp (Backend-Defaults spiegeln). */
export function defaultFeedingSystemConfig(feedingType: FeedingMode): FeedingSystemConfig {
  if (feedingType === 'TMR') {
    return { system: 'TMR', concentrate_distribution: 'included_in_tmr' }
  }
  if (feedingType === 'PMR') {
    return { system: 'PMR_stall', concentrate_distribution: 'transponder' }
  }
  return { system: 'PMR_pasture', concentrate_distribution: 'milkparlor' }
}

// --- FAN-MODE-V1 (Spec §4/§6/§8, freigegeben 2026-04-21) ---

export type FanMode = 'auto_iterative' | 'reference' | 'evaluation_only'
export type RelaxationPolicy = 'strict' | 'standard' | 'soft'
export type ObjectiveStrategy = 'balance_then_cost' | 'balance_only' | 'cost_only'
export type PolicyProfile =
  | 'tmr_standard'
  | 'pmr_standard'
  | 'pmr_pasture_spring'
  | 'pmr_pasture_summer'
  | 'pmr_pasture_autumn'
  // DLG 01|2025 Tabelle 14: Leistungs-/Physiologiestufen
  | 'tmr_fresh_lactation'
  | 'tmr_high_yield'
  | 'tmr_mid_yield'
  | 'tmr_late_lactation'
  | 'tmr_dry_cow'
  | 'tmr_transit'
export type SeasonProfile =
  | 'spring_young'
  | 'spring_mid'
  | 'spring_late'
  | 'summer_young'
  | 'summer_mid'
  | 'summer_late'
  | 'autumn'
  | 'winter'

export interface FanOptions {
  mode?: FanMode
  reference?: number
  tolerance?: number
  tolerance_warn?: number
  max_iterations?: number
}

export const FAN_REFERENCE_PRESETS: readonly number[] = [2.5, 3.0, 3.5] as const
export const FAN_DEFAULTS = {
  mode: 'auto_iterative' as FanMode,
  tolerance: 0.05,
  tolerance_warn: 0.10,
  max_iterations: 5,
  relaxation_policy: 'standard' as RelaxationPolicy,
  objective_strategy: 'balance_then_cost' as ObjectiveStrategy,
} as const

export interface FanCalibrationPayload {
  mode: FanMode
  reference: number | null
  tolerance: number
  tolerance_warn: number
  max_iterations: number
  iterations: Array<{ i: number; fan_in: number; fan_out: number; delta: number }>
  iteration_count: number
  converged: boolean | null
  fani_final: number | null
  catalog_version?: string | null
  feeds_exact?: number
  feeds_mapped?: number
  feeds_fallback?: number
  fallback_warning?: string | null
}

export interface ConstraintStatusItem {
  name: string
  kind: 'hart' | 'weich'
  class: 'A' | 'B' | 'C' | null
  unit: string
  target: number
  actual: number
  difference?: number | null
  fulfilled: boolean
  deviation_norm: number
  penalty_cost: number
  status: 'ok' | 'violated' | 'hard_violated'
  source?: string
}

export interface PenaltySummary {
  total: number
  by_class: { A: number; B: number; C: number }
  soft_violations: number
  hard_violations: number
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
  fan_slope_source?: 'exact' | 'mapped' | 'fallback'
  // Slice 1f (2026-04-23): Block-Zuordnung je Fuetterungssystem.
  block?: 'tmr_block' | 'pasture_block' | 'concentrate_staged_block' | string
}

export interface NutrientSupply {
  dmi_kg: number
  me_mj: number
  sidp_g: number
  andfom_g: number
  starch_g: number
  staerke_g?: number
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

export interface DlgIndicators {
  strukturindex: number | null
  strukturindex_ziel: string
  strukturindex_erfuellt: boolean
  andfom_gf_kgdm: number
  andfom_gf_ziel: string
  pabkh_kgdm: number
  pabkh_ziel: string
  xl_kgdm: number
  xl_ziel: string
  rmd_gn_kgdm: number | null
  rmd_ziel: string
  forage_share_pct: number
  forage_share_ziel: string
  // GfE-Workshop 2023
  // DLG 01|2023: peNDF ist Kontroll-/Validierungsgroesse, nicht die primaere
  // Planungsgroesse. Primaer gesteuert wird ueber aNDFomGF (siehe Felder oben).
  pendf_kgdm?: number
  pendf_min_kgdm?: number
  pendf_ziel?: string
  pendf_erfuellt?: boolean
  pendf_role?: string
  pendf_model_calibrated?: boolean
  pendf_model_status?: string
  // Staerkeadaptive Aufschlusselung der aNDFomGF-Zieldichte.
  andfom_gf_base?: number
  andfom_gf_starch_uplift?: number
  ph_predicted?: number
  ph_ziel?: string
  ph_ok?: boolean
  // 2026-04-21: Flag, ob die Zebeli/Schwarz-Formel fuer die aktuelle Ration
  // anwendbar ist (peNDF 60-250 g/kg TM, Staerke 50-350 g/kg TM, DMI 10-25 kg/d).
  // Ausserhalb des Bereichs wird keine pH-Warnung ausgegeben.
  ph_formula_applicable?: boolean
  // DLG 01|2025 Kap. 8.3: Formelquelle (Zebeli 2008) und pansenabbaubare Staerke
  // (ST - bST) als korrekter Formel-Input.
  ph_formula_source?: string
  abbaust_kgdm?: number
  // DLG 01|2025 Kap. 8.2: aNDFomGF + strukturwirksame Co-Produkte,
  // binaere Kaskade (200 g/kg TM bei pabKH <= 210, 280 g/kg TM daruber).
  andfom_gf_cop_kgdm?: number
  andfom_gf_cop_target_kgdm?: number
  andfom_gf_cop_step?: '<=210' | '>210' | '>260_warn' | string
  andfom_gf_cop_ziel?: string
  // DLG 01|2025 Kap. 8.4: Fermentationsindex Kohlenhydrate (FIKH).
  // Ziel >= 50 %. Kann null sein, wenn keine NDFD-Werte verfuegbar sind.
  fikh_pct?: number | null
  fikh_ziel?: string
  fikh_erfuellt?: boolean
  fikh_diagnose?: string
  fikh_quelle?: string
}

// DLG 01|2025 Tabelle 14: Leistungs-/Physiologiestufen-Profile mit
// Referenzkorridoren (ME, CP, sidP, pabKH, XL, Grobfutter, aNDFomGF+CoP, aNDFom).
export interface PolicyProfileTargets {
  label?: string
  me_kgdm_min?: number
  me_kgdm_max?: number
  cp_kgdm_min?: number
  cp_kgdm_max?: number
  sidp_kgdm_min?: number
  sidp_kgdm_max?: number
  pabkh_max?: number
  xl_kgdm_min?: number
  xl_kgdm_max?: number
  forage_share_min_pct?: number
  forage_share_max_pct?: number
  andfom_gf_cop_min?: number
  ndf_kgdm_min?: number
}

// DLG 01|2025: Band-Auswertung (Post-Solve-Soft-Constraint).
// Jeder Eintrag vergleicht die Ist-Werte einer Ration gegen die
// Referenzkorridore des aktiven Profils. Penalty fliesst in Klasse B.
export interface PolicyProfileBand {
  name: string
  kind: 'weich' | 'hart'
  class: 'A' | 'B' | 'C'
  unit: string
  target: number
  target_min?: number | null
  target_max?: number | null
  direction: 'min' | 'max' | 'target'
  actual: number
  difference: number
  fulfilled: boolean
  deviation_norm: number
  penalty_cost: number
  status: 'ok' | 'violated'
  source: 'policy_profile'
}

export interface PolicyProfileEvaluation {
  profile: PolicyProfile
  label?: string | null
  bands: PolicyProfileBand[]
  violation_count: number
  violations: PolicyProfileBand[]
  penalty_total: number
  source: string
}

// Native LP-Slacks fuer DLG-01|2025-Policy-Baender (Stage-2-Cost + Policy-Slack):
// Gegenstueck zur Post-Solve-Band-Auswertung. Die Slack-Variablen sind direkt im
// LP-Solver gebunden; ihre Werte geben die vom Solver gewaehlte Korridor-
// Verletzung pro Band in absoluten Einheiten (g/d bzw. %TM*kg/d) zurueck.
export interface PolicyProfileLpSlack {
  name: string
  unit: string
  direction: 'min' | 'max'
  band_min?: number | null
  band_max?: number | null
  halfwidth: number
  weight: number
  slack_value: number
  penalty_cost: number
  active: boolean
}

// SARA-Safety-Reopt (Pansenazidose-Schutz, 2026-04-21):
// Wenn die erste Optimierung pH < 5.9 / peNDF < Minimum / pabKH am Limit liefert,
// wird automatisch mit verschaerften Constraints erneut geloest und der Benutzer
// ueber ein Badge informiert.
export interface SaraSafetyReoptPayload {
  triggered: boolean
  reason?: string | null
  actions?: string[]
  resolved?: boolean
  resolution_note?: string
  metrics_before?: {
    ph_predicted?: number
    ph_formula_applicable?: boolean
    pendf_kgdm?: number
    pendf_min_kgdm?: number
    pabkh_kgdm?: number
    pabkh_limit_kgdm?: number
    starch_kgdm?: number
    total_dmi_kg?: number
  }
  metrics_after?: {
    ph_predicted?: number
    ph_formula_applicable?: boolean
    pendf_kgdm?: number
    pendf_min_kgdm?: number
    pabkh_kgdm?: number
    pabkh_limit_kgdm?: number
    starch_kgdm?: number
    total_dmi_kg?: number
  }
}

export interface NutrientSupplyExtended {
  dmi_kg: number
  me_mj: number
  sidp_g: number
  andfom_g: number
  starch_g?: number
  staerke_g?: number
  sugar_g: number
  fat_g: number
  ca_g: number
  p_g: number
  na_g: number
  mg_g?: number
  k_g?: number
  forage_share_pct: number
  // GfE-Workshop 2023
  pendf_kgdm?: number
  pendf_min_kgdm?: number
  staerke_kgdm?: number
  ph_predicted?: number
  sidlys_g?: number
  sidmet_g?: number
  sidlys_sidmet_ratio?: number
}

export interface OptimizationDiagnosis {
  reason: string | null
  gaps: string[]
  suggestions: string[]
}

/**
 * Slice 1f (2026-04-23): Block-Aggregate je Fuetterungssystem.
 * Bei reinem TMR sind pasture_block / concentrate_staged_block leer (0-Werte).
 */
export interface RationBlockSummary {
  dmi_kg: number
  dmi_share_pct: number
  cost_eur_day: number
  me_mj: number
  sidp_g: number
  cp_g: number
  items: Array<{ feed_id: string; name: string; kgdm: number; kgfm: number }>
}

export interface RationBlocks {
  feeding_system: {
    system: 'TMR' | 'PMR_stall' | 'PMR_pasture' | string | null
    concentrate_distribution: 'transponder' | 'ams' | 'milkparlor' | 'included_in_tmr' | string | null
    concentrate_max_per_serving_kg: number | null
    concentrate_servings_per_day: number | null
    concentrate_max_per_day_kg: number | null
    treat_as_primiparous?: boolean
    default_concentrate_recipe?: Record<string, unknown> | null
    /** Backend: TMR -> PMR_pasture wenn Weide in der Loesung > 0 kg TM/d. */
    auto_promoted_from_tmr?: boolean
  }
  tmr_block: RationBlockSummary
  pasture_block: RationBlockSummary
  concentrate_staged_block: RationBlockSummary
}

/**
 * Slice 2 (2026-04-23): Konzentrat-Futterabruf-Staffel.
 * Linear/stueckweise linear oberhalb der Grobfutter-Basisleistung.
 * Nur fuer gestaffelte Verteilungssysteme (transponder/ams/milkparlor).
 */
export interface ConcentrateCallUpRow {
  milk_kg_day: number
  additional_milk_kg: number
  concentrate_kg_fm_day_low: number
  concentrate_kg_fm_day_high: number
  concentrate_kg_fm_day_mid: number
  concentrate_kg_tm_day_mid: number
  per_serving_kg_fm: number
  exceeds_per_serving_limit: boolean
  exceeds_recommended_daily_limit: boolean
  exceeds_hard_safety_limit: boolean
}

/**
 * Slice 3 (2026-04-23): Misch- und Fuetterungsprotokoll TMR-Block.
 * Nur gesetzt, wenn der Ration mindestens eine TMR-Komponente enthaelt.
 */
export interface MixingProtocolStep {
  step: number
  feed_id: string | null
  name: string
  group_idx: number
  group_label: string
  kgdm: number
  kgfm: number
  dm_frac: number
  share_fm_pct: number
}

export interface MixingProtocolExcludedPastureItem {
  feed_id: string
  name: string
  kgdm: number
  reason?: string
}

export interface MixingProtocol {
  basis: {
    feeding_system: string
    concentrate_distribution: string | null
    target_dm_frac: number
    actual_dm_frac_before_water: number
    overfill_pct: number
  }
  steps: MixingProtocolStep[]
  water_addition_kg_fm: number
  overfill_kg_fm: number
  totals: {
    tmr_kgdm: number
    tmr_kgfm_without_water: number
    tmr_kgfm_with_water: number
    tmr_kgfm_with_water_and_overfill: number
  }
  /** Weideanteile, die bewusst nicht im Mischwagen landen. */
  excluded_pasture?: {
    kgdm: number
    items: MixingProtocolExcludedPastureItem[]
  }
  warnings: string[]
}

export interface ConcentrateCallUp {
  basis: {
    feeding_system: string
    concentrate_distribution: string
    milk_from_forage_kg: number
    target_milk_kg: number
    concentrate_max_per_serving_kg_fm: number | null
    concentrate_servings_per_day: number | null
    concentrate_max_per_day_kg_fm: number | null
    hard_safety_daily_cap_kg_fm: number | null
    kg_conc_per_additional_milk_low: number
    kg_conc_per_additional_milk_high: number
    assumed_concentrate_dm_frac: number
  }
  rows: ConcentrateCallUpRow[]
  warnings: string[]
}

/** Maschinenlesbarer Patch fuer Re-Optimierung (UI „Vorschlag übernehmen“). */
export interface RationAdjustmentApplyPatch {
  relaxation_policy?: RelaxationPolicy
  policy_profile?: PolicyProfile | null
  add_feed_ids?: string[]
}

export interface RationAdjustmentSuggestion {
  id: string
  title: string
  detail: string
  apply_patch: RationAdjustmentApplyPatch
}

export interface OptimizationResult {
  status: 'optimal' | 'infeasible' | 'unbounded' | 'error'
  objective_value?: number
  total_cost_eur_day?: number
  total_cost_eur_100kg_milk?: number
  ration_items: RationItem[]
  nutrient_supply: NutrientSupply
  constraint_report: ConstraintReportItem[]
  constraint_status?: ConstraintStatusItem[]
  penalty_summary?: PenaltySummary
  dlg_indicators?: DlgIndicators
  warnings: string[]
  /** Vorschläge zur Rationsanpassung inkl. optional anwendbarem Patch. */
  ration_adjustment_suggestions?: RationAdjustmentSuggestion[]
  metadata?: Record<string, unknown>
  forage_performance?: {
    feeding_type: FeedingMode
    target_milk_kg: number
    forage_only: {
      forage_dmi_kg: number
      milk_from_energy_kg: number
      milk_from_protein_kg: number
      limiting_milk_kg: number
    }
    supplemented: {
      total_dmi_kg: number
      concentrate_dmi_kg: number
      forage_displacement_dmi_kg: number
      forage_displacement_factor: number
      milk_from_energy_kg: number
      milk_from_protein_kg: number
      limiting_milk_kg: number
    }
  }
  pasture_risk?: PastureRiskPayload | null
  sara_safety_reopt?: SaraSafetyReoptPayload
  fan_calibration?: FanCalibrationPayload
  active_policy_profile?: PolicyProfile
  // DLG 01|2025 Tabelle 14: Referenzkorridore fuer das aktive Profil.
  policy_profile_targets?: PolicyProfileTargets | null
  // DLG 01|2025: Post-Solve-Band-Auswertung (weiche Bindung).
  policy_profile_evaluation?: PolicyProfileEvaluation | null
  // DLG 01|2025: Native LP-Slack-Bindung (Stage-2-Cost + Policy-Slack).
  // Vorhanden nur wenn der erweiterte Solve mit Policy-Targets erfolgreich war.
  policy_profile_lp_slacks?: PolicyProfileLpSlack[] | null
  policy_profile_lp_total_penalty?: number | null
  policy_profile_lp_mode?:
    | 'stage2_cost_plus_policy_slack'
    | 'stage2_cost_plus_concentrate_slack'
    | null
  concentrate_max_lp_slack_kg?: number | null
  concentrate_max_lp_slack_penalty?: number | null
  policy_overrides?: Record<string, unknown>
  relaxation_policy?: RelaxationPolicy
  objective_strategy?: ObjectiveStrategy
  season_profile?: SeasonProfile | null
  diagnosis?: OptimizationDiagnosis | null
  // Slice 1f: Block-Aggregate je Fuetterungssystem.
  ration_blocks?: RationBlocks | null
  // Slice 2: Konzentrat-Futterabruf-Staffel (linear, stueckweise).
  concentrate_call_up?: ConcentrateCallUp | null
  // Slice 3: Mischprotokoll fuer den TMR-Block (nur bei Mischwagen).
  mixing_protocol?: MixingProtocol | null
}

export interface MilkFromSupply {
  milk_from_energy_kg: number
  milk_from_protein_kg: number
  limiting_milk_kg: number
}

export interface PastureRiskPayload {
  active: boolean
  feeding_type: FeedingMode
  pasture_dmi_kg: number
  grass_silage_dmi_kg: number
  pasture_cp_g_kgdm: number | null
  pasture_k_mg_ratio: number | null
  pasture_k_mg_ratio_ziel: string
  mg_supplement_dmi_kg: number
  mg_supplement_ziel: string
  milk_from_pasture: MilkFromSupply | null
  milk_from_grass_silage: MilkFromSupply | null
  milk_from_pasture_plus_grass_silage: MilkFromSupply | null
  warnings: string[]
}

export interface CompoundFeedComponent {
  name: string
  inclusion_pct: number
  matched_feed_id?: string | null
  matched_feed_name?: string | null
}

export interface CompoundFeedDeclaredAnalysis {
  crude_protein_pct?: number | null
  crude_fat_pct?: number | null
  crude_fiber_pct?: number | null
  crude_ash_pct?: number | null
  calcium_pct?: number | null
  phosphorus_pct?: number | null
  sodium_pct?: number | null
  magnesium_pct?: number | null
  nel_mj_kg?: number | null
}

export interface CompoundFeedGfeEstimate {
  basis: string
  match_coverage_pct: number
  me_fan1_mj_kgdm?: number | null
  me_fani_mj_kgdm?: number | null
  nel_mj_kgdm?: number | null
  sidp_g_kgdm?: number | null
  nxp_g_kgdm?: number | null
  cp_g_kgdm?: number | null
  andfom_g_kgdm?: number | null
  starch_g_kgdm?: number | null
  sugar_g_kgdm?: number | null
  fat_g_kgdm?: number | null
  omd_method?: string | null
}

export interface UploadedCompoundFeed {
  source_filename: string
  source_type: string
  product_name: string
  supplier_name?: string | null
  declared_analysis: CompoundFeedDeclaredAnalysis
  composition: CompoundFeedComponent[]
  gfe2023_estimate: CompoundFeedGfeEstimate
  optimizer_feed: Record<string, unknown>
  warnings: string[]
  raw_text_preview: string
}

export interface CompoundFeedUploadResult {
  parsed: UploadedCompoundFeed
  warnings: string[]
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

export interface OptimizeFromProfileExtras {
  fan_options?: FanOptions
  relaxation_policy?: RelaxationPolicy
  objective_strategy?: ObjectiveStrategy
  season_profile?: SeasonProfile
  policy_profile?: PolicyProfile
  policy_overrides?: Record<string, unknown>
  /** Slice 1h: explizites Fuetterungssystem (snake_case wie FastAPI-Body). */
  feeding_system_config?: FeedingSystemConfig
  feed_block_overrides?: FeedBlockAssignment[]
}

export async function optimizeFromProfile(
  cowProfile: CowProfile,
  feedIds?: string[],
  customFeeds?: object[],
  priceOverrides?: Record<string, number>,
  maxTmOverrides?: Record<string, number>,
  minTmOverrides?: Record<string, number>,
  extras?: OptimizeFromProfileExtras,
): Promise<OptimizationResult> {
  const { data } = await apiClient.post<OptimizationResult>(`${BASE}/optimize/from-profile`, {
    cow_profile: cowProfile,
    feeds: feedIds,
    custom_feeds: customFeeds,
    price_overrides: priceOverrides,
    max_tm_overrides: maxTmOverrides,
    min_tm_overrides: minTmOverrides,
    ...(extras ?? {}),
  })
  return data
}

export async function optimizeDemo(): Promise<OptimizationResult> {
  const { data } = await apiClient.post<OptimizationResult>(`${BASE}/optimize/demo`)
  return data
}

export async function uploadCompoundFeedDocument(file: File): Promise<CompoundFeedUploadResult> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<CompoundFeedUploadResult>(
    `${BASE}/compound-feed/upload`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
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

// ---------------------------------------------------------------------------
// DLG Datenbank-Status
// ---------------------------------------------------------------------------

export interface DlgDbInfo {
  feed_count: number
  source: string
  is_fallback: boolean
  last_update: string | null
  days_since_update: number | null
  needs_update: boolean
  update_interval_days: number
  dlg_info_url: string
  hint: string
}

export async function fetchDlgInfo(): Promise<DlgDbInfo> {
  const { data } = await apiClient.get<DlgDbInfo>(`${BASE}/dlg/info`)
  return data
}

export async function triggerDlgRefresh(): Promise<{ refreshed: boolean; feed_count: number; message: string }> {
  const { data } = await apiClient.post<{ refreshed: boolean; feed_count: number; message: string }>(
    `${BASE}/dlg/refresh`
  )
  return data
}

// ---------------------------------------------------------------------------
// Betriebseigene Grundfuttermittel (aus GrundfutterAnalysen)
// ---------------------------------------------------------------------------

export interface CustomFeedFromGfa {
  id: string
  name: string
  group: string
  forage: boolean
  dm_pct: number
  price_eur_kgdm: number
  me_mj_kgdm: number
  sidp_g_kgdm: number
  cp_g_kgdm: number
  andfom_g_kgdm: number
  xl_g_kgdm: number
  rmd_gn_kgdm: number | null
  ca_g_kgdm: number
  p_g_kgdm: number
  _optimizer_feed: object
}

export async function feedsFromGrundfutterAnalysen(
  analysen: GrundfutterAnalyse[]
): Promise<CustomFeedFromGfa[]> {
  const { data } = await apiClient.post<CustomFeedFromGfa[]>(`${BASE}/feeds/from-grundfutter`, analysen)
  return data
}

/**
 * Konvertiert eine GrundfutterAnalyse lokal (ohne API-Roundtrip) in ein FeedIngredient-Objekt
 * das in der Futtermitteltabelle angezeigt werden kann.
 */
export function gfaToDisplayFeed(gfa: GrundfutterAnalyse): FeedIngredient & { _isCustom: true; _analyseId: string } {
  const dm = (gfa.trockensubstanz_os ?? 86) / 100
  return {
    id: `gfa_${gfa.id}`,
    name: gfa.bezeichnung,
    group: 'Grundfutter/Betrieb',
    dm_frac: dm,
    price_eur_kgdm: 0.065,
    me_mj_kgdm: gfa.me_gfe2023_ts ?? gfa.me_rind_gfe2008_ts ?? 9.5,
    sidp_g_kgdm: gfa.sidp_ts ?? (gfa.nxp_ts ? gfa.nxp_ts * 0.95 : 0),
    andfom_g_kgdm: (gfa.andfom_ts ?? 0) * 10,
    starch_g_kgdm: 0,
    sugar_g_kgdm: (gfa.gesamtzucker_ts ?? 0) * 10,
    fat_g_kgdm: (gfa.rohfett_ts ?? 0) * 10,
    ca_g_kgdm: (gfa.calcium_ts ?? 0) * 10,
    p_g_kgdm: (gfa.phosphor_ts ?? 0) * 10,
    na_g_kgdm: (gfa.natrium_ts ?? 0) * 10,
    min_kgdm: 0,
    max_kgdm: 12,
    active: true,
    _isCustom: true,
    _analyseId: gfa.id,
  }
}

// ---------------------------------------------------------------------------
// Grundfutter-Analysen
// ---------------------------------------------------------------------------

const GFA_BASE = '/api/v1/agrar/grundfutter-analysen'

export interface GrundfutterAnalyse {
  id: string
  tenant_id: string
  bezeichnung: string
  probenart: string | null
  labor: string | null
  probe_nr: string | null
  auftragsnummer: string | null
  erntetermin: string | null
  analyse_datum: string | null
  probenahme_ort: string | null
  schnitt: number | null
  quelle_datei: string | null
  // Sensorik
  aussehen: string | null
  geruch: string | null
  ph_wert: number | null
  // Grundnährstoffe (% TS)
  trockensubstanz_os: number | null
  rohprotein_ts: number | null
  rohfaser_ts: number | null
  rohfett_ts: number | null
  rohasche_ts: number | null
  gesamtzucker_ts: number | null
  nfc_ts: number | null
  // Faser
  adfom_ts: number | null
  andfom_ts: number | null
  adl_ts: number | null
  hemicellulose_ts: number | null
  // Gasbildung / OMD
  gasbildung_ts: number | null
  omd_ts: number | null
  // Energie
  me_rind_gfe2008_ts: number | null
  nel_ts: number | null
  me_gfe2023_ts: number | null
  bruttoenergie_ts: number | null
  strukturwert_ts: number | null
  // Protein
  nxp_ts: number | null
  rnb_ts: number | null
  sidp_ts: number | null
  rmd_ts: number | null
  // Mineralstoffe
  calcium_ts: number | null
  phosphor_ts: number | null
  natrium_ts: number | null
  magnesium_ts: number | null
  kalium_ts: number | null
  // Verwaltung
  verifiziert: boolean
  notizen: string | null
  created_at: string
}

export interface GrundfutterAnalyseIn {
  bezeichnung: string
  probenart?: string
  labor?: string
  probe_nr?: string
  erntetermin?: string
  probenahme_ort?: string
  schnitt?: number
  ph_wert?: number
  trockensubstanz_os?: number
  rohprotein_ts?: number
  rohfaser_ts?: number
  rohfett_ts?: number
  rohasche_ts?: number
  gesamtzucker_ts?: number
  nfc_ts?: number
  adfom_ts?: number
  andfom_ts?: number
  adl_ts?: number
  hemicellulose_ts?: number
  gasbildung_ts?: number
  omd_ts?: number
  me_rind_gfe2008_ts?: number
  nel_ts?: number
  me_gfe2023_ts?: number
  bruttoenergie_ts?: number
  strukturwert_ts?: number
  nxp_ts?: number
  rnb_ts?: number
  sidp_ts?: number
  rmd_ts?: number
  calcium_ts?: number
  phosphor_ts?: number
  natrium_ts?: number
  magnesium_ts?: number
  kalium_ts?: number
  notizen?: string
}

export interface PdfUploadResult {
  saved: boolean
  confidence: 'high' | 'medium' | 'low'
  warnings: string[]
  parsed?: GrundfutterAnalyseIn
  analyse_id?: string
  data?: GrundfutterAnalyse
  raw_text_preview?: string
}

export async function fetchGrundfutterAnalysen(params?: {
  probenart?: string
  verifiziert?: boolean
  limit?: number
  offset?: number
}): Promise<{ total: number; items: GrundfutterAnalyse[] }> {
  const { data } = await apiClient.get<{ total: number; items: GrundfutterAnalyse[] }>(GFA_BASE, { params })
  return data
}

export async function createGrundfutterAnalyse(payload: GrundfutterAnalyseIn): Promise<GrundfutterAnalyse> {
  const { data } = await apiClient.post<GrundfutterAnalyse>(GFA_BASE, payload)
  return data
}

export async function patchGrundfutterAnalyse(
  id: string,
  payload: Partial<GrundfutterAnalyseIn> & { verifiziert?: boolean }
): Promise<GrundfutterAnalyse> {
  const { data } = await apiClient.patch<GrundfutterAnalyse>(`${GFA_BASE}/${id}`, payload)
  return data
}

export async function deleteGrundfutterAnalyse(id: string): Promise<void> {
  await apiClient.delete(`${GFA_BASE}/${id}`)
}

export async function uploadGrundfutterPdf(
  file: File,
  save = false
): Promise<PdfUploadResult> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<PdfUploadResult>(
    `${GFA_BASE}/upload-pdf?save=${save}`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data
}

export async function uploadGrundfutterCsv(
  file: File,
  save = false
): Promise<PdfUploadResult> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<PdfUploadResult>(
    `${GFA_BASE}/upload-csv?save=${save}`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data
}

export async function promoteAsFeed(id: string): Promise<{ einzelfuttermittel_id: string; artikel_nummer: string; name?: string }> {
  const { data } = await apiClient.post<{ einzelfuttermittel_id: string; artikel_nummer: string; name?: string }>(
    `${GFA_BASE}/${id}/as-feed`
  )
  return data
}
