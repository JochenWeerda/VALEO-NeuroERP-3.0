/**
 * Agrar API Hooks
 * TanStack Query hooks for Dünger, PSM, Schlagkartei
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

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

// ── Query Keys ─────────────────────────────────────────────────────────

export const agrarKeys = {
  all: ['agrar'] as const,
  duenger: () => [...agrarKeys.all, 'duenger'] as const,
  psm: () => [...agrarKeys.all, 'psm'] as const,
  kunden: () => [...agrarKeys.all, 'kunden'] as const,
  schlaege: (kundeId?: string) => [...agrarKeys.all, 'schlaege', kundeId] as const,
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackDuenger: Duenger[] = [
  {
    id: 'DUE-001', artikelnummer: 'DUE-001', name: 'NPK 15-15-15 Universal', typ: 'Mineraldünger',
    hersteller: 'BASF', n_gehalt: 15, p_gehalt: 15, k_gehalt: 15, s_gehalt: 8, mg_gehalt: 2,
    dmv_nummer: 'DMV-2024-001', eu_zulassung: 'EU-2024-001', ablauf_zulassung: '2026-12-31',
    gefahrstoff_klasse: 'Nicht gefährlich', wassergefaehrdend: false, lagerklasse: 'Nicht wassergefährdend',
    kultur_typ: 'Getreide', dosierung_min: 200, dosierung_max: 400, zeitpunkt: 'Herbst',
    ek_preis: 450, vk_preis: 520, lagerbestand: 2500, ist_aktiv: true,
    ausgangsstoff_explosivstoffe: false, erklaerung_landwirt_erforderlich: false, erklaerung_landwirt_status: null,
  },
  {
    id: 'DUE-002', artikelnummer: 'DUE-002', name: 'Kalkammonsalpeter 27', typ: 'Mineraldünger',
    hersteller: 'Yara', n_gehalt: 27, p_gehalt: 0, k_gehalt: 0, s_gehalt: 0, mg_gehalt: 0,
    dmv_nummer: 'DMV-2024-002', eu_zulassung: 'EU-2024-002', ablauf_zulassung: '2027-06-30',
    gefahrstoff_klasse: 'Nicht gefährlich', wassergefaehrdend: false, lagerklasse: 'Nicht wassergefährdend',
    kultur_typ: 'Mais', dosierung_min: 150, dosierung_max: 300, zeitpunkt: 'Frühjahr',
    ek_preis: 380, vk_preis: 445, lagerbestand: 1800, ist_aktiv: true,
    ausgangsstoff_explosivstoffe: true, erklaerung_landwirt_erforderlich: true, erklaerung_landwirt_status: 'ausstehend',
  },
  {
    id: 'DUE-003', artikelnummer: 'DUE-003', name: 'Schwefelsaures Ammoniak', typ: 'Mineraldünger',
    hersteller: 'K+S', n_gehalt: 21, p_gehalt: 0, k_gehalt: 0, s_gehalt: 24, mg_gehalt: 0,
    dmv_nummer: 'DMV-2024-003', eu_zulassung: 'EU-2024-003', ablauf_zulassung: '2026-08-15',
    gefahrstoff_klasse: 'Reizend', wassergefaehrdend: true, lagerklasse: 'WGK 1',
    kultur_typ: 'Raps', dosierung_min: 100, dosierung_max: 200, zeitpunkt: 'Herbst',
    ek_preis: 295, vk_preis: 355, lagerbestand: 950, ist_aktiv: true,
    ausgangsstoff_explosivstoffe: true, erklaerung_landwirt_erforderlich: true, erklaerung_landwirt_status: 'geprueft',
  },
]

const fallbackPSM: PSM[] = [
  { id: '1', mittel: 'Roundup PowerFlex', wirkstoff: 'Glyphosat 480 g/l', kulturen: ['Getreide', 'Mais', 'Raps'], zulassungBis: '2026-12-31', status: 'aktiv', erklaerungLandwirtStatus: null },
  { id: '2', mittel: 'Fungisan Pro', wirkstoff: 'Tebuconazol 250 g/l', kulturen: ['Getreide', 'Raps'], zulassungBis: '2025-06-30', status: 'auslaufend', erklaerungLandwirtStatus: null },
]

const fallbackKunden: Kunde[] = [
  { id: 'k1', name: 'Schmidt Landwirtschaft GbR', betriebsnummer: 'DE-NI-030012', bundesland: 'niedersachsen', schlagCount: 12, gesamtflaeche: 145.8 },
  { id: 'k2', name: 'Müller Agrar KG', betriebsnummer: 'DE-NI-030045', bundesland: 'niedersachsen', schlagCount: 8, gesamtflaeche: 89.3 },
  { id: 'k3', name: 'Bauer Hof Meier', betriebsnummer: 'DE-BY-094015', bundesland: 'bayern', schlagCount: 5, gesamtflaeche: 52.1 },
  { id: 'all', name: 'Alle Kunden', betriebsnummer: '', bundesland: '', schlagCount: 25, gesamtflaeche: 287.2 },
]

const fallbackSchlaege: Schlag[] = [
  { id: '1', name: 'Nordfeld 1', flik: 'DENILI0000012345', flaeche: 12.5, kultur: 'Winterweizen', vorkultur: 'Winterraps', kundeId: 'k1', kundeName: 'Schmidt Landwirtschaft GbR', gemeinde: 'Nordhausen', gemarkung: 'Nordheim', bodenart: 'Lehm', ackerzahl: 65, status: 'aktiv', letzteMassnahme: { datum: '2025-11-15', typ: 'Düngung' } },
  { id: '2', name: 'Südacker', flik: 'DENILI0000012346', flaeche: 8.3, kultur: 'Winterraps', vorkultur: 'Winterweizen', kundeId: 'k2', kundeName: 'Müller Agrar KG', gemeinde: 'Südhausen', gemarkung: 'Südfeld', bodenart: 'Sandig-Lehm', ackerzahl: 55, status: 'aktiv', letzteMassnahme: { datum: '2025-11-10', typ: 'PSM-Behandlung' } },
  { id: '3', name: 'Wiesengrund', flik: 'DENILI0000012347', flaeche: 15.2, kultur: 'Silomais', vorkultur: 'Wintergerste', kundeId: 'k1', kundeName: 'Schmidt Landwirtschaft GbR', gemeinde: 'Nordhausen', gemarkung: 'Wiesenau', bodenart: 'Lehm-Ton', ackerzahl: 70, status: 'aktiv' },
  { id: '4', name: 'Bergacker', flik: 'DEBYLI0000098765', flaeche: 10.5, kultur: 'Wintergerste', vorkultur: 'Kartoffeln', kundeId: 'k3', kundeName: 'Bauer Hof Meier', gemeinde: 'Bergdorf', gemarkung: 'Am Berg', bodenart: 'Sandig', ackerzahl: 45, status: 'aktiv' },
  { id: '5', name: 'Stilllegungsfläche', flaeche: 3.2, kultur: 'Brache', kundeId: 'k1', kundeName: 'Schmidt Landwirtschaft GbR', gemeinde: 'Nordhausen', status: 'stillgelegt' },
]

// ── Dünger Hooks ───────────────────────────────────────────────────────

export function useDuenger(filters?: { search?: string; typ?: string; hersteller?: string }) {
  return useQuery({
    queryKey: [...agrarKeys.duenger(), filters],
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.search) params.append('search', filters.search)
        if (filters?.typ) params.append('typ', filters.typ)
        if (filters?.hersteller) params.append('hersteller', filters.hersteller)

        const response = await apiClient.get<{ items: Duenger[]; total: number }>(
          `/api/v1/agrar/duenger?${String(params)}`
        )
        if (response.data?.items?.length) return response.data
      } catch {
        // API not available – use fallback
      }
      let items = [...fallbackDuenger]
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(d =>
          d.name.toLowerCase().includes(s) ||
          d.artikelnummer.toLowerCase().includes(s) ||
          d.hersteller.toLowerCase().includes(s)
        )
      }
      if (filters?.typ) items = items.filter(d => d.typ === filters.typ)
      if (filters?.hersteller) items = items.filter(d => d.hersteller === filters.hersteller)
      return { items, total: items.length }
    },
    staleTime: 2 * 60 * 1000,
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

// ── PSM Hooks ──────────────────────────────────────────────────────────

export function usePSM(filters?: { search?: string }) {
  return useQuery({
    queryKey: [...agrarKeys.psm(), filters],
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.search) params.append('search', filters.search)

        const response = await apiClient.get<{ items: PSM[]; total: number }>(
          `/api/v1/agrar/psm?${String(params)}`
        )
        if (response.data?.items?.length) return response.data
      } catch {
        // API not available – use fallback
      }
      let items = [...fallbackPSM]
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(p =>
          p.mittel.toLowerCase().includes(s) ||
          p.wirkstoff.toLowerCase().includes(s)
        )
      }
      return { items, total: items.length }
    },
    staleTime: 2 * 60 * 1000,
  })
}

// ── Schlagkartei Hooks ─────────────────────────────────────────────────

export function useAgrarKunden() {
  return useQuery({
    queryKey: agrarKeys.kunden(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: Kunde[] }>('/api/v1/agrar/kunden')
        if (response.data?.items?.length) return response.data.items
      } catch {
        // API not available – use fallback
      }
      return fallbackKunden
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useSchlaege(kundeId?: string) {
  return useQuery({
    queryKey: agrarKeys.schlaege(kundeId),
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (kundeId && kundeId !== 'all') params.append('kunde_id', kundeId)

        const response = await apiClient.get<{ items: Schlag[] }>(
          `/api/v1/agrar/schlaege?${String(params)}`
        )
        if (response.data?.items?.length) return response.data.items
      } catch {
        // API not available – use fallback
      }
      return fallbackSchlaege
    },
    staleTime: 2 * 60 * 1000,
  })
}

// ── Extended Types ────────────────────────────────────────────────────

export type Aussaat = { id: string; schlag: string; kultur: string; sorte: string; datum: string; flaeche: number; saatmenge: number; status: 'geplant' | 'ausgesaet' | 'aufgelaufen' }
export type Bodenprobe = { id: string; schlag: string; datum: string; labor: string; n: number; p: number; k: number; ph: number; status: 'beauftragt' | 'analysiert' | 'abgeschlossen' }
export type DuengerKomponente = { id: string; name: string; typ: string; n_gehalt: number; p_gehalt: number; k_gehalt: number; s_gehalt: number; mg_gehalt: number; preis_pro_tonne: number; verfuegbar: number }
export type Ernte = { id: string; schlag: string; kultur: string; datum: string; menge: number; ertrag: number; status: 'geplant' | 'laufend' | 'abgeschlossen' }
export type Massnahme = { id: string; datum: string; uhrzeit: string; schlagId: string; schlagName: string; kundeId: string; kundeName: string; typ: string; mittel: string; menge: number; einheit: string; flaeche: number; anwender: string; geraet: string; compliant: boolean; exportiert: boolean }
export type Kultur = { id: string; name: string; kategorie: string; flaeche: number; ertrag: number; preis: number; deckungsbeitrag: number }
export type PSMAuflage = { id: string; psm_id: string; psm_name: string; auflage_typ: string; beschreibung: string; prioritaet: 'hoch' | 'mittel' | 'niedrig'; status: 'offen' | 'erfuellt' | 'ueberfaellig'; faellig_am: string; zugewiesen_an: string; compliance_status: 'ok' | 'warning' | 'critical' }
export type Schadbild = { id: string; name: string; beschreibung: string; schwere: 'gering' | 'mittel' | 'hoch'; kultur: string; saison: string }
export type WirkstoffGruppe = { id: string; name: string; wirkstoffe: string[]; resistenzRisiko: 'gering' | 'mittel' | 'hoch'; letzteAnwendung: string; rotationsEmpfehlung: string }
export type PSMSachkundeNachweis = { id: string; kunde: string; kundennr: string; nachweisNr: string; ausstellungsdatum: string; gueltigBis: string; ausstellendeStelle: string; status: 'gueltig' | 'ablaufend' | 'abgelaufen'; complianceStatus?: string }
export type WasserschutzZone = { id: string; name: string; typ: string; zone: string; koordinaten: { lat: number; lng: number }; radius: number; restriktionsgrad: 'niedrig' | 'mittel' | 'hoch' }
export type Sorte = { id: string; name: string; art: string; zuechter: string; zulassung: string; eigenschaft: string[]; status: 'aktiv' | 'auslaufend' }

// ── Extended Fallback Data ────────────────────────────────────────────

const fallbackAussaaten: Aussaat[] = [
  { id: '1', schlag: 'Nordfeld 1', kultur: 'Weizen', sorte: 'Asano', datum: '2025-10-15', flaeche: 12.5, saatmenge: 2250, status: 'ausgesaet' },
  { id: '2', schlag: 'Südacker', kultur: 'Raps', sorte: 'Mentor', datum: '2025-08-20', flaeche: 8.3, saatmenge: 332, status: 'aufgelaufen' },
]

const fallbackBodenproben: Bodenprobe[] = [
  { id: '1', schlag: 'Nordfeld 1', datum: '2025-09-15', labor: 'Labor Nord', n: 12.5, p: 18.2, k: 25.8, ph: 6.8, status: 'analysiert' },
  { id: '2', schlag: 'Südacker', datum: '2025-09-20', labor: 'Lufa', n: 10.3, p: 14.5, k: 22.1, ph: 7.1, status: 'abgeschlossen' },
]

const fallbackKomponenten: DuengerKomponente[] = [
  { id: 'DUE-001', name: 'Kalkammonsalpeter', typ: 'Mineraldünger', n_gehalt: 27.0, p_gehalt: 0, k_gehalt: 0, s_gehalt: 0, mg_gehalt: 0, preis_pro_tonne: 450, verfuegbar: 1500 },
  { id: 'DUE-002', name: 'Superphosphat', typ: 'Mineraldünger', n_gehalt: 0, p_gehalt: 18.0, k_gehalt: 0, s_gehalt: 12, mg_gehalt: 0, preis_pro_tonne: 380, verfuegbar: 800 },
  { id: 'DUE-003', name: 'Kornkali', typ: 'Mineraldünger', n_gehalt: 0, p_gehalt: 0, k_gehalt: 40.0, s_gehalt: 6, mg_gehalt: 4, preis_pro_tonne: 420, verfuegbar: 1200 },
]

const fallbackErnten: Ernte[] = [
  { id: '1', schlag: 'Nordfeld 1', kultur: 'Weizen', datum: '2025-08-15', menge: 150, ertrag: 12.0, status: 'abgeschlossen' },
  { id: '2', schlag: 'Südacker', kultur: 'Raps', datum: '2025-07-25', menge: 33.2, ertrag: 4.0, status: 'abgeschlossen' },
]

const fallbackMassnahmen: Massnahme[] = [
  { id: '1', datum: '2025-11-15', uhrzeit: '08:30', schlagId: '1', schlagName: 'Nordfeld 1', kundeId: 'k1', kundeName: 'Schmidt Landwirtschaft GbR', typ: 'Düngung', mittel: 'ENTEC 26', menge: 350, einheit: 'kg/ha', flaeche: 12.5, anwender: 'Max Mustermann', geraet: 'Amazone ZA-M 1500', compliant: true, exportiert: false },
  { id: '2', datum: '2025-11-10', uhrzeit: '10:00', schlagId: '2', schlagName: 'Südacker', kundeId: 'k2', kundeName: 'Müller Agrar KG', typ: 'PSM-Behandlung', mittel: 'Folicur', menge: 1.0, einheit: 'l/ha', flaeche: 8.3, anwender: 'Peter Weber', geraet: 'Horsch Leeb 6 GS', compliant: true, exportiert: true },
]

const fallbackKulturen: Kultur[] = [
  { id: '1', name: 'Weizen (Winterweizen)', kategorie: 'Getreide', flaeche: 65.5, ertrag: 7.8, preis: 220, deckungsbeitrag: 850 },
  { id: '2', name: 'Raps (Winterraps)', kategorie: 'Ölsaaten', flaeche: 28.3, ertrag: 4.0, preis: 480, deckungsbeitrag: 680 },
  { id: '3', name: 'Silomais', kategorie: 'Mais', flaeche: 22.0, ertrag: 45.0, preis: 38, deckungsbeitrag: 520 },
]

const fallbackAuflagen: PSMAuflage[] = [
  { id: '1', psm_id: 'PSM-001', psm_name: 'Roundup PowerFlex', auflage_typ: 'NW', beschreibung: 'Abstand zu Gewässern mind. 5m', prioritaet: 'hoch', status: 'offen', faellig_am: '2026-03-15', zugewiesen_an: 'Max Mustermann', compliance_status: 'warning' },
]

const fallbackSchadbilder: Schadbild[] = [
  { id: '1', name: 'Gelbrost am Weizen', beschreibung: 'Gelbe Streifen auf Blättern', schwere: 'mittel', kultur: 'Weizen', saison: 'Frühjahr' },
  { id: '2', name: 'Rapsglanzkäfer', beschreibung: 'Fraßschäden an Blütenknospen', schwere: 'hoch', kultur: 'Raps', saison: 'Frühjahr' },
]

const fallbackResistenz: WirkstoffGruppe[] = [
  { id: '1', name: 'Azole', wirkstoffe: ['Tebuconazol', 'Prothioconazol', 'Epoxiconazol'], resistenzRisiko: 'hoch', letzteAnwendung: '2025-08-15', rotationsEmpfehlung: '3 Jahre Pause empfohlen' },
  { id: '2', name: 'Strobilurine', wirkstoffe: ['Azoxystrobin', 'Pyraclostrobin'], resistenzRisiko: 'mittel', letzteAnwendung: '2025-06-20', rotationsEmpfehlung: 'Jährlich wechseln' },
]

const fallbackSachkunde: PSMSachkundeNachweis[] = [
  { id: '1', kunde: 'Landwirtschaft Müller', kundennr: 'K-10023', nachweisNr: 'SK-PSM-2022-4567', ausstellungsdatum: '2022-03-15', gueltigBis: '2025-03-15', ausstellendeStelle: 'LWK Niedersachsen', status: 'ablaufend', complianceStatus: 'warning' },
]

const fallbackWasserschutz: WasserschutzZone[] = [
  { id: '1', name: 'Trinkwasserschutzgebiet Nord', typ: 'Trinkwasserschutzgebiet', zone: 'Zone II', koordinaten: { lat: 52.52, lng: 13.4 }, radius: 5000, restriktionsgrad: 'hoch' },
]

const fallbackSorten: Sorte[] = [
  { id: '1', name: 'Asano', art: 'Weizen', zuechter: 'KWS', zulassung: '2020', eigenschaft: ['Winterhart', 'Ertragsstark'], status: 'aktiv' },
  { id: '2', name: 'Mentor', art: 'Raps', zuechter: 'DSV', zulassung: '2019', eigenschaft: ['Trockenresistent', 'Ölreich'], status: 'aktiv' },
]

// ── Extended Query Keys ───────────────────────────────────────────────

export const agrarExtraKeys = {
  aussaaten: () => [...agrarKeys.all, 'aussaaten'] as const,
  bodenproben: () => [...agrarKeys.all, 'bodenproben'] as const,
  mischungen: () => [...agrarKeys.all, 'mischungen'] as const,
  ernten: () => [...agrarKeys.all, 'ernten'] as const,
  massnahmen: () => [...agrarKeys.all, 'massnahmen'] as const,
  kulturen: () => [...agrarKeys.all, 'kulturen'] as const,
  auflagen: () => [...agrarKeys.all, 'auflagen'] as const,
  schadbilder: () => [...agrarKeys.all, 'schadbilder'] as const,
  resistenz: () => [...agrarKeys.all, 'resistenz'] as const,
  sachkundeRegister: () => [...agrarKeys.all, 'sachkunde'] as const,
  wasserschutz: () => [...agrarKeys.all, 'wasserschutz'] as const,
  sorten: () => [...agrarKeys.all, 'sorten'] as const,
}

// ── Extended Hooks ────────────────────────────────────────────────────

export function useAussaaten() {
  return useQuery({ queryKey: agrarExtraKeys.aussaaten(), queryFn: async () => { try { const r = await apiClient.get<Aussaat[]>('/api/v1/agrar/aussaaten'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackAussaaten }, staleTime: 2 * 60 * 1000 })
}

export function useBodenproben() {
  return useQuery({ queryKey: agrarExtraKeys.bodenproben(), queryFn: async () => { try { const r = await apiClient.get<Bodenprobe[]>('/api/v1/agrar/bodenproben'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackBodenproben }, staleTime: 5 * 60 * 1000 })
}

export function useDuengerKomponenten() {
  return useQuery({ queryKey: agrarExtraKeys.mischungen(), queryFn: async () => { try { const r = await apiClient.get<DuengerKomponente[]>('/api/v1/agrar/duenger/komponenten'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackKomponenten }, staleTime: 5 * 60 * 1000 })
}

export function useErnten() {
  return useQuery({ queryKey: agrarExtraKeys.ernten(), queryFn: async () => { try { const r = await apiClient.get<Ernte[]>('/api/v1/agrar/ernten'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackErnten }, staleTime: 2 * 60 * 1000 })
}

export function useMassnahmen() {
  return useQuery({ queryKey: agrarExtraKeys.massnahmen(), queryFn: async () => { try { const r = await apiClient.get<Massnahme[]>('/api/v1/agrar/massnahmen'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackMassnahmen }, staleTime: 2 * 60 * 1000 })
}

export function useKulturen() {
  return useQuery({ queryKey: agrarExtraKeys.kulturen(), queryFn: async () => { try { const r = await apiClient.get<Kultur[]>('/api/v1/agrar/kulturpflanzen'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackKulturen }, staleTime: 5 * 60 * 1000 })
}

export function usePSMAuflagen() {
  return useQuery({ queryKey: agrarExtraKeys.auflagen(), queryFn: async () => { try { const r = await apiClient.get<PSMAuflage[]>('/api/v1/agrar/psm/auflagen'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackAuflagen }, staleTime: 2 * 60 * 1000 })
}

export function useSchadbilder() {
  return useQuery({ queryKey: agrarExtraKeys.schadbilder(), queryFn: async () => { try { const r = await apiClient.get<Schadbild[]>('/api/v1/agrar/psm/schadbilder'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackSchadbilder }, staleTime: 5 * 60 * 1000 })
}

export function useWirkstoffGruppen() {
  return useQuery({ queryKey: agrarExtraKeys.resistenz(), queryFn: async () => { try { const r = await apiClient.get<WirkstoffGruppe[]>('/api/v1/agrar/psm/resistenz'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackResistenz }, staleTime: 5 * 60 * 1000 })
}

export function usePSMSachkundeRegister() {
  return useQuery({ queryKey: agrarExtraKeys.sachkundeRegister(), queryFn: async () => { try { const r = await apiClient.get<PSMSachkundeNachweis[]>('/api/v1/agrar/psm/sachkunde'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackSachkunde }, staleTime: 5 * 60 * 1000 })
}

export function useWasserschutzZonen() {
  return useQuery({ queryKey: agrarExtraKeys.wasserschutz(), queryFn: async () => { try { const r = await apiClient.get<WasserschutzZone[]>('/api/v1/agrar/psm/wasserschutz'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackWasserschutz }, staleTime: 10 * 60 * 1000 })
}

export function useSorten() {
  return useQuery({ queryKey: agrarExtraKeys.sorten(), queryFn: async () => { try { const r = await apiClient.get<Sorte[]>('/api/v1/agrar/saatgut/sorten'); if (r.data?.length) return r.data } catch { /* fallback to mock data */ } return fallbackSorten }, staleTime: 5 * 60 * 1000 })
}
