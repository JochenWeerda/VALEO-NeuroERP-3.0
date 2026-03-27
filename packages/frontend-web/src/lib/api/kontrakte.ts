import { apiClient } from '@/lib/axios'

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
