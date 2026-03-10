/**
 * Portal (Kundenportal) API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type PortalDashboard = {
  kpis: { label: string; value: string; trend?: string }[]
  letzteBestellungen: { id: string; nummer: string; datum: string; betrag: number; status: string }[]
  neueDokumente: { id: string; name: string; datum: string; typ: string }[]
}

export type PortalAnfrage = {
  id: string; nummer: string; betreff: string; datum: string; status: 'offen' | 'beantwortet' | 'geschlossen'
}

export type PortalBestellung = {
  id: string; nummer: string; datum: string; artikel: string; menge: number; betrag: number; status: 'bestellt' | 'versendet' | 'geliefert'
}

export type PortalDokument = {
  id: string; name: string; kategorie: string; datum: string; groesse: number; typ: string
}

export type PortalLieferscheinCompliance = {
  number: string
  date: string
  customerId: string
  supplierName?: string
  totalNutrientNKg?: number
  totalNutrientP2o5Kg?: number
  totalCo2eKg?: number
  psmCompliance?: {
    psmLineCount?: number
    compliant?: boolean
    sachkundeStatus?: string
    sdsMitgeliefert?: string
    adrPunkte?: number
    adrWithin1000Rule?: boolean
    missingMandatoryFields?: string[]
    hinweise?: string[]
  }
}

export type PortalFeldbuch = {
  id: string; schlag: string; kultur: string; flaeche: number; letzteMassnahme: string; naechsteMassnahme: string
}

// Neue Feldbuch-Typen (echte Schlag + Maßnahmen Trennung)
export type PortalSchlag = {
  id: string
  name: string
  flik?: string
  flaeche: number
  kultur: string
  vorkultur?: string
  gemeinde: string
  gemarkung?: string
  bodenart?: string
  ackerzahl?: number
  status: 'aktiv' | 'stillgelegt' | 'brache'
}

export type PortalMassnahme = {
  id: string
  schlagId: string | null
  schlagName: string | null
  datum: string
  typ: string
  bezeichnung?: string
  mittel?: string
  menge?: number
  einheit?: string
  flaeche?: number
  anwender?: string
  quelle: 'erp_service' | 'erp_lieferschein' | 'portal'
  auflagen?: string[]
  compliant: boolean
  exportiert: boolean
  bemerkung?: string
}

export type PortalFeldbuchStats = {
  schlaege: number
  gesamtFlaeche: number
  massnahmen: number
  valeoDienste: number
}

export type PortalNaehrstoffbilanz = {
  id: string; schlag: string; kultur: string; n_saldo: number; p_saldo: number; k_saldo: number; bewertung: 'ok' | 'warnung' | 'kritisch'
}

export type PortalRechnung = {
  id: string; nummer: string; datum: string; betrag: number; status: 'offen' | 'bezahlt' | 'ueberfaellig'
}

export type PortalShopProdukt = {
  id: string; name: string; kategorie: string; preis: number; einheit: string; verfuegbar: boolean
}

export type PortalVertrag = {
  id: string; nummer: string; typ: string; partner: string; laufzeitBis: string; status: 'aktiv' | 'auslaufend' | 'beendet'
}

export type PortalZertifikat = {
  id: string; art: string; nummer: string; gueltigBis: string; status: 'gueltig' | 'ablaufend' | 'abgelaufen'
}

const EMPTY_PORTAL_DASHBOARD: PortalDashboard = {
  kpis: [],
  letzteBestellungen: [],
  neueDokumente: [],
}

const EMPTY_PORTAL_FELDBUCH_STATS: PortalFeldbuchStats = {
  schlaege: 0,
  gesamtFlaeche: 0,
  massnahmen: 0,
  valeoDienste: 0,
}

export function usePortalDashboard() {
  return useQuery({
    queryKey: ['portal', 'dashboard'],
    queryFn: async () => (await apiClient.get<PortalDashboard>('/api/v1/portal/dashboard')).data,
    initialData: EMPTY_PORTAL_DASHBOARD,
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalAnfragen() {
  return useQuery({
    queryKey: ['portal', 'anfragen'],
    queryFn: async () => (await apiClient.get<PortalAnfrage[]>('/api/v1/portal/anfragen')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalBestellungen() {
  return useQuery({
    queryKey: ['portal', 'bestellungen'],
    queryFn: async () => (await apiClient.get<PortalBestellung[]>('/api/v1/portal/bestellungen')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalDokumente() {
  return useQuery({
    queryKey: ['portal', 'dokumente'],
    queryFn: async () => (await apiClient.get<PortalDokument[]>('/api/v1/portal/dokumente')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalLieferscheinCompliance() {
  return useQuery({
    queryKey: ['portal', 'lieferscheine', 'compliance'],
    queryFn: async () => {
      const resp = await apiClient.get<{ ok: boolean; data: PortalLieferscheinCompliance[] }>('/api/mcp/documents/sales_delivery?skip=0&limit=100')
      return resp.data?.data ?? []
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalFeldbuch() {
  return useQuery({
    queryKey: ['portal', 'feldbuch'],
    queryFn: async () => (await apiClient.get<PortalFeldbuch[]>('/api/v1/portal/feldbuch')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

// ── Neue Feldbuch-Hooks ──────────────────────────────────────────────────

export function usePortalFeldbuchSchlaege() {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'schlaege'],
    queryFn: async () => (await apiClient.get<PortalSchlag[]>('/api/v1/portal/feldbuch/schlaege')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalFeldbuchMassnahmen(params?: {
  schlagId?: string
  typ?: string
  von?: string
  bis?: string
}) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'massnahmen', params],
    queryFn: async () => {
      const p = new URLSearchParams()
      if (params?.schlagId) p.set('schlag_id', params.schlagId)
      if (params?.typ) p.set('typ', params.typ)
      if (params?.von) p.set('von', params.von)
      if (params?.bis) p.set('bis', params.bis)
      const url = `/api/v1/portal/feldbuch/massnahmen${p.toString() ? `?${  p.toString()}` : ''}`
      return (await apiClient.get<PortalMassnahme[]>(url)).data
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalFeldbuchStats() {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'stats'],
    queryFn: async () => (await apiClient.get<PortalFeldbuchStats>('/api/v1/portal/feldbuch/stats')).data,
    initialData: EMPTY_PORTAL_FELDBUCH_STATS,
    staleTime: 2 * 60 * 1000,
  })
}

export function useCreatePortalSchlag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<PortalSchlag, 'id'>) =>
      (await apiClient.post<PortalSchlag>('/api/v1/portal/feldbuch/schlaege', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'schlaege'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useCreatePortalMassnahme() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<PortalMassnahme, 'id' | 'quelle' | 'compliant' | 'exportiert'>) =>
      (await apiClient.post<PortalMassnahme>('/api/v1/portal/feldbuch/massnahmen', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useUpdatePortalMassnahme() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<PortalMassnahme> }) =>
      (await apiClient.put<PortalMassnahme>(`/api/v1/portal/feldbuch/massnahmen/${id}`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
    },
  })
}

export async function exportFeldbuchCsv(
  format: 'csv' | 'ackerschlagkartei',
  params?: { schlagId?: string; von?: string; bis?: string },
): Promise<void> {
  const p = new URLSearchParams({ format })
  if (params?.schlagId) p.set('schlag_id', params.schlagId)
  if (params?.von) p.set('von', params.von)
  if (params?.bis) p.set('bis', params.bis)

  const response = await apiClient.get<Blob>(
    `/api/v1/portal/feldbuch/export?${p.toString()}`,
    { responseType: 'blob' },
  )
  const blob = response.data
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  const today = new Date().toISOString().split('T')[0]
  anchor.download = format === 'ackerschlagkartei'
    ? `ackerschlagkartei_${today}.csv`
    : `feldbuch_export_${today}.csv`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(url)
}

export async function importFeldbuchCsv(
  file: File,
): Promise<{ created: number; updated: number; errors: string[] }> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await apiClient.post<{ created: number; updated: number; errors: string[] }>(
    '/api/v1/portal/feldbuch/import',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data
}

export function usePortalNaehrstoffbilanzen() {
  return useQuery({
    queryKey: ['portal', 'bilanzen'],
    queryFn: async () => (await apiClient.get<PortalNaehrstoffbilanz[]>('/api/v1/portal/naehrstoffbilanzen')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalRechnungen() {
  return useQuery({
    queryKey: ['portal', 'rechnungen'],
    queryFn: async () => (await apiClient.get<PortalRechnung[]>('/api/v1/portal/rechnungen')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalShop() {
  return useQuery({
    queryKey: ['portal', 'shop'],
    queryFn: async () => (await apiClient.get<PortalShopProdukt[]>('/api/v1/portal/shop')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalVertraege() {
  return useQuery({
    queryKey: ['portal', 'vertraege'],
    queryFn: async () => (await apiClient.get<PortalVertrag[]>('/api/v1/portal/vertraege')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalZertifikate() {
  return useQuery({
    queryKey: ['portal', 'zertifikate'],
    queryFn: async () => (await apiClient.get<PortalZertifikat[]>('/api/v1/portal/zertifikate')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export async function downloadSalesDeliverySustainabilityCsv(year: number, customerId?: string) {
  const params = new URLSearchParams({ year: String(year) })
  if (customerId) {
    params.set('customer_id', customerId)
  }

  const response = await apiClient.get<Blob>(
    `/api/mcp/documents/analytics/sales-delivery-sustainability/export.csv?${params.toString()}`,
    { responseType: 'blob' },
  )

  const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `sales-delivery-sustainability-${year}${customerId ? `-${customerId}` : ''}.csv`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(url)
}

export async function downloadSalesDeliverySustainabilityPdf(year: number, customerId?: string) {
  const params = new URLSearchParams({ year: String(year) })
  if (customerId) {
    params.set('customer_id', customerId)
  }

  const response = await apiClient.get<Blob>(
    `/api/mcp/documents/analytics/sales-delivery-sustainability/export.pdf?${params.toString()}`,
    { responseType: 'blob' },
  )

  const blob = new Blob([response.data], { type: 'application/pdf' })
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `sales-delivery-sustainability-${year}${customerId ? `-${customerId}` : ''}.pdf`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(url)
}
