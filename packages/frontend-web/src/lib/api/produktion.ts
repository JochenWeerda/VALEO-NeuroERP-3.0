/**
 * Produktion – Mischfutter API Hooks (FEED-CHAIN-002)
 * Verfuegbarkeit, Rezepte, Produktionsauftraege inkl. Lifecycle + Trace.
 * Verträge: app/api/v1/endpoints/produktion_mischfutter.py
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────────

export type KomponenteVerfuegbarkeit = {
  id: string
  name: string
  verfuegbar_t: number
  einheit: string
  min_bestand_t?: number | null
  unter_minimum?: boolean
}

export type RezeptKomponente = {
  komponente_name: string
  anteil: number
  einzelfutter_id?: string | null
}

export type Rezept = {
  id: string
  name: string
  rezept_code: string
  tierart: string
  protein_ziel?: number | null
  energie_ziel?: number | null
  komponenten: RezeptKomponente[]
}

export type VerbrauchRow = {
  einzelfutter_id?: string | null
  name: string
  anteil: number
  menge_t: number
}

export type ProduktionsauftragStatus =
  | 'erstellt'
  | 'freigegeben'
  | 'in_produktion'
  | 'fertig'
  | 'storniert'

export type Produktionsauftrag = {
  id: string
  chargen_id: string
  rezept_id: string | null
  rezept_name: string
  menge_t: number
  status: ProduktionsauftragStatus
  bestands_abzug_erfolgt: boolean
  charge_id?: string | null
  verbrauch?: VerbrauchRow[] | null
  created_at?: string | null
}

export type FeedChainTrace = {
  auftrag: {
    id: string
    chargen_id: string
    rezept_id: string | null
    rezept_name: string
    menge_t: number
    status: string
    freigegeben_am?: string | null
    fertig_am?: string | null
  }
  charge: {
    id: string
    chargen_id: string
    status: string
    qualitaetsstatus: string
    lagerort: string
    menge: number
    rohstoffe: Array<Record<string, unknown>>
  } | null
  komponenten: VerbrauchRow[]
  kette_geschlossen: boolean
}

/** FEED-CHAIN-004: Einzelfutter ↔ domain_inventory.articles */
export type FeedInventoryLinkRow = {
  id: string
  artikel_nummer: string
  name: string
  inventory_article_id?: string | null
  verfuegbar_t: number
  inv_article_number?: string | null
}

export type FeedInventoryLinksResponse = {
  items: FeedInventoryLinkRow[]
  total: number
  mapped_count: number
  unmapped_count: number
}

// ── Hooks ──────────────────────────────────────────────────────────────────

// Achtung: kein ``initialData: []`` — das zählt als frischer Fetch und unterdrückt
// zusammen mit ``staleTime`` den ersten echten Request (Select blieb dauerhaft leer).
const EMPTY: never[] = []

export function useMischfutterVerfuegbarkeit() {
  const query = useQuery({
    queryKey: ['produktion', 'mischfutter', 'verfuegbarkeit'],
    queryFn: async () =>
      (await apiClient.get<KomponenteVerfuegbarkeit[]>('/api/v1/produktion/mischfutter/verfuegbarkeit')).data,
    staleTime: 60 * 1000,
  })
  return { ...query, data: query.data ?? (EMPTY as KomponenteVerfuegbarkeit[]) }
}

export function useMischfutterRezepte() {
  const query = useQuery({
    queryKey: ['produktion', 'mischfutter', 'rezepte'],
    queryFn: async () =>
      (await apiClient.get<Rezept[]>('/api/v1/produktion/mischfutter/rezepte')).data,
    staleTime: 5 * 60 * 1000,
  })
  return { ...query, data: query.data ?? (EMPTY as Rezept[]) }
}

export function useProduktionsauftraege(status?: ProduktionsauftragStatus) {
  const query = useQuery({
    queryKey: ['produktion', 'mischfutter', 'auftraege', status ?? 'alle'],
    queryFn: async () =>
      (
        await apiClient.get<Produktionsauftrag[]>('/api/v1/produktion/mischfutter/auftraege', {
          params: status ? { status } : undefined,
        })
      ).data,
    staleTime: 15 * 1000,
    refetchOnWindowFocus: false,
  })
  return { ...query, data: query.data ?? (EMPTY as Produktionsauftrag[]) }
}

export function useCreateProduktionsauftrag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: {
      rezept_id: string
      menge_t: number
      chargen_id?: string
      bemerkung?: string
    }) =>
      (await apiClient.post<Produktionsauftrag>('/api/v1/produktion/mischfutter/auftrag', payload)).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['produktion', 'mischfutter', 'auftraege'] })
    },
  })
}

/** Statusübergang; bei ``freigegeben`` zieht das Backend Bestand ab (Snapshot),
 * bei ``fertig`` entsteht die Fertigwaren-Charge (FEED-CHAIN-001). */
export async function updateProduktionsauftragStatus(
  auftragId: string,
  status: Exclude<ProduktionsauftragStatus, 'erstellt'>,
  freigegebenVon?: string,
): Promise<Produktionsauftrag> {
  const res = await apiClient.patch<Produktionsauftrag>(
    `/api/v1/produktion/mischfutter/auftrag/${encodeURIComponent(auftragId)}/status`,
    { status, freigegeben_von: freigegebenVon ?? null },
  )
  return res.data
}

/** Belegkette Auftrag ↔ Charge ↔ Komponenten (Auftrag-ID oder chargen_id). */
export async function fetchProduktionsTrace(ref: string): Promise<FeedChainTrace> {
  const res = await apiClient.get<FeedChainTrace>(
    `/api/v1/produktion/mischfutter/auftraege/${encodeURIComponent(ref)}/trace`,
  )
  return res.data
}

export function useFeedInventoryLinks() {
  return useQuery({
    queryKey: ['produktion', 'mischfutter', 'inventory-links'],
    queryFn: async () =>
      (await apiClient.get<FeedInventoryLinksResponse>('/api/v1/produktion/mischfutter/inventory-links')).data,
    staleTime: 30 * 1000,
  })
}

/** Legt fehlenden Lagerartikel an oder verknüpft per artikel_nummer (idempotent). */
export function useEnsureFeedInventoryLink() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (einzelfutterId: string) =>
      (
        await apiClient.post<{ ok: boolean; article_id: string; created?: boolean }>(
          `/api/v1/produktion/mischfutter/inventory-links/${encodeURIComponent(einzelfutterId)}/ensure`,
        )
      ).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['produktion', 'mischfutter', 'inventory-links'] })
    },
  })
}
