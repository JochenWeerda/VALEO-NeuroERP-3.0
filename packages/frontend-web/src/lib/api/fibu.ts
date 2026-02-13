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

// ── Extended Types ──────────────────────────────────────────────────────

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

export type HauptbuchBuchung = {
  id: string; datum: string; belegnummer: string; konto: string; text: string; soll: number; haben: number
}

export type AnlageDetail = {
  id: string; anlagennr: string; bezeichnung: string; anschaffung: string; anschaffungswert: number
  nutzungsdauer: number; afaSatz: number; kumulierteAfa: number; buchwert: number
}

export type DebitOP = {
  id: string; rechnungsnr: string; kunde: string; kundennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; ueberfaellig: boolean; mahnStufe: number
}

export type KreditOP = {
  id: string; rechnungsnr: string; lieferant: string; lieferantennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; skonto: number; skontoBis: string; zahlbar: boolean
}

// ── Extended Hooks ──────────────────────────────────────────────────────

export function useAnlagenDetail() {
  return useQuery({
    queryKey: [...fibuKeys.anlagen(), 'detail'],
    queryFn: async () => {
      const response = await apiClient.get<AnlageDetail[]>('/api/fibu/anlagen/detail')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useDebitorenOP() {
  return useQuery({
    queryKey: [...fibuKeys.debitoren(), 'op'],
    queryFn: async () => {
      const response = await apiClient.get<DebitOP[]>('/api/fibu/debitoren/op')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useKreditorenOP() {
  return useQuery({
    queryKey: [...fibuKeys.kreditoren(), 'op'],
    queryFn: async () => {
      const response = await apiClient.get<KreditOP[]>('/api/fibu/kreditoren/op')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useHauptbuchBuchungen() {
  return useQuery({
    queryKey: [...fibuKeys.buchungen(), 'hauptbuch'],
    queryFn: async () => {
      const response = await apiClient.get<HauptbuchBuchung[]>('/api/fibu/hauptbuch')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useKreditlinien() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'kreditlinien'],
    queryFn: async () => {
      const response = await apiClient.get<Kreditlinie[]>('/api/fibu/kreditlinien')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useSicherheiten() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'sicherheiten'],
    queryFn: async () => {
      const response = await apiClient.get<Sicherheit[]>('/api/fibu/sicherheiten')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useVerbindlichkeiten() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'verbindlichkeiten'],
    queryFn: async () => {
      const response = await apiClient.get<Verbindlichkeit[]>('/api/fibu/verbindlichkeiten')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useZahlungsvorschlaege() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'zahlungsvorschlaege'],
    queryFn: async () => {
      const response = await apiClient.get<Zahlungsvorschlag[]>('/api/fibu/zahlungsvorschlaege')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}
