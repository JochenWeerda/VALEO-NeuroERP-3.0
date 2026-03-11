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

const EMPTY_EINKAUF_REPORTS: { spend: EinkaufSpendItem[]; performance: EinkaufPerformance[] } = {
  spend: [],
  performance: [],
}

const EMPTY_EINKAUF_REPORTS_STANDARD: {
  openOrders: EinkaufOpenOrder[]
  supplierPerformance: EinkaufSupplierPerformance[]
  toleranceReports: EinkaufToleranceReport[]
} = {
  openOrders: [],
  supplierPerformance: [],
  toleranceReports: [],
}

export function useBestellvorschlaege() {
  return useQuery({
    queryKey: einkaufKeys.vorschlaege(),
    queryFn: async () => (await apiClient.get<Bestellvorschlag[]>('/api/v1/einkauf/bestellvorschlaege')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useWarengruppen() {
  return useQuery({
    queryKey: einkaufKeys.warengruppen(),
    queryFn: async () => (await apiClient.get<Warengruppe[]>('/api/v1/einkauf/warengruppen')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufAnfragen() {
  return useQuery({
    queryKey: einkaufKeys.anfragen(),
    queryFn: async () => (await apiClient.get<EinkaufAnfrage[]>('/api/v1/einkauf/anfragen')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useEinkaufAngebote() {
  return useQuery({
    queryKey: einkaufKeys.angebote(),
    queryFn: async () => (await apiClient.get<EinkaufAngebot[]>('/api/v1/einkauf/angebote')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useAnlieferavis() {
  return useQuery({
    queryKey: einkaufKeys.anlieferavis(),
    queryFn: async () => (await apiClient.get<Anlieferavis[]>('/api/v1/einkauf/anlieferavis')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useAuftragsbestaetigungen() {
  return useQuery({
    queryKey: einkaufKeys.bestaetigungen(),
    queryFn: async () => (await apiClient.get<Auftragsbestaetigung[]>('/api/v1/einkauf/auftragsbestaetigungen')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useRechnungseingaenge() {
  return useQuery({
    queryKey: einkaufKeys.rechnungseingaenge(),
    queryFn: async () => (await apiClient.get<Rechnungseingang[]>('/api/v1/einkauf/rechnungseingaenge')).data,
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

/** Workflow: Prüfen (entwurf → geprüft) */
export function useRechnungseingangPruefen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) =>
      (await apiClient.post<{ message: string; status: string }>(`/api/v1/einkauf/rechnungseingaenge/${encodeURIComponent(id)}/pruefen`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() }),
  })
}

/** Workflow: Freigeben (geprüft → freigegeben) */
export function useRechnungseingangFreigeben() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) =>
      (await apiClient.post<{ message: string; status: string }>(`/api/v1/einkauf/rechnungseingaenge/${encodeURIComponent(id)}/freigeben`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() }),
  })
}

/** Workflow: Verbuchen (freigegeben → verbucht) */
export function useRechnungseingangVerbuchen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) =>
      (await apiClient.post<{ message: string; status: string }>(`/api/v1/einkauf/rechnungseingaenge/${encodeURIComponent(id)}/verbuchen`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() }),
  })
}

export function useEinkaufReports() {
  return useQuery({
    queryKey: einkaufKeys.reports(),
    queryFn: async () => (await apiClient.get<{ spend: EinkaufSpendItem[]; performance: EinkaufPerformance[] }>('/api/v1/einkauf/reports')).data,
    initialData: EMPTY_EINKAUF_REPORTS,
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
    initialData: EMPTY_EINKAUF_REPORTS_STANDARD,
    staleTime: 5 * 60 * 1000,
  })
}

export function useEinkaufRetouren() {
  return useQuery({
    queryKey: einkaufKeys.retouren(),
    queryFn: async () => (await apiClient.get<EinkaufRetoure[]>('/api/v1/einkauf/retouren')).data,
    initialData: [],
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
    initialData: [],
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
    initialData: [],
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

// ─────────────────────────────────────────────────────────────────────────────
// Bestell-Vorschlag Engines + CRUD
// ─────────────────────────────────────────────────────────────────────────────

export type BvPosition = {
  article_id: string
  artikel_nr?: string
  artikel_bezeichnung?: string
  artikel_gruppe?: string
  einheit?: string
  ist_bestand: number
  offene_auftraege: number
  bedarf: number
  vorschlag_menge: number
  bestell_menge?: number
  mindestbestand: number
  maximalbestand: number
  meldebestand: number
  lieferant_id?: string
  lieferant_name?: string
  letzter_preis?: number
  preis_einheit?: string
  letzter_kauf_datum?: string
  wiederbeschaffungs_tage?: number
  reichweite_tage?: number
}

export type EinkaufLieferant = {
  id: string
  lieferantennummer: string
  firmenname: string
  ort?: string
  email?: string
  telefon?: string
  zahlungsbedingungen?: string
  lieferzeit_tage?: number
  bewertung?: number
  aktiv: boolean
}

export type EinkaufKontrakt = {
  id: string
  kontraktnummer: string
  lieferant_id: string
  bezeichnung?: string
  gueltig_von?: string
  gueltig_bis?: string
  status: string
  kontrakt_typ: string
  gesamtmenge?: number
  offene_menge?: number
}

export type ArtikelLagerParam = {
  id: string
  article_id: string
  warehouse_id?: string
  mindestbestand: number
  maximalbestand: number
  meldebestand: number
  soll_bestand?: number
  std_lieferant_id?: string
  std_bestellmenge?: number
  std_einheit?: string
  wiederbeschaffungs_tage: number
  durchschnitt_verbrauch_tag?: number
  reichweite_tage?: number
  aktiv: boolean
  notiz?: string
}

export type EinkaufBestellung = {
  id: string
  bestellnummer: string
  lieferant_id: string
  lieferant_name?: string
  bestelldatum: string
  lieferdatum_wunsch?: string
  status: string
  versand_art: string
  versandt_am?: string
  netto_summe?: number
  brutto_summe?: number
  positionen_anz: number
}

export const bvKeys = {
  lager:   (p?: Record<string, unknown>) => ['bv', 'lager',   p] as const,
  verkauf: (p?: Record<string, unknown>) => ['bv', 'verkauf', p] as const,
  rohware: (p?: Record<string, unknown>) => ['bv', 'rohware', p] as const,
  list:    (p?: Record<string, unknown>) => ['bv', 'list',    p] as const,
  lieferanten:  ['bv', 'lieferanten']  as const,
  kontrakte:    ['bv', 'kontrakte']    as const,
  alp:          ['bv', 'alp']          as const,
  bestellungen: ['bv', 'bestellungen'] as const,
}

// Engine-Hooks
export function useVorschlagLager(params?: {
  niederlassung_id?: string
  artikelgruppe?: string
  artikel_nr?: string
  nur_unter_meldebestand?: boolean
}) {
  return useQuery({
    queryKey: bvKeys.lager(params),
    queryFn: async () => {
      const p = new URLSearchParams()
      if (params?.niederlassung_id) p.set('niederlassung_id', params.niederlassung_id)
      if (params?.artikelgruppe) p.set('artikelgruppe', params.artikelgruppe)
      if (params?.artikel_nr) p.set('artikelNr', params.artikel_nr)
      if (params?.nur_unter_meldebestand !== undefined)
        p.set('nur_unter_meldebestand', String(params.nur_unter_meldebestand))
      const qs = p.toString() ? `?${p.toString()}` : ''
      return (await apiClient.get<BvPosition[]>(`/api/v1/einkauf/bestellvorschlaege/lager${qs}`)).data
    },
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useVorschlagVerkauf(params?: {
  niederlassung_id?: string
  artikelgruppe?: string
  von_datum?: string
  bis_datum?: string
}) {
  return useQuery({
    queryKey: bvKeys.verkauf(params),
    queryFn: async () => {
      const p = new URLSearchParams()
      if (params?.niederlassung_id) p.set('niederlassung_id', params.niederlassung_id)
      if (params?.artikelgruppe) p.set('artikelgruppe', params.artikelgruppe)
      if (params?.von_datum) p.set('vonDatum', params.von_datum)
      if (params?.bis_datum) p.set('bisDatum', params.bis_datum)
      const qs = p.toString() ? `?${p.toString()}` : ''
      return (await apiClient.get<BvPosition[]>(`/api/v1/einkauf/bestellvorschlaege/verkauf${qs}`)).data
    },
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useVorschlagRohware(params?: {
  stichtag?: string
  niederlassung_id?: string
}) {
  return useQuery({
    queryKey: bvKeys.rohware(params),
    queryFn: async () => {
      const p = new URLSearchParams()
      if (params?.stichtag) p.set('stichtag', params.stichtag)
      if (params?.niederlassung_id) p.set('niederlassung_id', params.niederlassung_id)
      const qs = p.toString() ? `?${p.toString()}` : ''
      return (await apiClient.get<BvPosition[]>(`/api/v1/einkauf/bestellvorschlaege/rohware${qs}`)).data
    },
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useSaveBestellvorschlag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: {
      vorschlag_typ: string
      positionen: BvPosition[]
      parameter?: Record<string, unknown>
      niederlassung_id?: string
      bezeichnung?: string
    }) => (await apiClient.post('/api/v1/einkauf/bestellvorschlaege', data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bv', 'list'] }),
  })
}

export function useVorschlagZuBestellung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vorschlag_id: string) =>
      (await apiClient.post(`/api/v1/einkauf/bestellvorschlaege/${encodeURIComponent(vorschlag_id)}/zu-bestellung`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['bv', 'list'] })
      qc.invalidateQueries({ queryKey: bvKeys.bestellungen })
    },
  })
}

// ArtikelLagerParameter
export function useArtikelLagerParameter(article_id?: string) {
  return useQuery({
    queryKey: [...bvKeys.alp, article_id],
    queryFn: async () => {
      const qs = article_id ? `?article_id=${encodeURIComponent(article_id)}` : ''
      return (await apiClient.get<ArtikelLagerParam[]>(`/api/v1/einkauf/artikel-lager-parameter${qs}`)).data
    },
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useUpsertArtikelLagerParameter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<ArtikelLagerParam> & { article_id: string }) => {
      if (data.id) {
        return (await apiClient.put(`/api/v1/einkauf/artikel-lager-parameter/${encodeURIComponent(data.id)}`, data)).data
      }
      return (await apiClient.post('/api/v1/einkauf/artikel-lager-parameter', data)).data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: bvKeys.alp }),
  })
}

// Lieferanten
export function useEinkaufLieferanten(aktiv?: boolean) {
  return useQuery({
    queryKey: [...bvKeys.lieferanten, aktiv],
    queryFn: async () => {
      const qs = aktiv !== undefined ? `?aktiv=${aktiv}` : ''
      return (await apiClient.get<EinkaufLieferant[]>(`/api/v1/einkauf/lieferanten${qs}`)).data
    },
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

// Kontrakte
export function useEinkaufKontrakte(lieferant_id?: string) {
  return useQuery({
    queryKey: [...bvKeys.kontrakte, lieferant_id],
    queryFn: async () => {
      const qs = lieferant_id ? `?lieferant_id=${encodeURIComponent(lieferant_id)}` : ''
      return (await apiClient.get<EinkaufKontrakt[]>(`/api/v1/einkauf/kontrakte${qs}`)).data
    },
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

// Bestellungen
export function useEinkaufBestellungen(params?: { status?: string; von?: string; bis?: string }) {
  return useQuery({
    queryKey: [...bvKeys.bestellungen, params],
    queryFn: async () => {
      const p = new URLSearchParams()
      if (params?.status) p.set('status', params.status)
      if (params?.von) p.set('von', params.von)
      if (params?.bis) p.set('bis', params.bis)
      const qs = p.toString() ? `?${p.toString()}` : ''
      return (await apiClient.get<EinkaufBestellung[]>(`/api/v1/einkauf/bestellungen${qs}`)).data
    },
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useBestellungVersenden() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, versand_art }: { id: string; versand_art: 'email' | 'fax' | 'edi' }) =>
      (await apiClient.post(`/api/v1/einkauf/bestellungen/${encodeURIComponent(id)}/versenden?versand_art=${versand_art}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: bvKeys.bestellungen }),
  })
}
