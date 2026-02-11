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
