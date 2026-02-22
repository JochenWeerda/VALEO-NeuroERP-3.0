import { apiClient } from '@/lib/api-client'

export type DeliveryOption =
  | 'vollstaendige_ablieferung'
  | 'hoflagerung'
  | 'berichtigung'
  | 'nachmeldung'

export type NawaroPrintNotificationPayload = {
  document_name: string
  harvest_year: number
  article_number?: string | null
  debtor_from?: string | null
  debtor_to?: string | null
  delivery_option: DeliveryOption
  form_code: string
  copies: number
  printer_name?: string | null
}

export type NawaroPrintNotification = NawaroPrintNotificationPayload & {
  id: string
  created_at?: string | null
  updated_at?: string | null
}

export type NawaroContractRowPayload = {
  contract_number?: string | null
  customer_name?: string | null
  name_1?: string | null
  total_area?: string | null
  standard_quantity?: string | null
  delivery_count?: number | null
  delivery_resource?: string | null
  quantity_b?: string | null
  harvest_declaration?: string | null
}

export type NawaroContractSheetPayload = {
  harvest_year: number
  article_number?: string | null
  is_summer: boolean
  is_winter: boolean
  rows: NawaroContractRowPayload[]
}

export type NawaroContractRow = NawaroContractRowPayload & {
  id: string
}

export type NawaroContractSheet = Omit<NawaroContractSheetPayload, 'rows'> & {
  id: string
  rows: NawaroContractRow[]
  created_at?: string | null
  updated_at?: string | null
}

export type NawaroAreaRowPayload = {
  customer_name?: string | null
  name_1?: string | null
  name_2?: string | null
  postal_code?: string | null
  city?: string | null
  phone?: string | null
  fax?: string | null
  area_2022?: string | null
  area_2023?: string | null
  area_2024?: string | null
  area_2025?: string | null
  area_2026?: string | null
}

export type NawaroAreaSheetPayload = {
  harvest_year_from: number
  harvest_year_to: number
  article_number?: string | null
  is_summer: boolean
  is_winter: boolean
  form_code: string
  rows: NawaroAreaRowPayload[]
}

export type NawaroAreaRow = NawaroAreaRowPayload & {
  id: string
}

export type NawaroAreaSheet = Omit<NawaroAreaSheetPayload, 'rows'> & {
  id: string
  rows: NawaroAreaRow[]
  created_at?: string | null
  updated_at?: string | null
}

export async function listPrintNotifications(): Promise<NawaroPrintNotification[]> {
  return (await apiClient.get<NawaroPrintNotification[]>('/api/v1/agrar/nawaro/print-notifications')).data
}

export async function createPrintNotification(payload: NawaroPrintNotificationPayload): Promise<NawaroPrintNotification> {
  return (await apiClient.post<NawaroPrintNotification>('/api/v1/agrar/nawaro/print-notifications', payload)).data
}

export async function updatePrintNotification(id: string, payload: NawaroPrintNotificationPayload): Promise<NawaroPrintNotification> {
  return (await apiClient.put<NawaroPrintNotification>(`/api/v1/agrar/nawaro/print-notifications/${id}`, payload)).data
}

export async function deletePrintNotification(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/agrar/nawaro/print-notifications/${id}`)
}

export async function listContractSheets(): Promise<NawaroContractSheet[]> {
  return (await apiClient.get<NawaroContractSheet[]>('/api/v1/agrar/nawaro/contract-sheets')).data
}

export async function createContractSheet(payload: NawaroContractSheetPayload): Promise<NawaroContractSheet> {
  return (await apiClient.post<NawaroContractSheet>('/api/v1/agrar/nawaro/contract-sheets', payload)).data
}

export async function updateContractSheet(id: string, payload: NawaroContractSheetPayload): Promise<NawaroContractSheet> {
  return (await apiClient.put<NawaroContractSheet>(`/api/v1/agrar/nawaro/contract-sheets/${id}`, payload)).data
}

export async function deleteContractSheet(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/agrar/nawaro/contract-sheets/${id}`)
}

export async function listAreaSheets(): Promise<NawaroAreaSheet[]> {
  return (await apiClient.get<NawaroAreaSheet[]>('/api/v1/agrar/nawaro/area-sheets')).data
}

export async function createAreaSheet(payload: NawaroAreaSheetPayload): Promise<NawaroAreaSheet> {
  return (await apiClient.post<NawaroAreaSheet>('/api/v1/agrar/nawaro/area-sheets', payload)).data
}

export async function updateAreaSheet(id: string, payload: NawaroAreaSheetPayload): Promise<NawaroAreaSheet> {
  return (await apiClient.put<NawaroAreaSheet>(`/api/v1/agrar/nawaro/area-sheets/${id}`, payload)).data
}

export async function deleteAreaSheet(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/agrar/nawaro/area-sheets/${id}`)
}

export type NawaroRapsCertificate = {
  id?: string
  scheme: string
  certificate_number: string
  chain_stage?: string | null
  valid_from?: string | null
  valid_until?: string | null
  issuer?: string | null
  status: string
}

export type NawaroRapsBalance = {
  id?: string
  booking_period?: string | null
  input_seed_tons: string
  output_oil_tons: string
  output_meal_tons: string
  output_other_tons: string
  allocation_oil_pct?: string | null
  allocation_meal_pct?: string | null
  heap_location?: string | null
  logistics_note?: string | null
}

export type NawaroRapsProfilePayload = {
  article_id?: string | null
  article_number?: string | null
  article_name: string
  harvest_year: number
  usage_food_pct: string
  usage_feed_pct: string
  usage_energy_pct: string
  usage_material_pct: string
  thg_gco2eq_mj?: string | null
  yield_dt_per_ha?: string | null
  notes?: string | null
  certificates: NawaroRapsCertificate[]
  balances: NawaroRapsBalance[]
}

export type NawaroRapsProfile = NawaroRapsProfilePayload & {
  id: string
  created_at?: string | null
  updated_at?: string | null
}

export type NawaroRapsDeriveResult = {
  profile: NawaroRapsProfile
  period: string
  source_tickets_kg: string
  source_settlements_kg: string
  source_input_tons: string
  plausibility_messages: string[]
}

export async function listRapsProfiles(): Promise<NawaroRapsProfile[]> {
  return (await apiClient.get<NawaroRapsProfile[]>('/api/v1/agrar/nawaro/raps-profiles')).data
}

export async function createRapsProfile(payload: NawaroRapsProfilePayload): Promise<NawaroRapsProfile> {
  return (await apiClient.post<NawaroRapsProfile>('/api/v1/agrar/nawaro/raps-profiles', payload)).data
}

export async function updateRapsProfile(id: string, payload: NawaroRapsProfilePayload): Promise<NawaroRapsProfile> {
  return (await apiClient.put<NawaroRapsProfile>(`/api/v1/agrar/nawaro/raps-profiles/${id}`, payload)).data
}

export async function deleteRapsProfile(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/agrar/nawaro/raps-profiles/${id}`)
}

export async function deriveRapsProfileFromOps(id: string, period?: string): Promise<NawaroRapsDeriveResult> {
  const query = period ? `?period=${encodeURIComponent(period)}` : ''
  return (await apiClient.post<NawaroRapsDeriveResult>(`/api/v1/agrar/nawaro/raps-profiles/${id}/derive-from-ops${query}`)).data
}
