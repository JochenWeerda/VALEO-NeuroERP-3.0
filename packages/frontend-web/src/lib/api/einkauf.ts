/**
 * Einkauf (Procurement) API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

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
export type EinkaufSupplierPerformance = {
  supplier: string
  onTimeDelivery: number
  qualityScore: number
  priceScore: number
  serviceScore: number
  overallScore: number
  totalOrders: number
}
export type EinkaufOpenOrder = {
  id?: string
  purchaseOrderNumber?: string
  supplierId?: string
  supplierName?: string
  status?: string
  deliveryDate?: string
  totalAmount?: number
}
export type EinkaufToleranceReport = { purchaseOrderNumber?: string; deviation?: number; type?: string }
export type EinkaufRetoure = {
  id: string
  nummer: string
  grund: string
  status: string
  datum?: string | null
  lieferant?: string
}

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
  reportsStandard: () => [...einkaufKeys.all, 'reports-standard'] as const,
  retouren: () => [...einkaufKeys.all, 'retouren'] as const,
}

export function useBestellvorschlaege() {
  return useQuery({
    queryKey: einkaufKeys.vorschlaege(),
    queryFn: async () => (await apiClient.get<Bestellvorschlag[]>('/api/v1/einkauf/bestellvorschlaege')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useWarengruppen() {
  return useQuery({
    queryKey: einkaufKeys.warengruppen(),
    queryFn: async () => (await apiClient.get<Warengruppe[]>('/api/v1/einkauf/warengruppen')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufAnfragen() {
  return useQuery({
    queryKey: einkaufKeys.anfragen(),
    queryFn: async () => (await apiClient.get<EinkaufAnfrage[]>('/api/v1/einkauf/anfragen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useEinkaufAngebote() {
  return useQuery({
    queryKey: einkaufKeys.angebote(),
    queryFn: async () => (await apiClient.get<EinkaufAngebot[]>('/api/v1/einkauf/angebote')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useAnlieferavis() {
  return useQuery({
    queryKey: einkaufKeys.anlieferavis(),
    queryFn: async () => (await apiClient.get<Anlieferavis[]>('/api/v1/einkauf/anlieferavis')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useAuftragsbestaetigungen() {
  return useQuery({
    queryKey: einkaufKeys.bestaetigungen(),
    queryFn: async () => (await apiClient.get<Auftragsbestaetigung[]>('/api/v1/einkauf/auftragsbestaetigungen')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useRechnungseingaenge() {
  return useQuery({
    queryKey: einkaufKeys.rechnungseingaenge(),
    queryFn: async () => (await apiClient.get<Rechnungseingang[]>('/api/v1/einkauf/rechnungseingaenge')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useEinkaufReports() {
  return useQuery({
    queryKey: einkaufKeys.reports(),
    queryFn: async () => (await apiClient.get<{ spend: EinkaufSpendItem[]; performance: EinkaufPerformance[] }>('/api/v1/einkauf/reports')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufReportsStandard() {
  return useQuery({
    queryKey: einkaufKeys.reportsStandard(),
    queryFn: async () =>
      (
        await apiClient.get<{
          openOrders: EinkaufOpenOrder[]
          supplierPerformance: EinkaufSupplierPerformance[]
          toleranceReports: EinkaufToleranceReport[]
        }>('/api/v1/einkauf/reports/standard')
      ).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufRetouren() {
  return useQuery({
    queryKey: einkaufKeys.retouren(),
    queryFn: async () => (await apiClient.get<EinkaufRetoure[]>('/api/v1/einkauf/retouren')).data,
    staleTime: 60 * 1000,
  })
}

export function useUpdateEinkaufRetoure() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, status, grund }: { id: string; status: string; grund?: string }) =>
      (await apiClient.patch(`/api/v1/einkauf/retouren/${encodeURIComponent(id)}`, { status, grund })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.retouren() }),
  })
}
