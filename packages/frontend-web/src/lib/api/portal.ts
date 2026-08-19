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
  wirtschaftsjahr?: number | null
}

export type PortalArbeitskontext = {
  customerId: string
  betriebName: string
  betriebsstaette?: string | null
  wirtschaftsjahr: number
  erntejahr: number
  rolle: string
  syncStatus: string
  datenstand: string
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
  begruendung?: string | null
  sachkundeNummer?: string | null
  sachkundeGueltigBis?: string | null
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
    // placeholderData statt initialData: eine leere Liste darf den Mount-Fetch
    // nicht unterdruecken (Seeds waren sonst bis zur ersten Mutation unsichtbar).
    placeholderData: [],
    staleTime: 5 * 60 * 1000,
  })
}

// ── Neue Feldbuch-Hooks ──────────────────────────────────────────────────

export function usePortalFeldbuchSchlaege() {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'schlaege'],
    queryFn: async () => (await apiClient.get<PortalSchlag[]>('/api/v1/portal/feldbuch/schlaege')).data,
    placeholderData: [],
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
    placeholderData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalFeldbuchStats() {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'stats'],
    queryFn: async () => (await apiClient.get<PortalFeldbuchStats>('/api/v1/portal/feldbuch/stats')).data,
    placeholderData: EMPTY_PORTAL_FELDBUCH_STATS,
    staleTime: 2 * 60 * 1000,
  })
}

// ── DüV-Auswertungen (Ackerschlagkartei AS-W1..W6) ──────────────────────────
const FB = '/api/v1/portal/feldbuch'

export function usePortalDuengebilanz(jahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'duengebilanz', jahr ?? 'current'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/duengebilanz${jahr ? `?jahr=${jahr}` : ''}`)).data,
    staleTime: 60 * 1000,
  })
}

export function usePortalDuengebedarf(jahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'duengebedarf', jahr ?? 'current'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/duengebedarf${jahr ? `?jahr=${jahr}` : ''}`)).data,
    staleTime: 60 * 1000,
  })
}

export function usePortalStoffstrombilanz(jahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'stoffstrombilanz', jahr ?? 'current'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/stoffstrombilanz${jahr ? `?jahr=${jahr}` : ''}`)).data,
    staleTime: 60 * 1000,
  })
}

export function usePortalPflanzenschutzUebersicht(jahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'psm-uebersicht', jahr ?? 'current'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/pflanzenschutz-uebersicht${jahr ? `?jahr=${jahr}` : ''}`)).data,
    staleTime: 60 * 1000,
  })
}

export function usePortalErnteAuswertung(jahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'ernte-auswertung', jahr ?? 'current'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/ernte-auswertung${jahr ? `?jahr=${jahr}` : ''}`)).data,
    staleTime: 60 * 1000,
  })
}

export function usePortalArbeitskontext(wirtschaftsjahr: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'arbeitskontext', wirtschaftsjahr],
    queryFn: async () =>
      (await apiClient.get<PortalArbeitskontext>(`${FB}/arbeitskontext?wirtschaftsjahr=${wirtschaftsjahr}`)).data,
    staleTime: 60 * 1000,
    enabled: Number.isFinite(wirtschaftsjahr),
  })
}

export function usePortalSchlaginfo(schlagId: string | null, wirtschaftsjahr?: number) {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'schlaginfo', schlagId, wirtschaftsjahr ?? 'all'],
    queryFn: async () => {
      const q = wirtschaftsjahr ? `?wirtschaftsjahr=${wirtschaftsjahr}` : ''
      return (await apiClient.get<Record<string, unknown>>(`${FB}/schlaege/${schlagId}/schlaginfo${q}`)).data
    },
    enabled: Boolean(schlagId),
    staleTime: 30 * 1000,
  })
}

export function usePortalJahreswechsel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: { von_jahr: number; nach_jahr: number; dry_run?: boolean }) =>
      (await apiClient.post<Record<string, unknown>>(`${FB}/jahreswechsel`, body)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'schlaege'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function usePortalSammelDuengung() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: {
      schlag_ids: string[]
      datum: string
      mittel: string
      menge_kg_ha: number
      n_gehalt?: number
      duenger_form?: string
      preis_je_einheit?: number
      anwender?: string
    }) => (await apiClient.post<Record<string, unknown>>(`${FB}/massnahmen/sammel-duengung`, body)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function usePortalStammdaten() {
  return useQuery({
    queryKey: ['portal', 'feldbuch', 'stammdaten'],
    queryFn: async () => (await apiClient.get<Record<string, unknown>>(`${FB}/stammdaten`)).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalQsCheckliste() {
  return useMutation({
    mutationFn: async (body: Record<string, boolean>) =>
      (await apiClient.post<Record<string, unknown>>(`${FB}/qs-checkliste`, body)).data,
  })
}

export function usePortalOfflineSync() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (ops: Array<Record<string, unknown>>) =>
      (await apiClient.post<Record<string, unknown>>(`${FB}/offline/sync`, { ops })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch'] })
    },
  })
}

/** Imperative Agent-/Tool-API (ohne React-Hooks) — Pfade = OpenAPI operation_id-Familie. */
export const portalFeldbuchAgentApi = {
  listSchlaege: async () =>
    (await apiClient.get<PortalSchlag[]>(`${FB}/schlaege`)).data,
  getSchlag: async (id: string) =>
    (await apiClient.get<PortalSchlag>(`${FB}/schlaege/${id}`)).data,
  createSchlag: async (data: Record<string, unknown>) =>
    (await apiClient.post<PortalSchlag>(`${FB}/schlaege`, data)).data,
  updateSchlag: async (id: string, data: Record<string, unknown>) =>
    (await apiClient.put<PortalSchlag>(`${FB}/schlaege/${id}`, data)).data,
  deleteSchlag: async (id: string) => {
    await apiClient.delete(`${FB}/schlaege/${id}`)
  },
  listMassnahmen: async (params?: { schlag_id?: string; typ?: string }) => {
    const p = new URLSearchParams()
    if (params?.schlag_id) p.set('schlag_id', params.schlag_id)
    if (params?.typ) p.set('typ', params.typ)
    const qs = p.toString()
    const q = qs ? `?${qs}` : ''
    return (await apiClient.get<PortalMassnahme[]>(`${FB}/massnahmen${q}`)).data
  },
  getMassnahme: async (id: string) =>
    (await apiClient.get<PortalMassnahme>(`${FB}/massnahmen/${id}`)).data,
  createMassnahme: async (data: Record<string, unknown>) =>
    (await apiClient.post<PortalMassnahme>(`${FB}/massnahmen`, data)).data,
  updateMassnahme: async (id: string, data: Record<string, unknown>) =>
    (await apiClient.put<PortalMassnahme>(`${FB}/massnahmen/${id}`, data)).data,
  deleteMassnahme: async (id: string) => {
    await apiClient.delete(`${FB}/massnahmen/${id}`)
  },
} as const

export function useCreatePortalSchlag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<PortalSchlag, 'id'> | Record<string, unknown>) =>
      portalFeldbuchAgentApi.createSchlag(data as Record<string, unknown>),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'schlaege'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useUpdatePortalSchlag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      portalFeldbuchAgentApi.updateSchlag(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'schlaege'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useDeletePortalSchlag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => portalFeldbuchAgentApi.deleteSchlag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'schlaege'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useCreatePortalMassnahme() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Record<string, unknown>) =>
      portalFeldbuchAgentApi.createMassnahme(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useUpdatePortalMassnahme() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      portalFeldbuchAgentApi.updateMassnahme(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
    },
  })
}

export function useDeletePortalMassnahme() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => portalFeldbuchAgentApi.deleteMassnahme(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'massnahmen'] })
      queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch', 'stats'] })
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
