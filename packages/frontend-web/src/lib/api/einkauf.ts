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

export type EinkaufLieferscheinPosition = {
  id: string
  pos_nr: number
  artikel_nr?: string | null
  lieferant_artikel_nr?: string | null
  bezeichnung?: string | null
  gebinde_nr?: string | null
  gebinde?: number | null
  menge: number
  einheit?: string | null
  einzelpreis?: number | null
  nettobetrag?: number | null
  lagerhalle?: string | null
  lagerfach?: string | null
  charge?: string | null
  serien_nr?: string | null
  kontakt?: string | null
  prozent?: number | null
  master_nr?: string | null
}

export type EinkaufLieferschein = {
  id: string
  tenant_id: string
  lieferschein_nr: string
  lieferschein_datum: string
  niederlassung?: string | null
  lieferant_id?: string | null
  lieferant_name?: string | null
  zahlungsbedingung?: string | null
  texte?: string | null
  zwischenhaendler?: string | null
  wie_vom_ls: boolean
  lieferanten_stamm?: string | null
  liefer_termin?: string | null
  lieferdatum?: string | null
  liefer_nr?: string | null
  bediener?: string | null
  erledigt: boolean
  verfuegbarer_bestand?: number | null
  summe_gewicht?: number | null
  mwst_betrag?: number | null
  netto_betrag?: number | null
  brutto_betrag?: number | null
  created_at: string
  updated_at: string
  positionen: EinkaufLieferscheinPosition[]
}

export type EinkaufLieferscheinCreate = Omit<EinkaufLieferschein, 'id' | 'tenant_id' | 'created_at' | 'updated_at'> & {
  positionen: Omit<EinkaufLieferscheinPosition, 'id'>[]
}

export type EinkaufFrachtauftrag = {
  id: string
  tenant_id: string
  frachtauftrag_nr: string
  frachtauftrag_erzeugt?: string | null
  niederlassung?: string | null
  liefertermin?: string | null
  spediteur_nr?: string | null
  spediteur_name?: string | null
  email?: string | null
  telefon?: string | null
  belegnummer?: string | null
  lade_datum?: string | null
  kunde_id?: string | null
  kunde_name?: string | null
  debitoren_filter?: string | null
  created_at: string
  updated_at: string
}

export type EinkaufFrachtauftragCreate = Omit<EinkaufFrachtauftrag, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>

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
  lieferscheine: () => [...einkaufKeys.all, 'lieferscheine'] as const,
  frachtauftraege: () => [...einkaufKeys.all, 'frachtauftraege'] as const,
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

export function useEinkaufLieferscheine() {
  return useQuery({
    queryKey: einkaufKeys.lieferscheine(),
    queryFn: async () => (await apiClient.get<EinkaufLieferschein[]>('/api/v1/einkauf/lieferscheine')).data,
    staleTime: 60 * 1000,
  })
}

export function useCreateEinkaufLieferschein() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: EinkaufLieferscheinCreate) =>
      (await apiClient.post<EinkaufLieferschein>('/api/v1/einkauf/lieferscheine', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.lieferscheine() }),
  })
}

export function useDeleteEinkaufLieferschein() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => (await apiClient.delete(`/api/v1/einkauf/lieferscheine/${encodeURIComponent(id)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.lieferscheine() }),
  })
}

export function useEinkaufFrachtauftraege() {
  return useQuery({
    queryKey: einkaufKeys.frachtauftraege(),
    queryFn: async () => (await apiClient.get<EinkaufFrachtauftrag[]>('/api/v1/einkauf/frachtauftraege')).data,
    staleTime: 60 * 1000,
  })
}

export function useCreateEinkaufFrachtauftrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: EinkaufFrachtauftragCreate) =>
      (await apiClient.post<EinkaufFrachtauftrag>('/api/v1/einkauf/frachtauftraege', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.frachtauftraege() }),
  })
}

export function useDeleteEinkaufFrachtauftrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => (await apiClient.delete(`/api/v1/einkauf/frachtauftraege/${encodeURIComponent(id)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.frachtauftraege() }),
  })
}
