/**
 * Futter/Futtermittel API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

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

export function useEinzelfutter() {
  return useQuery({
    queryKey: ['futter', 'einzel'],
    queryFn: async () => (await apiClient.get<Einzelfutter[]>('/api/v1/futter/einzelfuttermittel')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useMischfutter() {
  return useQuery({
    queryKey: ['futter', 'misch'],
    queryFn: async () => (await apiClient.get<Mischfutter[]>('/api/v1/futter/mischfuttermittel')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterChargen() {
  return useQuery({
    queryKey: ['futter', 'chargen'],
    queryFn: async () => (await apiClient.get<FutterCharge[]>('/api/v1/futter/chargen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterQualitaet() {
  return useQuery({
    queryKey: ['futter', 'qualitaet'],
    queryFn: async () => (await apiClient.get<FutterQualitaet[]>('/api/v1/futter/qualitaetskontrolle')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useFutterStatistik() {
  return useQuery({
    queryKey: ['futter', 'statistik'],
    queryFn: async () => (await apiClient.get<FutterStatistik>('/api/v1/futter/statistik')).data,
    staleTime: 5 * 60 * 1000,
  })
}
