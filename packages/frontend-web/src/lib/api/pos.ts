/**
 * POS (Point of Sale) API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

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

const EMPTY_TAGESABSCHLUSS: Tagesabschluss = {
  datum: '',
  umsatzBar: 0,
  umsatzKarte: 0,
  umsatzGesamt: 0,
  transaktionen: 0,
  stornos: 0,
  retouren: 0,
  kassenbestand: {
    soll: 0,
    ist: 0,
    differenz: 0,
  },
}

export function useGiftCards() {
  return useQuery({
    queryKey: ['pos', 'gift-cards'],
    queryFn: async () => (await apiClient.get<GiftCard[]>('/api/v1/pos/gift-cards')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useRabatte() {
  return useQuery({
    queryKey: ['pos', 'rabatte'],
    queryFn: async () => (await apiClient.get<Rabatt[]>('/api/v1/pos/rabatte')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useSuspendedSales() {
  return useQuery({
    queryKey: ['pos', 'suspended'],
    queryFn: async () => (await apiClient.get<SuspendedSale[]>('/api/v1/pos/suspended-sales')).data,
    initialData: [],
    staleTime: 30 * 1000,
  })
}

export function useTagesabschluss() {
  return useQuery({
    queryKey: ['pos', 'tagesabschluss'],
    queryFn: async () => (await apiClient.get<Tagesabschluss>('/api/v1/pos/tagesabschluss')).data,
    initialData: EMPTY_TAGESABSCHLUSS,
    staleTime: 60 * 1000,
  })
}

export function useTSEJournal() {
  return useQuery({
    queryKey: ['pos', 'tse-journal'],
    queryFn: async () => (await apiClient.get<TSEEintrag[]>('/api/v1/pos/tse-journal')).data,
    initialData: [],
    staleTime: 30 * 1000,
  })
}
