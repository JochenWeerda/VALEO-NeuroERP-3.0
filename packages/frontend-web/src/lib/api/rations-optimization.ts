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
}

export interface OptimizationResult {
  status: 'optimal' | 'infeasible' | 'unbounded' | 'error'
  objective_value?: number
  total_cost_eur_day?: number
  total_cost_eur_100kg_milk?: number
  ration_items: RationItem[]
  nutrient_supply: NutrientSupply
  constraint_report: ConstraintReportItem[]
  dlg_indicators?: DlgIndicators
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

export async function promoteAsFeed(id: string): Promise<{ einzelfuttermittel_id: string; artikel_nummer: string }> {
  const { data } = await apiClient.post<{ einzelfuttermittel_id: string; artikel_nummer: string }>(
    `${GFA_BASE}/${id}/as-feed`
  )
  return data
}
