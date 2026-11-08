/**
 * Futter/Futtermittel API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

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

const EMPTY_FUTTER_STATISTIK: FutterStatistik = {
  gesamtProduktion: 0,
  gesamtAbsatz: 0,
  durchschnittsPreis: 0,
  topProdukte: [],
}

export function useFutterChargen() {
  return useQuery({
    queryKey: ['futter', 'chargen'],
    queryFn: async () => (await apiClient.get<FutterCharge[]>('/api/v1/futter/chargen')).data,
    initialData: [],
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterQualitaet() {
  return useQuery({
    queryKey: ['futter', 'qualitaet'],
    queryFn: async () => (await apiClient.get<FutterQualitaet[]>('/api/v1/futter/qualitaetskontrolle')).data,
    initialData: [],
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterStatistik() {
  return useQuery({
    queryKey: ['futter', 'statistik'],
    queryFn: async () => (await apiClient.get<FutterStatistik>('/api/v1/futter/statistik')).data,
    initialData: EMPTY_FUTTER_STATISTIK,
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
    staleTime: 5 * 60 * 1000,
  })
}

// ── Detail-Types ──────────────────────────────────────────────

export type EinzelfutterDetail = {
  id: string
  artikel: string
  art: string
  herkunft: string
  lieferant: string
  protein: number
  energie: number
  gvo_status: string
  qs_milch: boolean
  verfuegbar: number
}

export type MischfutterKomponente = {
  komponente: string
  anteil: number
}

export type MischfutterDetail = {
  id: string
  typ: string
  tierart: string
  leistungsstufe: string
  rezeptur: MischfutterKomponente[]
  protein: number
  energie: number
}

export type RezeptKomponente = {
  id: string
  name: string
  anteil: number
}

export type RezeptDetail = {
  id: string
  name: string
  tierart: string
  komponenten: RezeptKomponente[]
  protein: number
  energie: number
}

// ── Detail-Hooks ──────────────────────────────────────────────

export function useEinzelfutterDetail(id: string) {
  return useQuery({
    queryKey: ['futter', 'einzel', id],
    queryFn: async () => (await apiClient.get<EinzelfutterDetail>(`/api/v1/futter/einzelfuttermittel/${id}`)).data,
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  })
}

export function useMischfutterDetail(id: string) {
  return useQuery({
    queryKey: ['futter', 'misch', id],
    queryFn: async () => (await apiClient.get<MischfutterDetail>(`/api/v1/futter/mischfuttermittel/${id}`)).data,
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  })
}

export function useRezeptDetail(id: string) {
  return useQuery({
    queryKey: ['rezepte', id],
    queryFn: async () => (await apiClient.get<RezeptDetail>(`/api/v1/futter/rezepte/${id}`)).data,
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  })
}
