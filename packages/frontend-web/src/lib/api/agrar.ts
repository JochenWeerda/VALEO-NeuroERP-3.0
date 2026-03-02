import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type Duenger = {
  id: string
  artikelnummer: string
  name: string
  typ: string
  hersteller: string
  n_gehalt: number
  p_gehalt: number
  k_gehalt: number
  s_gehalt: number
  mg_gehalt: number
  dmv_nummer: string
  eu_zulassung: string
  ablauf_zulassung: string
  gefahrstoff_klasse: string
  wassergefaehrdend: boolean
  lagerklasse: string
  kultur_typ: string
  dosierung_min: number
  dosierung_max: number
  zeitpunkt: string
  ek_preis: number
  vk_preis: number
  lagerbestand: number
  ist_aktiv: boolean
  ausgangsstoff_explosivstoffe: boolean
  erklaerung_landwirt_erforderlich: boolean
  erklaerung_landwirt_status: string | null
}

export type PSM = {
  id: string
  mittel: string
  wirkstoff: string
  kulturen: string[]
  zulassungBis: string
  status: 'aktiv' | 'auslaufend' | 'widerrufen'
  erklaerungLandwirtStatus: string | null
}

export type Kunde = {
  id: string
  name: string
  betriebsnummer: string
  bundesland: string
  schlagCount: number
  gesamtflaeche: number
}

export type Schlag = {
  id: string
  name: string
  flik?: string
  flaeche: number
  kultur: string
  vorkultur?: string
  kundeId: string
  kundeName: string
  gemeinde: string
  gemarkung?: string
  bodenart?: string
  ackerzahl?: number
  status: 'aktiv' | 'stillgelegt' | 'brache'
  letzteMassnahme?: {
    datum: string
    typ: string
  }
}

export type Aussaat = {
  id: string
  schlag: string
  kultur: string
  sorte: string
  datum: string
  flaeche: number
  saatmenge: number
  status: 'geplant' | 'ausgesaet'
}

export type Bodenprobe = {
  id: string
  schlag: string
  datum: string
  labor: string
  n: number
  p: number
  k: number
  ph: number
  status: 'beauftragt' | 'analysiert' | 'abgeschlossen'
}

export type Kultur = {
  id: string
  name: string
  kategorie: string
  flaeche: number
  ertrag: number
  preis: number
  deckungsbeitrag: number
}

export type Ernte = {
  id: string
  schlag: string
  kultur: string
  datum: string
  menge: number
  ertrag: number
  status: 'geplant' | 'laufend' | 'abgeschlossen'
}

export type Sorte = {
  id: string
  name: string
  art: string
  zuechter: string
  zulassung: string
  eigenschaft: string[]
  status: 'aktiv' | 'auslaufend'
}

export type DuengerKomponente = {
  id: string
  name: string
  n_gehalt: number
  p_gehalt: number
  k_gehalt: number
  preis_pro_tonne: number
}

export type Massnahme = {
  id: string
  datum: string
  uhrzeit?: string
  schlagId: string
  schlagName: string
  kundeId: string
  kundeName: string
  typ: string
  mittel: string
  menge: number
  einheit: string
  flaeche: number
  anwender?: string
  windgeschwindigkeit?: number
  temperatur?: number
  auflagen?: string[]
  compliant: boolean
  exportiert: boolean
}

export type PSMAuflage = {
  id: string
  psm_id: string
  psm_name: string
  auflage_typ: string
  beschreibung: string
  prioritaet: 'hoch' | 'mittel' | 'niedrig'
  status: 'offen' | 'erfuellt' | 'ueberfaellig'
  faellig_am: string
  compliance_status: 'ok' | 'warning' | 'critical'
  zugewiesen_an: string
}

export type Schadbild = {
  id: string
  name: string
  beschreibung: string
  schwere: 'leicht' | 'mittel' | 'schwer' | 'gering' | 'hoch'
  kultur: string
  saison: string
}

export type WirkstoffGruppe = {
  id: string
  name: string
  wirkstoffe: string[]
  resistenzRisiko: 'hoch' | 'mittel' | 'niedrig'
  letzteAnwendung: string
  rotationsEmpfehlung: string
}

export type WasserschutzZone = {
  id: string
  name: string
  typ: string
  zone: string
  restriktionsgrad: 'hoch' | 'mittel' | 'niedrig'
  koordinaten: { lat: number; lng: number }
  radius: number
}

export type PSMSachkundeNachweis = {
  id: string
  kunde: string
  kundennr: string
  nachweisNr: string
  ausstellungsdatum: string
  gueltigBis: string
  ausstellendeStelle: string
  status: 'gueltig' | 'ablaufend' | 'abgelaufen'
  complianceStatus?: 'compliant' | 'warning' | 'non-compliant'
}

export const agrarKeys = {
  all: ['agrar'] as const,
  duenger: () => [...agrarKeys.all, 'duenger'] as const,
  psm: () => [...agrarKeys.all, 'psm'] as const,
  kunden: () => [...agrarKeys.all, 'kunden'] as const,
  schlaege: (kundeId?: string) => [...agrarKeys.all, 'schlaege', kundeId] as const,
}

function extractList<T>(payload: unknown, endpoint: string): T[] {
  if (Array.isArray(payload)) return payload as T[]
  if (payload && typeof payload === 'object') {
    const rec = payload as Record<string, unknown>
    if (Array.isArray(rec.items)) return rec.items as T[]
    if (Array.isArray(rec.data)) return rec.data as T[]
    if (Array.isArray(rec.results)) return rec.results as T[]
  }
  throw new Error(`Invalid API payload for ${endpoint}`)
}

async function fetchList<T>(endpoint: string): Promise<T[]> {
  const response = await apiClient.get<unknown>(endpoint)
  return extractList<T>(response.data, endpoint)
}

export function useDuenger(filters?: { search?: string; typ?: string; hersteller?: string }) {
  return useQuery({
    queryKey: [...agrarKeys.duenger(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.typ) params.append('typ', filters.typ)
      if (filters?.hersteller) params.append('hersteller', filters.hersteller)

      const endpoint = `/api/v1/agrar/duenger?${String(params)}`
      const response = await apiClient.get<unknown>(endpoint)
      const items = extractList<Duenger>(response.data, '/api/v1/agrar/duenger')
      const total = (response.data as { total?: number })?.total ?? items.length
      return { items, total }
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useDuengerItem(id: string) {
  return useQuery({
    queryKey: [...agrarKeys.duenger(), id],
    queryFn: async () => {
      const response = await apiClient.get<Duenger>(`/api/v1/agrar/duenger/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateDuenger() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Partial<Duenger>) => {
      const response = await apiClient.post<Duenger>('/api/v1/agrar/duenger', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.duenger() })
    },
  })
}

export function useUpdateDuenger() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Duenger> }) => {
      const response = await apiClient.patch<Duenger>(`/api/v1/agrar/duenger/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.duenger() })
    },
  })
}

export function useDeleteDuenger() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/agrar/duenger/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.duenger() })
    },
  })
}

export function usePSM(filters?: { search?: string; source?: 'local' | 'bvl' }) {
  return useQuery({
    queryKey: [...agrarKeys.psm(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      params.append('source', filters?.source ?? 'bvl')

      const endpoint = `/api/v1/agrar/psm?${String(params)}`
      const response = await apiClient.get<unknown>(endpoint)
      const items = extractList<PSM>(response.data, '/api/v1/agrar/psm')
      const total = (response.data as { total?: number })?.total ?? items.length
      return { items, total }
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function usePSMItem(id: string) {
  return useQuery({
    queryKey: [...agrarKeys.psm(), id],
    queryFn: async () => {
      const response = await apiClient.get<PSM>(`/api/v1/agrar/psm/${id}?source=bvl`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useKunden() {
  return useQuery({
    queryKey: agrarKeys.kunden(),
    queryFn: async () => {
      const response = await apiClient.get<unknown>('/api/v1/agrar/kunden')
      return extractList<Kunde>(response.data, '/api/v1/agrar/kunden')
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useAgrarKunden() {
  return useKunden()
}

export function useKundeItem(id: string) {
  return useQuery({
    queryKey: [...agrarKeys.kunden(), id],
    queryFn: async () => {
      const response = await apiClient.get<Kunde>(`/api/v1/agrar/kunden/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useSchlaege(kundeId?: string) {
  return useQuery({
    queryKey: agrarKeys.schlaege(kundeId),
    queryFn: async () => {
      const params = kundeId && kundeId !== 'all' ? `?kundeId=${kundeId}` : ''
      const response = await apiClient.get<unknown>(`/api/v1/agrar/schlaege${params}`)
      return extractList<Schlag>(response.data, '/api/v1/agrar/schlaege')
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useSchlagItem(id: string) {
  return useQuery({
    queryKey: [...agrarKeys.schlaege(), id],
    queryFn: async () => {
      const response = await apiClient.get<Schlag>(`/api/v1/agrar/schlaege/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateSchlag() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Partial<Schlag>) => {
      const response = await apiClient.post<Schlag>('/api/v1/agrar/schlaege', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.schlaege() })
    },
  })
}

export function useUpdateSchlag() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Schlag> }) => {
      const response = await apiClient.patch<Schlag>(`/api/v1/agrar/schlaege/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.schlaege() })
    },
  })
}

export function useDeleteSchlag() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/agrar/schlaege/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: agrarKeys.schlaege() })
    },
  })
}

export function useAussaaten() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'aussaaten'],
    queryFn: () => fetchList<Aussaat>('/api/v1/agrar/aussaaten'),
    staleTime: 2 * 60 * 1000,
  })
}

export function useBodenproben() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'bodenproben'],
    queryFn: () => fetchList<Bodenprobe>('/api/v1/agrar/bodenproben'),
    staleTime: 2 * 60 * 1000,
  })
}

export function useKulturen() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'kulturen'],
    queryFn: () => fetchList<Kultur>('/api/v1/agrar/kulturen'),
    staleTime: 5 * 60 * 1000,
  })
}

export function useErnten() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'ernten'],
    queryFn: () => fetchList<Ernte>('/api/v1/agrar/ernte'),
    staleTime: 2 * 60 * 1000,
  })
}

export function useSorten() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'sorten'],
    queryFn: () => fetchList<Sorte>('/api/v1/agrar/saatgut/sortenregister'),
    staleTime: 5 * 60 * 1000,
  })
}

export function useDuengerKomponenten() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'duenger-komponenten'],
    queryFn: () => fetchList<DuengerKomponente>('/api/v1/agrar/duenger/komponenten'),
    staleTime: 5 * 60 * 1000,
  })
}

export function useMassnahmen() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'massnahmen'],
    queryFn: () => fetchList<Massnahme>('/api/v1/agrar/feldbuch/massnahmen'),
    staleTime: 2 * 60 * 1000,
  })
}

export function usePSMAuflagen() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'psm-auflagen'],
    queryFn: () => fetchList<PSMAuflage>('/api/v1/agrar/psm/auflagen'),
    staleTime: 2 * 60 * 1000,
  })
}

export function useSchadbilder() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'schadbilder'],
    queryFn: () => fetchList<Schadbild>('/api/v1/agrar/psm/schadbilder'),
    staleTime: 10 * 60 * 1000,
  })
}

export function useWirkstoffGruppen() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'wirkstoffgruppen'],
    queryFn: () => fetchList<WirkstoffGruppe>('/api/v1/agrar/psm/wirkstoffgruppen'),
    staleTime: 10 * 60 * 1000,
  })
}

export function useWasserschutzZonen() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'wasserschutz-zonen'],
    queryFn: () => fetchList<WasserschutzZone>('/api/v1/agrar/psm/wasserschutz-zonen'),
    staleTime: 10 * 60 * 1000,
  })
}

export function usePSMSachkundeRegister() {
  return useQuery({
    queryKey: [...agrarKeys.all, 'psm-sachkunde-register'],
    queryFn: async () => {
      const response = await apiClient.get<unknown>('/api/v1/compliance/sachkunde-register')
      return extractList<PSMSachkundeNachweis>(response.data, '/api/v1/compliance/sachkunde-register')
    },
    staleTime: 5 * 60 * 1000,
  })
}

// ────────────────────────────────────────────────────────────────────────────
// Wetter (BrightSky DWD + Open-Meteo ICON-D2)
// ────────────────────────────────────────────────────────────────────────────

export type WetterAktuell = {
  timestamp?: string
  temperatur?: number           // °C
  taupunkt?: number             // °C
  relative_feuchte?: number     // %
  niederschlag?: number         // mm/h
  windgeschwindigkeit?: number  // km/h
  windrichtung?: number         // Grad
  windboee?: number             // km/h
  bedeckungsgrad?: number       // %
  sonnenscheindauer?: number    // min/h
  strahlung?: number            // Wh/m²
  luftdruck?: number            // hPa
  sichtweite?: number           // m
  bedingung?: string            // icon code (sunny, rainy, ...)
  station_id?: string
  station_name?: string
  station_lat?: number
  station_lon?: number
}

export type WetterWarnung = {
  id: string
  event: string
  headline: string
  description?: string
  instruction?: string
  severity: string    // Minor | Moderate | Severe | Extreme
  urgency?: string
  certainty?: string
  gueltig_von?: string
  gueltig_bis?: string
  ausgabezeit?: string
}

export type PrognoseTag = {
  datum: string
  temperatur_max?: number
  temperatur_min?: number
  niederschlag_summe?: number    // mm
  niederschlag_stunden?: number
  et0_fao?: number               // mm (FAO Grasreferenz-ET₀)
  wachstumsgradtage?: number     // Wachstumsgradtage base 0°C
  sonnenscheindauer?: number     // Stunden
  windgeschwindigkeit_max?: number  // km/h
  uv_index_max?: number
}

export type Maschine = {
  id: string
  name: string
  typ: string
  hersteller?: string
  modell?: string
  baujahr?: number
  kennzeichen?: string
  fahrgestellnummer?: string
  leistung_kw?: number
  betriebsstunden: number
  naechste_wartung_stunden?: number
  naechste_wartung_datum?: string
  status: 'verfuegbar' | 'im-einsatz' | 'werkstatt' | 'stillgelegt'
  standort?: string
  customer_id?: string
  notiz?: string
  ist_aktiv: boolean
  wartung_faellig: boolean
  auslastung?: number
  created_at?: string
  updated_at?: string
}

type WetterCoords = { lat: number; lon: number }

export function useWetterAktuell(coords?: WetterCoords) {
  return useQuery({
    queryKey: [...agrarKeys.all, 'wetter-aktuell', coords],
    queryFn: async () => {
      const response = await apiClient.get<WetterAktuell>(
        `/api/v1/agrar/wetter/aktuell?lat=${coords!.lat}&lon=${coords!.lon}`
      )
      return response.data
    },
    enabled: !!coords,
    staleTime: 10 * 60 * 1000,   // 10 Min — Wetterdaten ändern sich nicht so schnell
    retry: 1,
  })
}

export function useWetterWarnungen(coords?: WetterCoords) {
  return useQuery({
    queryKey: [...agrarKeys.all, 'wetter-warnungen', coords],
    queryFn: async () => {
      const response = await apiClient.get<WetterWarnung[]>(
        `/api/v1/agrar/wetter/warnungen?lat=${coords!.lat}&lon=${coords!.lon}`
      )
      return response.data
    },
    enabled: !!coords,
    staleTime: 15 * 60 * 1000,
    retry: 1,
  })
}

export function useWetterPrognose(coords?: WetterCoords, tage = 7) {
  return useQuery({
    queryKey: [...agrarKeys.all, 'wetter-prognose', coords, tage],
    queryFn: async () => {
      const response = await apiClient.get<PrognoseTag[]>(
        `/api/v1/agrar/wetter/prognose?lat=${coords!.lat}&lon=${coords!.lon}&tage=${tage}`
      )
      return response.data
    },
    enabled: !!coords,
    staleTime: 30 * 60 * 1000,   // 30 Min
    retry: 1,
  })
}

// ────────────────────────────────────────────────────────────────────────────
// Maschinenpark
// ────────────────────────────────────────────────────────────────────────────

export function useMaschinen(filters?: { typ?: string; status?: string; customer_id?: string }) {
  return useQuery({
    queryKey: [...agrarKeys.all, 'maschinen', filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.typ) params.append('typ', filters.typ)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.customer_id) params.append('customer_id', filters.customer_id)
      const response = await apiClient.get<{ items: Maschine[]; total: number; stats: Record<string, number> }>(
        `/api/v1/agrar/maschinen?${String(params)}`
      )
      return response.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useCreateMaschine() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Partial<Maschine>) => {
      const response = await apiClient.post<Maschine>('/api/v1/agrar/maschinen', data)
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [...agrarKeys.all, 'maschinen'] }),
  })
}

export function useUpdateMaschine() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Maschine> }) => {
      const response = await apiClient.patch<Maschine>(`/api/v1/agrar/maschinen/${id}`, data)
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [...agrarKeys.all, 'maschinen'] }),
  })
}

export function useSetMaschineStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const response = await apiClient.patch<Maschine>(`/api/v1/agrar/maschinen/${id}/status`, { status })
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [...agrarKeys.all, 'maschinen'] }),
  })
}

export function useBuchBetriebsstunden() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, stunden }: { id: string; stunden: number }) => {
      const response = await apiClient.patch<Maschine>(`/api/v1/agrar/maschinen/${id}/stunden`, { stunden })
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [...agrarKeys.all, 'maschinen'] }),
  })
}
