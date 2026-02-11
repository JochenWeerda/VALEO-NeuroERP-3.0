/**
 * POS (Point of Sale) API Hooks
 * TanStack Query hooks for Gift Cards, Rabatte, Suspended Sales, Tagesabschluss, TSE
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type GiftCard = {
  id: string; nummer: string; betrag: number; restbetrag: number; ausgestellt: string; gueltigBis: string; status: 'aktiv' | 'eingeloest' | 'abgelaufen'
}

export type Rabatt = {
  id: string; name: string; typ: 'prozent' | 'betrag'; wert: number; bedingung: string; gueltigVon: string; gueltigBis: string; status: 'aktiv' | 'inaktiv'
}

export type SuspendedSale = {
  id: string; kassierer: string; zeitpunkt: string; positionen: number; betrag: number; grund: string
}

export type Tagesabschluss = {
  datum: string; umsatzBar: number; umsatzKarte: number; umsatzGesamt: number; transaktionen: number; stornos: number; retouren: number
  kassenbestand: { soll: number; ist: number; differenz: number }
}

export type TSEEintrag = {
  id: string; transaktionsNr: string; zeitstempel: string; typ: string; betrag: number; signatur: string; status: 'ok' | 'fehler'
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackGiftCards: GiftCard[] = [
  { id: '1', nummer: 'GC-2026-001', betrag: 50, restbetrag: 35, ausgestellt: '2026-01-15', gueltigBis: '2027-01-15', status: 'aktiv' },
  { id: '2', nummer: 'GC-2026-002', betrag: 100, restbetrag: 0, ausgestellt: '2025-12-20', gueltigBis: '2026-12-20', status: 'eingeloest' },
]

const fallbackRabatte: Rabatt[] = [
  { id: '1', name: 'Frühlings-Rabatt', typ: 'prozent', wert: 10, bedingung: 'Ab 500 EUR Bestellwert', gueltigVon: '2026-03-01', gueltigBis: '2026-05-31', status: 'aktiv' },
  { id: '2', name: 'Neukunden-Bonus', typ: 'betrag', wert: 25, bedingung: 'Erste Bestellung', gueltigVon: '2026-01-01', gueltigBis: '2026-12-31', status: 'aktiv' },
  { id: '3', name: 'Mengenrabatt Dünger', typ: 'prozent', wert: 5, bedingung: 'Ab 10t Dünger', gueltigVon: '2026-01-01', gueltigBis: '2026-06-30', status: 'aktiv' },
]

const fallbackSuspended: SuspendedSale[] = [
  { id: '1', kassierer: 'Müller', zeitpunkt: '2026-02-10 14:32', positionen: 5, betrag: 245.80, grund: 'Kunde holt Ware' },
  { id: '2', kassierer: 'Schmidt', zeitpunkt: '2026-02-10 11:15', positionen: 2, betrag: 89.50, grund: 'Preisabklärung' },
]

const fallbackTagesabschluss: Tagesabschluss = {
  datum: new Date().toLocaleDateString('de-DE'), umsatzBar: 3450, umsatzKarte: 8920, umsatzGesamt: 12370, transaktionen: 47, stornos: 2, retouren: 1,
  kassenbestand: { soll: 3650, ist: 3645, differenz: -5 },
}

const fallbackTSE: TSEEintrag[] = [
  { id: '1', transaktionsNr: 'TSE-2026-000142', zeitstempel: '2026-02-10 14:32:15', typ: 'Beleg', betrag: 125.50, signatur: 'a1b2c3d4e5...', status: 'ok' },
  { id: '2', transaktionsNr: 'TSE-2026-000141', zeitstempel: '2026-02-10 14:28:03', typ: 'Beleg', betrag: 89.90, signatur: 'f6g7h8i9j0...', status: 'ok' },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function useGiftCards() {
  return useQuery({ queryKey: ['pos', 'gift-cards'], queryFn: async () => { try { const r = await apiClient.get<GiftCard[]>('/api/v1/pos/gift-cards'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackGiftCards }, staleTime: 2 * 60 * 1000 })
}

export function useRabatte() {
  return useQuery({ queryKey: ['pos', 'rabatte'], queryFn: async () => { try { const r = await apiClient.get<Rabatt[]>('/api/v1/pos/rabatte'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackRabatte }, staleTime: 5 * 60 * 1000 })
}

export function useSuspendedSales() {
  return useQuery({ queryKey: ['pos', 'suspended'], queryFn: async () => { try { const r = await apiClient.get<SuspendedSale[]>('/api/v1/pos/suspended-sales'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackSuspended }, staleTime: 30 * 1000 })
}

export function useTagesabschluss() {
  return useQuery({ queryKey: ['pos', 'tagesabschluss'], queryFn: async () => { try { const r = await apiClient.get<Tagesabschluss>('/api/v1/pos/tagesabschluss'); if (r.data?.datum) return r.data } catch { /* fallback to mock data */ } return fallbackTagesabschluss }, staleTime: 60 * 1000 })
}

export function useTSEJournal() {
  return useQuery({ queryKey: ['pos', 'tse-journal'], queryFn: async () => { try { const r = await apiClient.get<TSEEintrag[]>('/api/v1/pos/tse-journal'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackTSE }, staleTime: 30 * 1000 })
}
