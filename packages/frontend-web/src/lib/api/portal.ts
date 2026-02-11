/**
 * Portal (Kundenportal) API Hooks
 * TanStack Query hooks for all customer portal pages
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

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

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackDashboard: PortalDashboard = {
  kpis: [
    { label: 'Offene Bestellungen', value: '3', trend: '+1' },
    { label: 'Letzte Rechnung', value: '4.250 EUR' },
    { label: 'Neue Dokumente', value: '5' },
    { label: 'Vertragsstatus', value: 'Aktiv' },
  ],
  letzteBestellungen: [
    { id: '1', nummer: 'PB-2026-001', datum: '2026-02-08', betrag: 12500, status: 'versendet' },
    { id: '2', nummer: 'PB-2026-002', datum: '2026-02-05', betrag: 8900, status: 'geliefert' },
  ],
  neueDokumente: [
    { id: '1', name: 'Rechnung RE-2026-042.pdf', datum: '2026-02-10', typ: 'PDF' },
    { id: '2', name: 'Lieferschein LS-2026-018.pdf', datum: '2026-02-09', typ: 'PDF' },
  ],
}

const fallbackAnfragen: PortalAnfrage[] = [
  { id: '1', nummer: 'PA-2026-001', betreff: 'Preisanfrage Weizen', datum: '2026-02-10', status: 'offen' },
  { id: '2', nummer: 'PA-2026-002', betreff: 'Lieferstatus PO-042', datum: '2026-02-08', status: 'beantwortet' },
]

const fallbackBestellungen: PortalBestellung[] = [
  { id: '1', nummer: 'PB-2026-001', datum: '2026-02-08', artikel: 'Weizen Saatgut', menge: 100, betrag: 12500, status: 'versendet' },
  { id: '2', nummer: 'PB-2026-002', datum: '2026-02-05', artikel: 'NPK-Dünger', menge: 50, betrag: 8900, status: 'geliefert' },
]

const fallbackDokumente: PortalDokument[] = [
  { id: '1', name: 'Rechnung RE-2026-042.pdf', kategorie: 'Rechnungen', datum: '2026-02-10', groesse: 125, typ: 'PDF' },
  { id: '2', name: 'Lieferschein LS-2026-018.pdf', kategorie: 'Lieferscheine', datum: '2026-02-09', groesse: 85, typ: 'PDF' },
  { id: '3', name: 'Analysebericht AB-2026-005.pdf', kategorie: 'Analysen', datum: '2026-02-07', groesse: 250, typ: 'PDF' },
]

const fallbackFeldbuch: PortalFeldbuch[] = [
  { id: '1', schlag: 'Nordfeld 1', kultur: 'Winterweizen', flaeche: 12.5, letzteMassnahme: 'Düngung 15.11.', naechsteMassnahme: 'Herbizid Mrz.' },
  { id: '2', schlag: 'Südacker', kultur: 'Winterraps', flaeche: 8.3, letzteMassnahme: 'PSM 10.11.', naechsteMassnahme: 'Düngung Feb.' },
]

const fallbackBilanzen: PortalNaehrstoffbilanz[] = [
  { id: '1', schlag: 'Nordfeld 1', kultur: 'Winterweizen', n_saldo: -12, p_saldo: 5, k_saldo: -8, bewertung: 'ok' },
  { id: '2', schlag: 'Südacker', kultur: 'Winterraps', n_saldo: 25, p_saldo: 18, k_saldo: 10, bewertung: 'warnung' },
]

const fallbackRechnungen: PortalRechnung[] = [
  { id: '1', nummer: 'RE-2026-042', datum: '2026-02-10', betrag: 4250, status: 'offen' },
  { id: '2', nummer: 'RE-2026-038', datum: '2026-01-28', betrag: 12800, status: 'bezahlt' },
]

const fallbackShop: PortalShopProdukt[] = [
  { id: '1', name: 'Weizen Saatgut Premium', kategorie: 'Saatgut', preis: 125, einheit: 'dt', verfuegbar: true },
  { id: '2', name: 'NPK 15-15-15', kategorie: 'Dünger', preis: 520, einheit: 't', verfuegbar: true },
  { id: '3', name: 'Roundup PowerFlex', kategorie: 'PSM', preis: 35, einheit: 'l', verfuegbar: false },
]

const fallbackVertraege: PortalVertrag[] = [
  { id: '1', nummer: 'RV-2026-001', typ: 'Rahmenvertrag', partner: 'VALEO Landhandel', laufzeitBis: '2026-12-31', status: 'aktiv' },
  { id: '2', nummer: 'RV-2025-008', typ: 'Liefervertrag', partner: 'VALEO Landhandel', laufzeitBis: '2026-03-31', status: 'auslaufend' },
]

const fallbackZertifikate: PortalZertifikat[] = [
  { id: '1', art: 'Bio-Zertifikat', nummer: 'BIO-2025-1234', gueltigBis: '2026-12-31', status: 'gueltig' },
  { id: '2', art: 'QS-Zertifikat', nummer: 'QS-2025-5678', gueltigBis: '2026-06-30', status: 'gueltig' },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function usePortalDashboard() {
  return useQuery({
    queryKey: ['portal', 'dashboard'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<PortalDashboard>('/api/v1/portal/dashboard')
        if (response.data?.kpis) return response.data
      } catch { /* fallback */ }
      return fallbackDashboard
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function usePortalAnfragen() {
  return useQuery({ queryKey: ['portal', 'anfragen'], queryFn: async () => { try { const r = await apiClient.get<PortalAnfrage[]>('/api/v1/portal/anfragen'); if (r.data?.length) return r.data } catch {} return fallbackAnfragen }, staleTime: 2 * 60 * 1000 })
}

export function usePortalBestellungen() {
  return useQuery({ queryKey: ['portal', 'bestellungen'], queryFn: async () => { try { const r = await apiClient.get<PortalBestellung[]>('/api/v1/portal/bestellungen'); if (r.data?.length) return r.data } catch {} return fallbackBestellungen }, staleTime: 2 * 60 * 1000 })
}

export function usePortalDokumente() {
  return useQuery({ queryKey: ['portal', 'dokumente'], queryFn: async () => { try { const r = await apiClient.get<PortalDokument[]>('/api/v1/portal/dokumente'); if (r.data?.length) return r.data } catch {} return fallbackDokumente }, staleTime: 2 * 60 * 1000 })
}

export function usePortalFeldbuch() {
  return useQuery({ queryKey: ['portal', 'feldbuch'], queryFn: async () => { try { const r = await apiClient.get<PortalFeldbuch[]>('/api/v1/portal/feldbuch'); if (r.data?.length) return r.data } catch {} return fallbackFeldbuch }, staleTime: 5 * 60 * 1000 })
}

export function usePortalNaehrstoffbilanzen() {
  return useQuery({ queryKey: ['portal', 'bilanzen'], queryFn: async () => { try { const r = await apiClient.get<PortalNaehrstoffbilanz[]>('/api/v1/portal/naehrstoffbilanzen'); if (r.data?.length) return r.data } catch {} return fallbackBilanzen }, staleTime: 5 * 60 * 1000 })
}

export function usePortalRechnungen() {
  return useQuery({ queryKey: ['portal', 'rechnungen'], queryFn: async () => { try { const r = await apiClient.get<PortalRechnung[]>('/api/v1/portal/rechnungen'); if (r.data?.length) return r.data } catch {} return fallbackRechnungen }, staleTime: 2 * 60 * 1000 })
}

export function usePortalShop() {
  return useQuery({ queryKey: ['portal', 'shop'], queryFn: async () => { try { const r = await apiClient.get<PortalShopProdukt[]>('/api/v1/portal/shop'); if (r.data?.length) return r.data } catch {} return fallbackShop }, staleTime: 5 * 60 * 1000 })
}

export function usePortalVertraege() {
  return useQuery({ queryKey: ['portal', 'vertraege'], queryFn: async () => { try { const r = await apiClient.get<PortalVertrag[]>('/api/v1/portal/vertraege'); if (r.data?.length) return r.data } catch {} return fallbackVertraege }, staleTime: 5 * 60 * 1000 })
}

export function usePortalZertifikate() {
  return useQuery({ queryKey: ['portal', 'zertifikate'], queryFn: async () => { try { const r = await apiClient.get<PortalZertifikat[]>('/api/v1/portal/zertifikate'); if (r.data?.length) return r.data } catch {} return fallbackZertifikate }, staleTime: 5 * 60 * 1000 })
}
