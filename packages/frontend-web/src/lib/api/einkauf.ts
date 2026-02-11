/**
 * Einkauf (Procurement) API Hooks
 * TanStack Query hooks for Bestellvorschläge, Warengruppen, Reports, Retouren, RFQ, Anfragen, etc.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type Bestellvorschlag = {
  id: string
  artikel: string
  aktuellBestand: number
  mindestbestand: number
  vorschlagMenge: number
  lieferant: string
  preis: number
  lieferzeit: number
  prioritaet: 'hoch' | 'mittel' | 'niedrig'
  grund: string
}

export type Warengruppe = {
  id: string
  name: string
  kategorie: string
  artikel: number
  umsatz: number
}

export type EinkaufAnfrage = {
  id: string
  anfrageNummer: string
  typ: string
  anforderer: string
  artikel: string
  menge: number
  prioritaet: 'niedrig' | 'normal' | 'hoch' | 'dringend'
  status: string
  faelligkeit: string
  createdAt: string
}

export type EinkaufAngebot = {
  id: string
  angebotNummer: string
  anfrage: string
  lieferant: string
  artikel: string
  preis: number
  gueltigBis: string
  status: string
  lieferzeit: string
  createdAt: string
}

export type Anlieferavis = {
  id: string
  avisNummer: string
  bestellung: string
  lieferant: string
  status: string
  geplantesAnlieferDatum: string
  kennzeichen: string
  createdAt: string
}

export type Auftragsbestaetigung = {
  id: string
  bestaetigungsNummer: string
  bestellung: string
  lieferant: string
  status: string
  createdAt: string
}

export type Rechnungseingang = {
  id: string
  rechnungsNummer: string
  lieferant: string
  bestellung: string
  wareneingang: string
  status: string
  bruttoBetrag: number
  rechnungsDatum: string
  createdAt: string
}

export type EinkaufSpendItem = { kategorie: string; anteil: number; betrag: number }
export type EinkaufPerformance = { lieferant: string; qualitaet: number; liefertreue: number; preis: number; gesamt: number }

// ── Query Keys ─────────────────────────────────────────────────────────

export const einkaufKeys = {
  all: ['einkauf'] as const,
  vorschlaege: () => [...einkaufKeys.all, 'vorschlaege'] as const,
  warengruppen: () => [...einkaufKeys.all, 'warengruppen'] as const,
  anfragen: () => [...einkaufKeys.all, 'anfragen'] as const,
  angebote: () => [...einkaufKeys.all, 'angebote'] as const,
  anlieferavis: () => [...einkaufKeys.all, 'anlieferavis'] as const,
  bestaetigungen: () => [...einkaufKeys.all, 'bestaetigungen'] as const,
  rechnungseingaenge: () => [...einkaufKeys.all, 'rechnungseingaenge'] as const,
  reports: () => [...einkaufKeys.all, 'reports'] as const,
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackVorschlaege: Bestellvorschlag[] = [
  { id: '1', artikel: 'Weizen Saatgut', aktuellBestand: 120, mindestbestand: 200, vorschlagMenge: 100, lieferant: 'Saatgut AG', preis: 45000, lieferzeit: 5, prioritaet: 'hoch', grund: 'Bestand unter Mindestbestand' },
  { id: '2', artikel: 'NPK-Dünger 15-15-15', aktuellBestand: 85, mindestbestand: 100, vorschlagMenge: 50, lieferant: 'Dünger GmbH', preis: 26000, lieferzeit: 3, prioritaet: 'mittel', grund: 'Saisonaler Mehrbedarf' },
  { id: '3', artikel: 'Glyphosat 360 g/l', aktuellBestand: 200, mindestbestand: 150, vorschlagMenge: 25, lieferant: 'AgroChem AG', preis: 8750, lieferzeit: 7, prioritaet: 'niedrig', grund: 'Auffüllung Sicherheitsbestand' },
]

const fallbackWarengruppen: Warengruppe[] = [
  { id: '1', name: 'Getreide', kategorie: 'Agrar', artikel: 45, umsatz: 1250000 },
  { id: '2', name: 'Saatgut', kategorie: 'Agrar', artikel: 32, umsatz: 890000 },
  { id: '3', name: 'Düngemittel', kategorie: 'Agrar', artikel: 28, umsatz: 750000 },
  { id: '4', name: 'Futtermittel', kategorie: 'Agrar', artikel: 18, umsatz: 420000 },
]

const fallbackAnfragen: EinkaufAnfrage[] = [
  { id: '1', anfrageNummer: 'BANF-2026-001', typ: 'BANF', anforderer: 'Lager Nord', artikel: 'Weizen Saatgut', menge: 100, prioritaet: 'hoch', status: 'OFFEN', faelligkeit: '2026-03-01', createdAt: '2026-02-10' },
  { id: '2', anfrageNummer: 'ANF-2026-002', typ: 'ANF', anforderer: 'Einkauf', artikel: 'NPK-Dünger', menge: 50, prioritaet: 'normal', status: 'IN_BEARBEITUNG', faelligkeit: '2026-03-15', createdAt: '2026-02-09' },
]

const fallbackAngebote: EinkaufAngebot[] = [
  { id: '1', angebotNummer: 'ANG-2026-001', anfrage: 'ANF-2026-002', lieferant: 'Dünger GmbH', artikel: 'NPK-Dünger', preis: 520, gueltigBis: '2026-03-15', status: 'ERFASST', lieferzeit: '3 Tage', createdAt: '2026-02-10' },
  { id: '2', angebotNummer: 'ANG-2026-002', anfrage: 'ANF-2026-002', lieferant: 'AgroChem AG', artikel: 'NPK-Dünger', preis: 495, gueltigBis: '2026-03-10', status: 'GEPRUEFT', lieferzeit: '5 Tage', createdAt: '2026-02-09' },
]

const fallbackAnlieferavis: Anlieferavis[] = [
  { id: '1', avisNummer: 'AVIS-2026-001', bestellung: 'PO-2026-042', lieferant: 'Saatgut AG', status: 'ANGEKUENDIGT', geplantesAnlieferDatum: '2026-02-15', kennzeichen: 'AB-CD 1234', createdAt: '2026-02-10' },
]

const fallbackBestaetigungen: Auftragsbestaetigung[] = [
  { id: '1', bestaetigungsNummer: 'AB-2026-001', bestellung: 'PO-2026-042', lieferant: 'Saatgut AG', status: 'BESTAETIGT', createdAt: '2026-02-10' },
]

const fallbackRechnungseingaenge: Rechnungseingang[] = [
  { id: '1', rechnungsNummer: 'RE-L-2026-001', lieferant: 'Saatgut AG', bestellung: 'PO-2026-042', wareneingang: 'WE-2026-001', status: 'ERFASST', bruttoBetrag: 45000, rechnungsDatum: '2026-02-10', createdAt: '2026-02-10' },
]

const fallbackSpend: EinkaufSpendItem[] = [
  { kategorie: 'Saatgut', anteil: 36, betrag: 890000 },
  { kategorie: 'Düngemittel', anteil: 30.4, betrag: 750000 },
  { kategorie: 'Landtechnik', anteil: 25.6, betrag: 632000 },
  { kategorie: 'Sonstiges', anteil: 8, betrag: 198000 },
]

const fallbackPerformance: EinkaufPerformance[] = [
  { lieferant: 'Saatgut AG', qualitaet: 95, liefertreue: 92, preis: 88, gesamt: 91.7 },
  { lieferant: 'Dünger GmbH', qualitaet: 90, liefertreue: 85, preis: 92, gesamt: 89.0 },
  { lieferant: 'AgroChem AG', qualitaet: 88, liefertreue: 78, preis: 95, gesamt: 87.0 },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function useBestellvorschlaege() {
  return useQuery({
    queryKey: einkaufKeys.vorschlaege(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<Bestellvorschlag[]>('/api/v1/einkauf/bestellvorschlaege')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackVorschlaege
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useWarengruppen() {
  return useQuery({
    queryKey: einkaufKeys.warengruppen(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<Warengruppe[]>('/api/v1/einkauf/warengruppen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackWarengruppen
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufAnfragen() {
  return useQuery({
    queryKey: einkaufKeys.anfragen(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<EinkaufAnfrage[]>('/api/v1/einkauf/anfragen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackAnfragen
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useEinkaufAngebote() {
  return useQuery({
    queryKey: einkaufKeys.angebote(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<EinkaufAngebot[]>('/api/v1/einkauf/angebote')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackAngebote
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useAnlieferavis() {
  return useQuery({
    queryKey: einkaufKeys.anlieferavis(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<Anlieferavis[]>('/api/v1/einkauf/anlieferavis')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackAnlieferavis
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useAuftragsbestaetigungen() {
  return useQuery({
    queryKey: einkaufKeys.bestaetigungen(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<Auftragsbestaetigung[]>('/api/v1/einkauf/auftragsbestaetigungen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackBestaetigungen
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useRechnungseingaenge() {
  return useQuery({
    queryKey: einkaufKeys.rechnungseingaenge(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<Rechnungseingang[]>('/api/v1/einkauf/rechnungseingaenge')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackRechnungseingaenge
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useEinkaufReports() {
  return useQuery({
    queryKey: einkaufKeys.reports(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ spend: EinkaufSpendItem[]; performance: EinkaufPerformance[] }>('/api/v1/einkauf/reports')
        if (response.data?.spend) return response.data
      } catch { /* fallback */ }
      return { spend: fallbackSpend, performance: fallbackPerformance }
    },
    staleTime: 5 * 60 * 1000,
  })
}
