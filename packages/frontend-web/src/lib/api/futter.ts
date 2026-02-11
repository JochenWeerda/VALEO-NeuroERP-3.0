/**
 * Futter/Futtermittel API Hooks
 * TanStack Query hooks for Einzelfutter, Mischfutter, Charge-Verfolgung, Qualität, Statistik
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type Einzelfutter = {
  id: string
  artikelnummer: string
  name: string
  kategorie: string
  rohprotein: number
  rohfaser: number
  energie: number
  preis: number
  bestand: number
  status: 'verfuegbar' | 'knapp' | 'ausverkauft'
}

export type Mischfutter = {
  id: string
  artikelnummer: string
  name: string
  tierart: string
  phase: string
  komponenten: number
  preis: number
  bestand: number
  status: 'verfuegbar' | 'in-produktion' | 'ausverkauft'
}

export type FutterCharge = {
  id: string
  chargenId: string
  produkt: string
  herstelldatum: string
  mhd: string
  menge: number
  status: 'freigegeben' | 'gesperrt' | 'in-pruefung'
}

export type FutterQualitaet = {
  id: string
  chargenId: string
  produkt: string
  pruefung: string
  ergebnis: string
  datum: string
  status: 'bestanden' | 'nicht-bestanden' | 'ausstehend'
}

export type FutterStatistik = {
  gesamtProduktion: number
  gesamtAbsatz: number
  durchschnittsPreis: number
  topProdukte: { name: string; menge: number }[]
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackEinzel: Einzelfutter[] = [
  { id: '1', artikelnummer: 'EF-001', name: 'Sojaschrot 44%', kategorie: 'Eiweißfutter', rohprotein: 44, rohfaser: 7, energie: 13.2, preis: 420, bestand: 85, status: 'verfuegbar' },
  { id: '2', artikelnummer: 'EF-002', name: 'Rapsschrot', kategorie: 'Eiweißfutter', rohprotein: 35, rohfaser: 12, energie: 11.8, preis: 310, bestand: 120, status: 'verfuegbar' },
  { id: '3', artikelnummer: 'EF-003', name: 'Weizenkleie', kategorie: 'Energiefutter', rohprotein: 16, rohfaser: 10, energie: 10.5, preis: 185, bestand: 15, status: 'knapp' },
]

const fallbackMisch: Mischfutter[] = [
  { id: '1', artikelnummer: 'MF-001', name: 'Milchleistungsfutter 20/4', tierart: 'Rind', phase: 'Laktation', komponenten: 8, preis: 380, bestand: 200, status: 'verfuegbar' },
  { id: '2', artikelnummer: 'MF-002', name: 'Schweinemast Endmast', tierart: 'Schwein', phase: 'Endmast', komponenten: 6, preis: 295, bestand: 0, status: 'in-produktion' },
]

const fallbackChargen: FutterCharge[] = [
  { id: '1', chargenId: 'FC-2026-001', produkt: 'Milchleistungsfutter 20/4', herstelldatum: '2026-02-01', mhd: '2026-08-01', menge: 50, status: 'freigegeben' },
  { id: '2', chargenId: 'FC-2026-002', produkt: 'Sojaschrot 44%', herstelldatum: '2026-01-15', mhd: '2026-07-15', menge: 85, status: 'freigegeben' },
]

const fallbackQualitaet: FutterQualitaet[] = [
  { id: '1', chargenId: 'FC-2026-001', produkt: 'Milchleistungsfutter', pruefung: 'Rohprotein-Analyse', ergebnis: '20.3% (Soll: 20%)', datum: '2026-02-02', status: 'bestanden' },
  { id: '2', chargenId: 'FC-2026-002', produkt: 'Sojaschrot', pruefung: 'Mykotoxin-Test', ergebnis: '< Grenzwert', datum: '2026-01-16', status: 'bestanden' },
]

const fallbackStatistik: FutterStatistik = {
  gesamtProduktion: 1250, gesamtAbsatz: 1180, durchschnittsPreis: 345,
  topProdukte: [
    { name: 'Milchleistungsfutter 20/4', menge: 450 },
    { name: 'Schweinemast Endmast', menge: 380 },
    { name: 'Sojaschrot 44%', menge: 350 },
  ],
}

// ── Hooks ──────────────────────────────────────────────────────────────

export function useEinzelfutter() {
  return useQuery({
    queryKey: ['futter', 'einzel'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Einzelfutter[]>('/api/v1/futter/einzelfuttermittel')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackEinzel
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useMischfutter() {
  return useQuery({
    queryKey: ['futter', 'misch'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Mischfutter[]>('/api/v1/futter/mischfuttermittel')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackMisch
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterChargen() {
  return useQuery({
    queryKey: ['futter', 'chargen'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<FutterCharge[]>('/api/v1/futter/chargen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackChargen
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterQualitaet() {
  return useQuery({
    queryKey: ['futter', 'qualitaet'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<FutterQualitaet[]>('/api/v1/futter/qualitaetskontrolle')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackQualitaet
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterStatistik() {
  return useQuery({
    queryKey: ['futter', 'statistik'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<FutterStatistik>('/api/v1/futter/statistik')
        if (response.data?.gesamtProduktion) return response.data
      } catch { /* fallback */ }
      return fallbackStatistik
    },
    staleTime: 5 * 60 * 1000,
  })
}
