/**
 * Portal (Kundenportal) API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
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

export function usePortalDashboard() {
  return useQuery({
    queryKey: ['portal', 'dashboard'],
    queryFn: async () => (await apiClient.get<PortalDashboard>('/api/v1/portal/dashboard')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalAnfragen() {
  return useQuery({
    queryKey: ['portal', 'anfragen'],
    queryFn: async () => (await apiClient.get<PortalAnfrage[]>('/api/v1/portal/anfragen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalBestellungen() {
  return useQuery({
    queryKey: ['portal', 'bestellungen'],
    queryFn: async () => (await apiClient.get<PortalBestellung[]>('/api/v1/portal/bestellungen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalDokumente() {
  return useQuery({
    queryKey: ['portal', 'dokumente'],
    queryFn: async () => (await apiClient.get<PortalDokument[]>('/api/v1/portal/dokumente')).data,
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
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalFeldbuch() {
  return useQuery({
    queryKey: ['portal', 'feldbuch'],
    queryFn: async () => (await apiClient.get<PortalFeldbuch[]>('/api/v1/portal/feldbuch')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalNaehrstoffbilanzen() {
  return useQuery({
    queryKey: ['portal', 'bilanzen'],
    queryFn: async () => (await apiClient.get<PortalNaehrstoffbilanz[]>('/api/v1/portal/naehrstoffbilanzen')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalRechnungen() {
  return useQuery({
    queryKey: ['portal', 'rechnungen'],
    queryFn: async () => (await apiClient.get<PortalRechnung[]>('/api/v1/portal/rechnungen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalShop() {
  return useQuery({
    queryKey: ['portal', 'shop'],
    queryFn: async () => (await apiClient.get<PortalShopProdukt[]>('/api/v1/portal/shop')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalVertraege() {
  return useQuery({
    queryKey: ['portal', 'vertraege'],
    queryFn: async () => (await apiClient.get<PortalVertrag[]>('/api/v1/portal/vertraege')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function usePortalZertifikate() {
  return useQuery({
    queryKey: ['portal', 'zertifikate'],
    queryFn: async () => (await apiClient.get<PortalZertifikat[]>('/api/v1/portal/zertifikate')).data,
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
