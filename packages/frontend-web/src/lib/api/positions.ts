/**
 * Commodity Position Matrix API client.
 */

import { apiClient } from '@/lib/axios'

const BASE = '/api/v1/positions'

export type PeriodCell = {
  period_key: string
  qty_buy_open: number
  qty_sell_open: number
  qty_net: number
  severity: string
  qty_tolerance?: number | null
}

export type ArticleRow = {
  article_id: string
  article_name: string
  unit: string
  sum_buy_open: number
  sum_sell_open: number
  sum_net: number
  cells: PeriodCell[]
}

export type MatrixResponse = {
  period_keys: string[]
  rows: ArticleRow[]
  as_of_date: string
  period_mode: string
}

export type ContractOpenItem = {
  contract_id: string
  contract_no: string
  party_id: string
  position_no: number
  article_id: string
  qty_contract: number
  qty_delivered: number
  qty_rest: number
  unit: string
  unit_price?: number | null
  valid_to?: string | null
  clerk_id?: string | null
}

export type MovementItem = {
  movement_id: string
  contract_id: string
  order_no?: string | null
  delivery_note_no?: string | null
  invoice_no?: string | null
  movement_date?: string | null
  quantity: number
  unit_price?: number | null
  route_no?: string | null
}

export type TopCauser = {
  contract_id: string
  contract_no: string
  contract_type: string
  qty_rest: number
  share_pct?: number | null
}

export type DrilldownResponse = {
  article_id: string
  article_name: string
  period_key: string
  branch_id?: string | null
  qty_buy_open: number
  qty_sell_open: number
  qty_net: number
  severity: string
  buy_contracts: ContractOpenItem[]
  sell_contracts: ContractOpenItem[]
  movements: MovementItem[]
  top_causers: TopCauser[]
}

export type CoverageItem = {
  article_id: string
  article_name: string
  period_key: string
  qty_buy_open: number
  qty_sell_open: number
  qty_net: number
  qty_tolerance?: number | null
  severity: string
  responsible?: string | null
  override_status?: string | null
}

export type CoverageMonitorResponse = {
  items: CoverageItem[]
  total: number
}

export type KpiResponse = {
  short_cell_count: number
  max_short_qty: number
  max_short_article_id?: string | null
  max_short_period_key?: string | null
  expiring_coverage_count: number
}

export type PositionRule = {
  rule_id: string
  scope_type: string
  scope_id: string
  neg_tolerance_qty: number
  max_short_days: number
  yellow_threshold?: number | null
  red_threshold?: number | null
  approval_required: boolean
  approval_role?: string | null
  active_from?: string | null
  active_to?: string | null
  tenant_id: string
  created_at?: string | null
  updated_at?: string | null
}

export type PositionRuleIn = {
  scope_type: string
  scope_id: string
  neg_tolerance_qty: number
  max_short_days?: number
  yellow_threshold?: number | null
  red_threshold?: number | null
  approval_required?: boolean
  approval_role?: string | null
  active_from?: string | null
  active_to?: string | null
}

export type PositionOverride = {
  override_id: string
  branch_id?: string | null
  article_id: string
  period_key: string
  requested_by?: string | null
  requested_at?: string | null
  reason?: string | null
  status: string
  approved_by?: string | null
  approved_at?: string | null
  valid_until?: string | null
  comment?: string | null
  related_doc_type?: string | null
  related_doc_id?: string | null
  tenant_id: string
  created_at?: string | null
}

export type OverrideRequestIn = {
  branch_id?: string | null
  article_id: string
  period_key: string
  reason: string
  related_doc_type?: string | null
  related_doc_id?: string | null
}

export interface MatrixParams {
  branch_id?: string | null
  as_of_date?: string | null
  period_mode?: string
  period_from: string
  period_to: string
  article_ids?: string | null
  use_cache?: boolean
  view_mode?: 'physisch' | 'physisch_disponiert' | 'inkl_archiv'
}

function toSearchParams(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v) !== '') search.set(k, String(v))
  })
  const s = search.toString()
  return s ? `?${s}` : ''
}

export async function getMatrix(params: MatrixParams): Promise<MatrixResponse> {
  return apiClient.get<MatrixResponse>(
    `${BASE}/matrix${toSearchParams(params as unknown as Record<string, string | number | boolean | undefined | null>)}`
  )
}

export async function getCellDrilldown(
  articleId: string,
  periodKey: string,
  params?: { branch_id?: string | null; as_of_date?: string | null; period_mode?: string; view_mode?: string },
): Promise<DrilldownResponse> {
  const suffix = params ? toSearchParams(params as Record<string, string | null | undefined>) : ''
  return apiClient.get<DrilldownResponse>(`${BASE}/cell/${encodeURIComponent(articleId)}/${encodeURIComponent(periodKey)}${suffix}`)
}

export async function getCoverageMonitor(params: {
  branch_id?: string | null
  as_of_date?: string | null
  period_mode?: string
  period_from: string
  period_to: string
  severity_filter?: string | null
  without_override_only?: boolean
  view_mode?: string
  skip?: number
  limit?: number
}): Promise<CoverageMonitorResponse> {
  return apiClient.get<CoverageMonitorResponse>(`${BASE}/coverage-monitor${toSearchParams(params as Record<string, string | number | boolean | undefined | null>)}`)
}

export async function getKpi(params: {
  branch_id?: string | null
  as_of_date?: string | null
  period_mode?: string
  period_from: string
  period_to: string
  article_ids?: string | null
  view_mode?: string
}): Promise<KpiResponse> {
  return apiClient.get<KpiResponse>(`${BASE}/kpi${toSearchParams(params as Record<string, string | undefined | null>)}`)
}

export async function refreshSnapshot(params: {
  branch_id?: string | null
  as_of_date?: string | null
  period_mode?: string
  period_from: string
  period_to: string
  article_ids?: string | null
  view_mode?: string
}): Promise<{ ok: boolean; cells_written: number }> {
  return apiClient.post<{ ok: boolean; cells_written: number }>(`${BASE}/refresh${toSearchParams(params as Record<string, string | undefined | null>)}`)
}

export async function listRules(params?: { scope_type?: string; scope_id?: string }): Promise<PositionRule[]> {
  const suffix = params ? toSearchParams(params as Record<string, string>) : ''
  return apiClient.get<PositionRule[]>(`${BASE}/rules${suffix}`)
}

export async function getRule(ruleId: string): Promise<PositionRule> {
  return apiClient.get<PositionRule>(`${BASE}/rules/${encodeURIComponent(ruleId)}`)
}

export async function createRule(payload: PositionRuleIn): Promise<PositionRule> {
  return apiClient.post<PositionRule, PositionRuleIn>(`${BASE}/rules`, payload)
}

export async function updateRule(ruleId: string, payload: PositionRuleIn): Promise<PositionRule> {
  return apiClient.put<PositionRule, PositionRuleIn>(`${BASE}/rules/${encodeURIComponent(ruleId)}`, payload)
}

export async function deleteRule(ruleId: string): Promise<void> {
  return apiClient.delete(`${BASE}/rules/${encodeURIComponent(ruleId)}`)
}

export async function listOverrides(params?: {
  status_filter?: string
  article_id?: string
  period_key?: string
}): Promise<PositionOverride[]> {
  const suffix = params ? toSearchParams(params as Record<string, string>) : ''
  return apiClient.get<PositionOverride[]>(`${BASE}/overrides${suffix}`)
}

export async function getOverride(overrideId: string): Promise<PositionOverride> {
  return apiClient.get<PositionOverride>(`${BASE}/overrides/${encodeURIComponent(overrideId)}`)
}

export async function requestOverride(payload: OverrideRequestIn, requestedBy?: string): Promise<PositionOverride> {
  return apiClient.post<PositionOverride, OverrideRequestIn & { requested_by?: string }>(
    `${BASE}/overrides`,
    requestedBy ? { ...payload, requested_by: requestedBy } : payload,
  )
}

export async function approveOverride(
  overrideId: string,
  payload: { comment: string; valid_days?: number },
  approvedBy?: string,
): Promise<PositionOverride> {
  return apiClient.post<PositionOverride, { comment: string; valid_days?: number; approved_by?: string }>(
    `${BASE}/overrides/${encodeURIComponent(overrideId)}/approve`,
    approvedBy ? { ...payload, approved_by: approvedBy } : payload,
  )
}

export async function rejectOverride(overrideId: string, payload: { comment: string }, rejectedBy?: string): Promise<PositionOverride> {
  return apiClient.post<PositionOverride, { comment: string; rejected_by?: string }>(
    `${BASE}/overrides/${encodeURIComponent(overrideId)}/reject`,
    rejectedBy ? { ...payload, rejected_by: rejectedBy } : payload,
  )
}
