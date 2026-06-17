import { apiClient } from '@/lib/api-client'

// ── Preislisten ───────────────────────────────────────────────────────────────

export type PreislistenItem = {
  id?: string
  price_list_id?: string
  article_id: string
  article_number?: string | null
  unit_price: number
  min_quantity?: number
  max_quantity?: number | null
  discount_percent?: number
  valid_from?: string | null
  valid_until?: string | null
}

export type Preisliste = {
  id: string
  tenant_id: string
  name: string
  description?: string | null
  currency: string
  price_list_type: string
  valid_from?: string | null
  valid_until?: string | null
  is_active: boolean
  item_count: number
  items: PreislistenItem[]
  created_at?: string | null
  updated_at?: string | null
}

export type PreislisteCreate = Omit<Preisliste, 'id' | 'tenant_id' | 'item_count' | 'created_at' | 'updated_at'>

export async function listPreislisten(tenantId?: string): Promise<Preisliste[]> {
  const qs = tenantId ? `?tenant_id=${tenantId}` : ''
  return (await apiClient.get<Preisliste[]>(`/api/v1/price-lists/${qs}`)).data
}

export async function getPreisliste(id: string): Promise<Preisliste> {
  return (await apiClient.get<Preisliste>(`/api/v1/price-lists/${id}`)).data
}

export async function createPreisliste(payload: PreislisteCreate, tenantId?: string): Promise<Preisliste> {
  const qs = tenantId ? `?tenant_id=${tenantId}` : ''
  return (await apiClient.post<Preisliste>(`/api/v1/price-lists/${qs}`, payload)).data
}

export async function updatePreisliste(id: string, payload: Partial<PreislisteCreate>): Promise<Preisliste> {
  return (await apiClient.put<Preisliste>(`/api/v1/price-lists/${id}`, payload)).data
}

export async function deletePreisliste(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/price-lists/${id}`)
}

// ── Preisfindung ──────────────────────────────────────────────────────────────

export type PreisfindungResult = {
  list_price: number
  discount: number
  net_price: number
  source: 'base' | 'price_list' | 'contract' | 'customer_discount' | 'employee_discount'
  price_list_id?: string | null
  contract_id?: string | null
}

export async function calculatePrice(params: {
  article_id: string
  customer_id?: string
  quantity?: number
  contract_id?: string
  user_role?: string
  tenant_id?: string
}): Promise<PreisfindungResult> {
  const p = new URLSearchParams()
  p.set('article_id', params.article_id)
  if (params.customer_id) p.set('customer_id', params.customer_id)
  if (params.quantity != null) p.set('quantity', String(params.quantity))
  if (params.contract_id) p.set('contract_id', params.contract_id)
  if (params.user_role) p.set('user_role', params.user_role)
  if (params.tenant_id) p.set('tenant_id', params.tenant_id)
  return (await apiClient.get<PreisfindungResult>(`/api/v1/pricing/calculate?${p.toString()}`)).data
}

// ── Rabattgruppen / Rabattklassen / Rabattsätze ───────────────────────────────

export type Rabattgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: 'EK' | 'VK'
  aktiv: boolean
  created_at: string
}

export type Rabattklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: 'EK' | 'VK'
  aktiv: boolean
  created_at: string
}

export type Rabattsatz = {
  id: string
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: 'EK' | 'VK'
  rabatt_prozent: number
  ab_menge?: number | null
  gueltig_ab?: string | null
  gueltig_bis?: string | null
  created_at: string
}

export async function listRabattgruppen(richtung?: string): Promise<Rabattgruppe[]> {
  const qs = richtung ? `?richtung=${richtung}` : ''
  return (await apiClient.get<Rabattgruppe[]>(`/api/v1/preise/rabatte/gruppen${qs}`)).data
}

export async function createRabattgruppe(payload: { gruppe_nr: string; bezeichnung: string; richtung: string }): Promise<Rabattgruppe> {
  return (await apiClient.post<Rabattgruppe>('/api/v1/preise/rabatte/gruppen', payload)).data
}

export async function deleteRabattgruppe(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/preise/rabatte/gruppen/${id}`)
}

export async function listRabattklassen(richtung?: string): Promise<Rabattklasse[]> {
  const qs = richtung ? `?richtung=${richtung}` : ''
  return (await apiClient.get<Rabattklasse[]>(`/api/v1/preise/rabatte/klassen${qs}`)).data
}

export async function createRabattklasse(payload: { klasse_nr: string; bezeichnung: string; richtung: string }): Promise<Rabattklasse> {
  return (await apiClient.post<Rabattklasse>('/api/v1/preise/rabatte/klassen', payload)).data
}

export async function deleteRabattklasse(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/preise/rabatte/klassen/${id}`)
}

export async function listRabattsaetze(params?: { richtung?: string; gruppe_nr?: string; klasse_nr?: string }): Promise<Rabattsatz[]> {
  const p = new URLSearchParams()
  if (params?.richtung) p.set('richtung', params.richtung)
  if (params?.gruppe_nr) p.set('gruppe_nr', params.gruppe_nr)
  if (params?.klasse_nr) p.set('klasse_nr', params.klasse_nr)
  const qs = p.toString() ? `?${p.toString()}` : ''
  return (await apiClient.get<Rabattsatz[]>(`/api/v1/preise/rabatte/saetze${qs}`)).data
}

export async function createRabattsatz(payload: {
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: string
  rabatt_prozent: number
  ab_menge?: number
  gueltig_ab?: string
  gueltig_bis?: string
}): Promise<Rabattsatz> {
  return (await apiClient.post<Rabattsatz>('/api/v1/preise/rabatte/saetze', payload)).data
}

export async function deleteRabattsatz(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/preise/rabatte/saetze/${id}`)
}

// ── Individualpreise ──────────────────────────────────────────────────────────

export type Individualpreis = {
  id: string
  preis_typ: 'VK' | 'EK'
  artikel_nr: string
  partner_nr?: string | null
  gueltig_von: string
  gueltig_bis?: string | null
  preis_eur: number
  mengeneinheit?: string | null
  staffel_menge: number
  waehrung: string
  notiz?: string | null
  created_at: string
}

export type IndividualpreisLookup = {
  artikel_nr: string
  partner_nr?: string | null
  preis_typ: string
  preis_eur: number
  mengeneinheit?: string | null
  gueltig_von: string
  gueltig_bis?: string | null
  staffel_menge: number
  quelle: string
}

export async function listIndividualpreise(params?: { preis_typ?: string; artikel_nr?: string; partner_nr?: string }): Promise<Individualpreis[]> {
  const p = new URLSearchParams()
  if (params?.preis_typ) p.set('preis_typ', params.preis_typ)
  if (params?.artikel_nr) p.set('artikel_nr', params.artikel_nr)
  if (params?.partner_nr) p.set('partner_nr', params.partner_nr)
  const qs = p.toString() ? `?${p.toString()}` : ''
  return (await apiClient.get<Individualpreis[]>(`/api/v1/preise/individualpreise${qs}`)).data
}

export async function createIndividualpreis(payload: Omit<Individualpreis, 'id' | 'created_at'>): Promise<Individualpreis> {
  return (await apiClient.post<Individualpreis>('/api/v1/preise/individualpreise', payload)).data
}

export async function deleteIndividualpreis(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/preise/individualpreise/${id}`)
}

export async function lookupIndividualpreis(params: {
  artikel_nr: string
  preis_typ?: string
  partner_nr?: string
  menge?: number
  datum?: string
}): Promise<IndividualpreisLookup | null> {
  const p = new URLSearchParams()
  p.set('artikel_nr', params.artikel_nr)
  if (params.preis_typ) p.set('preis_typ', params.preis_typ)
  if (params.partner_nr) p.set('partner_nr', params.partner_nr)
  if (params.menge != null) p.set('menge', String(params.menge))
  if (params.datum) p.set('datum', params.datum)
  const r = await apiClient.get<IndividualpreisLookup | null>(`/api/v1/preise/individualpreise/lookup?${p.toString()}`)
  return r.data
}
