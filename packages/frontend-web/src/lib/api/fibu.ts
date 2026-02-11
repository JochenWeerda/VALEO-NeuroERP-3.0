/**
 * Finanzbuchhaltung API Client
 * TanStack Query Hooks für alle Fibu-Endpoints
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type OffenerPosten = {
  id: string
  rechnungsnr: string
  datum: string
  faelligkeit: string
  betrag: number
  offen: number
  kunde_id?: string
  kunde_name?: string
  lieferant_id?: string
  lieferant_name?: string
  skonto_prozent?: number
  skonto_bis?: string
  mahn_stufe?: number
  zahlbar?: boolean
}

export type Buchung = {
  id: string
  belegnr: string
  datum: string
  soll_konto: string
  haben_konto: string
  betrag: number
  text: string
  belegart: string
}

export type Konto = {
  id: string
  kontonummer: string
  bezeichnung: string
  kontoart: string
  typ: string
  saldo: number
}

export type Anlage = {
  id: string
  anlagennr: string
  bezeichnung: string
  anschaffung: string
  anschaffungswert: number
  nutzungsdauer: number
  afa_satz: number
  kumulierte_afa: number
  buchwert: number
}

// ========== QUERY KEYS ==========

export const fibuKeys = {
  all: ['fibu'] as const,
  debitoren: () => [...fibuKeys.all, 'debitoren'] as const,
  kreditoren: () => [...fibuKeys.all, 'kreditoren'] as const,
  buchungen: () => [...fibuKeys.all, 'buchungen'] as const,
  konten: () => [...fibuKeys.all, 'konten'] as const,
  anlagen: () => [...fibuKeys.all, 'anlagen'] as const,
  bilanz: () => [...fibuKeys.all, 'bilanz'] as const,
  guv: () => [...fibuKeys.all, 'guv'] as const,
  bwa: () => [...fibuKeys.all, 'bwa'] as const,
  opVerwaltung: () => [...fibuKeys.all, 'op-verwaltung'] as const,
  stats: () => [...fibuKeys.all, 'stats'] as const,
}

// ========== HOOKS ==========

// Debitoren
export function useDebitoren(filters?: { ueberfaellig?: boolean; mahn_stufe?: number }) {
  return useQuery({
    queryKey: [...fibuKeys.debitoren(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.ueberfaellig !== undefined) params.append('ueberfaellig', String(filters.ueberfaellig))
      if (filters?.mahn_stufe !== undefined) params.append('mahn_stufe', String(filters.mahn_stufe))
      
      const response = await apiClient.get<OffenerPosten[]>(`/api/fibu/debitoren?${params.toString()}`)
      return response.data
    },
  })
}

export function useMahnen() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/api/fibu/debitoren/${id}/mahnen`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.debitoren() })
    },
  })
}

// Kreditoren
export function useKreditoren(filters?: { zahlbar?: boolean }) {
  return useQuery({
    queryKey: [...fibuKeys.kreditoren(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.zahlbar !== undefined) params.append('zahlbar', String(filters.zahlbar))
      
      const response = await apiClient.get<OffenerPosten[]>(`/api/fibu/kreditoren?${params.toString()}`)
      return response.data
    },
  })
}

export function useZahlungslauf() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (ids: string[]) => {
      const response = await apiClient.post('/api/fibu/kreditoren/zahlungslauf', { ids })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.kreditoren() })
      queryClient.invalidateQueries({ queryKey: fibuKeys.opVerwaltung() })
    },
  })
}

// Buchungen
export function useBuchungen(filters?: { datum_von?: string; datum_bis?: string; belegart?: string }) {
  return useQuery({
    queryKey: [...fibuKeys.buchungen(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.datum_von) params.append('datum_von', filters.datum_von)
      if (filters?.datum_bis) params.append('datum_bis', filters.datum_bis)
      if (filters?.belegart) params.append('belegart', filters.belegart)
      
      const response = await apiClient.get<Buchung[]>(`/api/fibu/buchungen?${params.toString()}`)
      return response.data
    },
  })
}

export function useCreateBuchung() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (buchung: Omit<Buchung, 'id'>) => {
      const response = await apiClient.post<Buchung>('/api/fibu/buchungen', buchung)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.buchungen() })
      queryClient.invalidateQueries({ queryKey: fibuKeys.konten() })
    },
  })
}

// Kontenplan
export function useKonten(filters?: { typ?: string }) {
  return useQuery({
    queryKey: [...fibuKeys.konten(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.typ) params.append('typ', filters.typ)
      
      const response = await apiClient.get<Konto[]>(`/api/fibu/konten?${params.toString()}`)
      return response.data
    },
  })
}

export function useKonto(kontonummer: string) {
  return useQuery({
    queryKey: [...fibuKeys.konten(), kontonummer],
    queryFn: async () => {
      const response = await apiClient.get<Konto>(`/api/fibu/konten/${kontonummer}`)
      return response.data
    },
    enabled: !!kontonummer,
  })
}

// Anlagen
export function useAnlagen() {
  return useQuery({
    queryKey: fibuKeys.anlagen(),
    queryFn: async () => {
      const response = await apiClient.get<Anlage[]>('/api/fibu/anlagen')
      return response.data
    },
  })
}

export function useCreateAnlage() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (anlage: Omit<Anlage, 'id' | 'kumulierte_afa' | 'buchwert'>) => {
      const response = await apiClient.post<Anlage>('/api/fibu/anlagen', anlage)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.anlagen() })
    },
  })
}

export function useAfaBerechnung(id: string, jahr = 2025) {
  return useQuery({
    queryKey: [...fibuKeys.anlagen(), id, 'afa', jahr],
    queryFn: async () => {
      const response = await apiClient.get(`/api/fibu/anlagen/${id}/afa?jahr=${jahr}`)
      return response.data
    },
    enabled: !!id,
  })
}

// Bilanz
export function useBilanz(stichtag = '2024-12-31') {
  return useQuery({
    queryKey: [...fibuKeys.bilanz(), stichtag],
    queryFn: async () => {
      const response = await apiClient.get(`/api/fibu/bilanz?stichtag=${stichtag}`)
      return response.data
    },
  })
}

// GuV
export function useGuV(periode = '2024') {
  return useQuery({
    queryKey: [...fibuKeys.guv(), periode],
    queryFn: async () => {
      const response = await apiClient.get(`/api/fibu/guv?periode=${periode}`)
      return response.data
    },
  })
}

// BWA
export function useBWA(monat = 10, jahr = 2025) {
  return useQuery({
    queryKey: [...fibuKeys.bwa(), monat, jahr],
    queryFn: async () => {
      const response = await apiClient.get(`/api/fibu/bwa?monat=${monat}&jahr=${jahr}`)
      return response.data
    },
  })
}

// OP-Verwaltung
export function useOPVerwaltung() {
  return useQuery({
    queryKey: fibuKeys.opVerwaltung(),
    queryFn: async () => {
      const response = await apiClient.get('/api/fibu/op-verwaltung')
      return response.data
    },
  })
}

// Stats
export function useFibuStats() {
  return useQuery({
    queryKey: fibuKeys.stats(),
    queryFn: async () => {
      const response = await apiClient.get('/api/fibu/stats')
      return response.data
    },
  })
}

// DATEV Export
export function useDATEVExport() {
  return useMutation({
    mutationFn: async (params: { typ: string; datum_von?: string; datum_bis?: string }) => {
      const searchParams = new URLSearchParams({ typ: params.typ })
      if (params.datum_von) searchParams.append('datum_von', params.datum_von)
      if (params.datum_bis) searchParams.append('datum_bis', params.datum_bis)

      const response = await apiClient.get(`/api/fibu/export/datev?${searchParams.toString()}`)
      return response.data
    },
  })
}

// ── Extended Types for Pages with Fallback ─────────────────────────────

export type Kreditlinie = {
  id: string; kunde: string; kundennr: string; limit: number; ausgenutzt: number; verfuegbar: number
  bonitaet: 'A' | 'B' | 'C' | 'D'; zahlungsziel: number; offenePosten: number; ueberfaellig: number
  status: 'aktiv' | 'gesperrt' | 'ueberzogen'
}

export type Sicherheit = {
  id: string; typ: 'abtretung' | 'sicherungseigentum' | 'buergschaft' | 'pfandrecht'
  kunde: string; kundennr: string; gegenstand: string; wert: number
  datumErstellung: string; gueltigBis?: string; status: 'aktiv' | 'abgelaufen' | 'freigegeben'
  kreditlinie: number; ausgenutzt: number
}

export type Verbindlichkeit = {
  id: string; rechnungsNr: string; lieferant: string; rechnungsDatum: string; faelligAm: string
  betrag: number; offen: number; status: 'offen' | 'teilbezahlt' | 'bezahlt' | 'skontofaehig'
}

export type Zahlungsvorschlag = {
  id: string; rechnungsNr: string; lieferant: string; betrag: number; faelligAm: string
  skonto: number; skontoBis: string; vorschlag: 'skonto' | 'faellig' | 'spaeter'; prioritaet: number
}

export type DebitOPMock = {
  id: string; rechnungsnr: string; kunde: string; kundennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; ueberfaellig: boolean; mahnStufe: number
}

export type KreditOPMock = {
  id: string; rechnungsnr: string; lieferant: string; lieferantennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; skonto: number; skontoBis: string; zahlbar: boolean
}

export type HauptbuchBuchung = {
  id: string; datum: string; belegnummer: string; konto: string; text: string; soll: number; haben: number
}

export type AnlageMock = {
  id: string; anlagennr: string; bezeichnung: string; anschaffung: string; anschaffungswert: number
  nutzungsdauer: number; afaSatz: number; kumulierteAfa: number; buchwert: number
}

// ── Extended Fallback Data ────────────────────────────────────────────

const fallbackAnlagenMock: AnlageMock[] = [
  { id: '1', anlagennr: 'ANL-001', bezeichnung: 'Mähdrescher Claas Lexion 770', anschaffung: '2022-04-15', anschaffungswert: 420000, nutzungsdauer: 10, afaSatz: 10, kumulierteAfa: 126000, buchwert: 294000 },
  { id: '2', anlagennr: 'ANL-002', bezeichnung: 'Lagerhalle B', anschaffung: '2018-06-01', anschaffungswert: 680000, nutzungsdauer: 25, afaSatz: 4, kumulierteAfa: 217600, buchwert: 462400 },
]

const fallbackDebitMock: DebitOPMock[] = [
  { id: '1', rechnungsnr: 'RE-2026-0123', kunde: 'Agrar Schmidt GmbH', kundennr: 'K-10001', datum: '2026-01-15', faelligkeit: '2026-02-15', betrag: 12500, offen: 12500, ueberfaellig: false, mahnStufe: 0 },
  { id: '2', rechnungsnr: 'RE-2025-0891', kunde: 'Landhandel Nord', kundennr: 'K-10005', datum: '2025-11-20', faelligkeit: '2025-12-20', betrag: 8500, offen: 8500, ueberfaellig: true, mahnStufe: 2 },
]

const fallbackKreditMock: KreditOPMock[] = [
  { id: '1', rechnungsnr: 'LI-2026-4523', lieferant: 'Saatgut Nord GmbH', lieferantennr: 'L-20001', datum: '2026-02-05', faelligkeit: '2026-03-05', betrag: 18500, offen: 18500, skonto: 2, skontoBis: '2026-02-15', zahlbar: true },
  { id: '2', rechnungsnr: 'LI-2026-4524', lieferant: 'Dünger GmbH', lieferantennr: 'L-20002', datum: '2026-01-28', faelligkeit: '2026-02-28', betrag: 24000, offen: 24000, skonto: 3, skontoBis: '2026-02-07', zahlbar: true },
]

const fallbackHauptbuch: HauptbuchBuchung[] = [
  { id: '1', datum: '2026-02-10', belegnummer: 'RE-2026-042', konto: '8400', text: 'Warenverkauf Weizen', soll: 0, haben: 5500 },
  { id: '2', datum: '2026-02-10', belegnummer: 'RE-2026-043', konto: '4400', text: 'Wareneinkauf Saatgut', soll: 3200, haben: 0 },
  { id: '3', datum: '2026-02-09', belegnummer: 'BA-2026-015', konto: '1200', text: 'Banküberweisung', soll: 0, haben: 8500 },
]

const fallbackKreditlinien: Kreditlinie[] = [
  { id: '1', kunde: 'Agrar Schmidt GmbH', kundennr: 'K-10023', limit: 200000, ausgenutzt: 145000, verfuegbar: 55000, bonitaet: 'A', zahlungsziel: 30, offenePosten: 145000, ueberfaellig: 0, status: 'aktiv' },
  { id: '2', kunde: 'Landhandel Nord', kundennr: 'K-10005', limit: 100000, ausgenutzt: 95000, verfuegbar: 5000, bonitaet: 'B', zahlungsziel: 14, offenePosten: 95000, ueberfaellig: 8500, status: 'ueberzogen' },
]

const fallbackSicherheiten: Sicherheit[] = [
  { id: '1', typ: 'abtretung', kunde: 'Agrar Schmidt GmbH', kundennr: 'K-10023', gegenstand: 'Forderungsabtretung Ernteerlöse 2026', wert: 150000, datumErstellung: '2026-01-15', gueltigBis: '2026-12-31', status: 'aktiv', kreditlinie: 200000, ausgenutzt: 85000 },
]

const fallbackVerbindlichkeiten: Verbindlichkeit[] = [
  { id: '1', rechnungsNr: 'ER-2026-0001', lieferant: 'Saatgut AG', rechnungsDatum: '2026-02-08', faelligAm: '2026-03-07', betrag: 25000, offen: 25000, status: 'skontofaehig' },
  { id: '2', rechnungsNr: 'ER-2026-0002', lieferant: 'Dünger GmbH', rechnungsDatum: '2026-01-20', faelligAm: '2026-02-20', betrag: 18500, offen: 12000, status: 'teilbezahlt' },
]

const fallbackZahlungsvorschlaege: Zahlungsvorschlag[] = [
  { id: '1', rechnungsNr: 'ER-2026-0001', lieferant: 'Saatgut AG', betrag: 25000, faelligAm: '2026-03-07', skonto: 2, skontoBis: '2026-02-18', vorschlag: 'skonto', prioritaet: 1 },
  { id: '2', rechnungsNr: 'ER-2026-0002', lieferant: 'Dünger GmbH', betrag: 12000, faelligAm: '2026-02-20', skonto: 0, skontoBis: '', vorschlag: 'faellig', prioritaet: 2 },
]

// ── Extended Hooks with Fallback ──────────────────────────────────────

export function useAnlagenMock() {
  return useQuery({ queryKey: [...fibuKeys.anlagen(), 'mock'], queryFn: async () => { try { const r = await apiClient.get<AnlageMock[]>('/api/fibu/anlagen'); if (r.data?.length) return r.data } catch {} return fallbackAnlagenMock }, staleTime: 5 * 60 * 1000 })
}

export function useDebitorenMock() {
  return useQuery({ queryKey: [...fibuKeys.debitoren(), 'mock'], queryFn: async () => { try { const r = await apiClient.get<DebitOPMock[]>('/api/fibu/debitoren'); if (r.data?.length) return r.data } catch {} return fallbackDebitMock }, staleTime: 2 * 60 * 1000 })
}

export function useKreditorenMock() {
  return useQuery({ queryKey: [...fibuKeys.kreditoren(), 'mock'], queryFn: async () => { try { const r = await apiClient.get<KreditOPMock[]>('/api/fibu/kreditoren'); if (r.data?.length) return r.data } catch {} return fallbackKreditMock }, staleTime: 2 * 60 * 1000 })
}

export function useHauptbuch() {
  return useQuery({ queryKey: [...fibuKeys.buchungen(), 'hauptbuch'], queryFn: async () => { try { const r = await apiClient.get<HauptbuchBuchung[]>('/api/fibu/hauptbuch'); if (r.data?.length) return r.data } catch {} return fallbackHauptbuch }, staleTime: 2 * 60 * 1000 })
}

export function useKreditlinien() {
  return useQuery({ queryKey: [...fibuKeys.all, 'kreditlinien'], queryFn: async () => { try { const r = await apiClient.get<Kreditlinie[]>('/api/fibu/kreditlinien'); if (r.data?.length) return r.data } catch {} return fallbackKreditlinien }, staleTime: 2 * 60 * 1000 })
}

export function useSicherheiten() {
  return useQuery({ queryKey: [...fibuKeys.all, 'sicherheiten'], queryFn: async () => { try { const r = await apiClient.get<Sicherheit[]>('/api/fibu/sicherheiten'); if (r.data?.length) return r.data } catch {} return fallbackSicherheiten }, staleTime: 5 * 60 * 1000 })
}

export function useVerbindlichkeiten() {
  return useQuery({ queryKey: [...fibuKeys.all, 'verbindlichkeiten'], queryFn: async () => { try { const r = await apiClient.get<Verbindlichkeit[]>('/api/fibu/verbindlichkeiten'); if (r.data?.length) return r.data } catch {} return fallbackVerbindlichkeiten }, staleTime: 2 * 60 * 1000 })
}

export function useZahlungsvorschlaege() {
  return useQuery({ queryKey: [...fibuKeys.all, 'zahlungsvorschlaege'], queryFn: async () => { try { const r = await apiClient.get<Zahlungsvorschlag[]>('/api/fibu/zahlungsvorschlaege'); if (r.data?.length) return r.data } catch {} return fallbackZahlungsvorschlaege }, staleTime: 2 * 60 * 1000 })
}
