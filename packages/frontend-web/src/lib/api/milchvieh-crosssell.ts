import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/** Cross-Sell-Auswertung Milchvieh: Hygiene-Bedarf + Kraftfutter-Potenzial. */

export type ProduktgruppePotenzial = {
  key: string
  label: string
  eur_per_1000l: [number, number]
  eur_jahr_min: number
  eur_jahr_max: number
}

export type MilchviehCrossSellItem = {
  kunden_nr: string
  name: string | null
  plz: string | null
  ort: string | null
  herd_size_kuehe: number
  herd_size_group: string | null
  milch_kg: number | null
  ecm_kg: number | null
  milchmenge_l_jahr: number
  fett_pct: number | null
  eiw_pct: number | null
  zellzahl_tsd_ml: number | null
  zellzahl_quelle: string | null
  hygiene_bedarf: 'niedrig' | 'mittel' | 'hoch'
  hygiene_dipp_l_jahr: number
  kraftfutter_t_jahr_min: number
  kraftfutter_t_jahr_max: number
  crosssell_ziel_eur: number
  crosssell_adressierbar_eur_min: number
  crosssell_adressierbar_eur_max: number
  crosssell_gewinnbar_eur_min: number
  crosssell_gewinnbar_eur_max: number
  produktgruppen: ProduktgruppePotenzial[]
}

export type MilchviehCrossSellSummary = {
  kunden: number
  nach_hygiene_bedarf: Record<string, number>
  milchmenge_l_jahr_gesamt: number
  kraftfutter_t_jahr_gesamt_min: number
  kraftfutter_t_jahr_gesamt_max: number
  dippmittel_l_jahr_gesamt: number
  kf_g_je_kg_ecm: [number, number]
  crosssell_eur_jahr_adressierbar_min: number
  crosssell_eur_jahr_ziel: number
  crosssell_eur_jahr_adressierbar_max: number
  crosssell_eur_jahr_gewinnbar_min: number
  crosssell_eur_jahr_gewinnbar_max: number
  produktgruppen: ProduktgruppePotenzial[]
  crosssell_eur_je_1000l: {
    adressierbar: [number, number]
    ziel: number
    gewinnbar: [number, number]
  }
}

export type CrossSellFilter = {
  hygiene_bedarf?: string
  min_kuehe?: number
  sort?: 'kraftfutter' | 'hygiene' | 'umsatz'
}

export function useMilchviehCrossSell(filter: CrossSellFilter = {}) {
  return useQuery({
    queryKey: ['milchvieh-crosssell', filter],
    queryFn: async () => {
      const params: Record<string, string | number> = {}
      if (filter.hygiene_bedarf) params.hygiene_bedarf = filter.hygiene_bedarf
      if (filter.min_kuehe) params.min_kuehe = filter.min_kuehe
      if (filter.sort) params.sort = filter.sort
      const res = await apiClient.get<MilchviehCrossSellItem[]>(
        '/api/v1/agrar/milchvieh-crosssell',
        { params },
      )
      return Array.isArray(res.data) ? res.data : []
    },
    staleTime: 60_000,
  })
}

export function useMilchviehCrossSellSummary() {
  return useQuery({
    queryKey: ['milchvieh-crosssell', 'summary'],
    queryFn: async () => {
      const res = await apiClient.get<MilchviehCrossSellSummary>(
        '/api/v1/agrar/milchvieh-crosssell/summary',
      )
      return res.data
    },
    staleTime: 60_000,
  })
}

export type GeoJSONFeatureCollection = {
  type: 'FeatureCollection'
  features: Array<{
    type: 'Feature'
    geometry: { type: 'Point'; coordinates: [number, number] }
    properties: Record<string, string | number | null>
  }>
}

export function useMilchviehMap(filter: CrossSellFilter = {}) {
  return useQuery({
    queryKey: ['milchvieh-crosssell', 'map', filter],
    queryFn: async () => {
      const params: Record<string, string | number> = {}
      if (filter.hygiene_bedarf) params.hygiene_bedarf = filter.hygiene_bedarf
      if (filter.min_kuehe) params.min_kuehe = filter.min_kuehe
      const res = await apiClient.get<GeoJSONFeatureCollection>(
        '/api/v1/agrar/milchvieh-crosssell/map',
        { params },
      )
      return res.data
    },
    staleTime: 60_000,
  })
}
