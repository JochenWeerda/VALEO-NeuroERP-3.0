import { apiClient } from '@/lib/api-client'

export type KontraktType = 'EINKAUF' | 'ZUKAUF' | 'VERKAUF'
export type KontraktStatus = 'OFFEN' | 'ERLEDIGT' | 'STORNIERT' | 'GELOESCHT'
export type MengenArt = 'GESAMTKONTRAKT' | 'EINZELMENGEN'

export type KontraktLine = {
  line_id?: string
  position_no: number
  article_id: string
  description1?: string | null
  description2?: string | null
  qty_contract: number
  qty_remaining?: number | null
  price_unit?: string | null
  unit_price?: number | null
  discount_pct?: number | null
  surcharge?: number | null
  rebate_type?: string | null
  is_bio?: boolean
  is_matif?: boolean
}

export type KontraktSteering = {
  contract_class?: string | null
  contract_group?: string | null
  contract_variant?: string | null
  disposition_flag?: string | null
  parity_code?: string | null
  parity_label?: string | null
  fallback_route?: string | null
  alternate_articles?: string[]
  print_template?: string | null
  print_channel?: string | null
  print_copy_count?: number | null
  last_printed_at?: string | null
  print_ready?: boolean
  washout_status?: string | null
  washout_quantity_t?: number | null
  washout_reason?: string | null
  writeoff_quantity_t?: number | null
  writeoff_reason?: string | null
  writeoff_candidate?: boolean
  hedge_strategy?: string | null
  hedge_market?: string | null
  hedge_status?: string | null
  hedge_target_pct?: number | null
  hedge_quantity_t?: number | null
  hedge_quote_pct?: number | null
  hedge_gap_pct?: number | null
  market_price_source?: string | null
  market_price_eur_t?: number | null
  market_price_date?: string | null
  market_price_delta_eur_t?: number | null
  market_valuation_eur?: number | null
  reference_price_eur_t?: number | null
  dunning_level?: number | null
  dunning_blocked?: boolean
  dunning_due_at?: string | null
  dunning_last_at?: string | null
  dunning_candidate?: boolean
  dunning_reason?: string | null
}

export type Kontrakt = {
  contract_id: string
  contract_no: string
  contract_type: KontraktType
  branch_id?: string | null
  clerk_id?: string | null
  party_id: string
  debitor_kto?: string | null
  kreditor_kto?: string | null
  contract_date?: string | null
  valid_from?: string | null
  valid_to?: string | null
  quantity_type: MengenArt
  total_quantity: number
  unit: string
  allow_overdelivery: boolean
  status: KontraktStatus
  notes?: string | null
  payment_terms?: string | null
  conditions_json?: Record<string, unknown>
  pricing_model?: string | null
  min_price?: number | null
  premium_type?: string | null
  premium_value?: number | null
  basis_reference?: string | null
  pricing_window_from?: string | null
  pricing_window_to?: string | null
  rest_quantity?: number
  steering?: KontraktSteering
  lines: KontraktLine[]
}

export type KontraktListItem = {
  contract_id: string
  contract_no: string
  contract_type: KontraktType
  party_id: string
  party_name?: string | null
  contract_date?: string | null
  valid_from?: string | null
  valid_to?: string | null
  total_quantity: number
  rest_quantity: number
  unit: string
  status: KontraktStatus
  pricing_model?: string | null
  allow_overdelivery: boolean
  first_article_id?: string | null
  first_article_desc?: string | null
  first_unit_price?: number | null
  steering?: KontraktSteering
}

export type KontraktListResponse = {
  items: KontraktListItem[]
  total: number
  skip: number
  limit: number
}

export type UmsaetzeResponse = {
  items: Array<{
    movement_id: string
    contract_id: string
    line_id?: string | null
    order_no?: string | null
    delivery_note_no?: string | null
    invoice_no?: string | null
    movement_date?: string | null
    quantity: number
    unit_price?: number | null
    route_no?: string | null
    is_invoiced: boolean
    is_archived: boolean
  }>
  verk_menge: number
}

export async function listKontrakte(params: Record<string, string | number | boolean | undefined>): Promise<KontraktListResponse> {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v) !== '') search.set(k, String(v))
  })
  const suffix = search.size ? `?${search.toString()}` : ''
  return apiClient.get<KontraktListResponse>(`/api/v1/kontrakte${suffix}`)
}

export async function getKontrakt(id: string): Promise<Kontrakt> {
  return apiClient.get<Kontrakt>(`/api/v1/kontrakte/${id}`)
}

export async function createKontrakt(payload: Omit<Kontrakt, 'contract_id' | 'rest_quantity'>): Promise<Kontrakt> {
  return apiClient.post<Kontrakt, Omit<Kontrakt, 'contract_id' | 'rest_quantity'>>('/api/v1/kontrakte', payload)
}

export async function updateKontrakt(id: string, payload: Omit<Kontrakt, 'contract_id' | 'rest_quantity'>): Promise<Kontrakt> {
  return apiClient.patch<Kontrakt, Omit<Kontrakt, 'contract_id' | 'rest_quantity'>>(`/api/v1/kontrakte/${id}`, payload)
}

export async function deleteKontrakt(id: string, force = false): Promise<{ ok: boolean }> {
  const suffix = force ? '?force=true' : ''
  return apiClient.delete<{ ok: boolean }>(`/api/v1/kontrakte/${id}${suffix}`)
}

export async function cancelKontrakt(id: string, reason?: string): Promise<Kontrakt> {
  return apiClient.post<Kontrakt, { reason?: string }>(`/api/v1/kontrakte/${id}/cancel`, { reason })
}

export async function listKontraktUmsaetze(
  id: string,
  params?: { include_archived?: boolean; only_invoiced?: boolean; article_id?: string },
): Promise<UmsaetzeResponse> {
  const search = new URLSearchParams()
  if (params?.include_archived) search.set('include_archived', 'true')
  if (params?.only_invoiced !== undefined) search.set('only_invoiced', String(params.only_invoiced))
  if (params?.article_id) search.set('article_id', params.article_id)
  const suffix = search.size ? `?${search.toString()}` : ''
  return apiClient.get<UmsaetzeResponse>(`/api/v1/kontrakte/${id}/movements${suffix}`)
}

export async function createKontraktUmsatz(
  id: string,
  payload: {
    line_id: string
    order_no?: string
    delivery_note_no?: string
    invoice_no?: string
    movement_date?: string
    quantity: number
    unit_price?: number
    route_no?: string
    is_invoiced?: boolean
    is_archived?: boolean
  },
): Promise<{
  movement_id: string
  contract_id: string
}> {
  return apiClient.post(`/api/v1/kontrakte/${id}/movements`, payload)
}

export async function listKontraktAudit(id: string): Promise<{
  items: Array<{
    audit_id: string
    field_name: string
    old_value?: string | null
    new_value?: string | null
    action: string
    changed_at: string
    changed_by?: string | null
  }>
}> {
  return apiClient.get(`/api/v1/kontrakte/${id}/audit`)
}

export async function lookupVerkaufKontrakte(payload: { query?: string; only_open?: boolean; limit?: number }): Promise<{
  items: Array<{
    contract_id: string
    line_id: string
    contract_no: string
    position_no: number
    date?: string | null
    name: string
    valid_from?: string | null
    valid_to?: string | null
    article_id: string
    bezeichnung: string
  }>
}> {
  return apiClient.post('/api/v1/kontrakte/lookup/verkauf', payload)
}
