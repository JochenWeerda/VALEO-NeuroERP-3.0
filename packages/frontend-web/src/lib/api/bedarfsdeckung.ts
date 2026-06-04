import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Bedarfsdeckungs-Cockpit (Durchdringungs-CRM): objektiver Jahresbedarf je
 * Produktgruppe vs. Ist-Bezug (12 M) → Deckungsgrad, Lücke, Next-Best-Offer.
 * „Die Lücke ist das Vertriebsobjekt."
 */

export type Sparte = 'milchvieh' | 'ackerbau'

export type ProduktgruppeDeckung = {
  key: string
  label: string
  sparte: Sparte
  bedarf_jahr_eur: number
  ist_12m_eur: number
  deckung_pct: number
  luecke_eur: number
  ziel_anteil: number
  realistische_luecke_eur: number
  geschuetzte_luecke_eur: number
  score: number
  aktion: 'Einstieg' | 'Cross-Sell' | 'Ausbauen' | 'Halten'
  kaeufergruppe: string
  kaeufergruppe_label: string
  kaeufergruppe_eigen: boolean
  letzter_bezug: string | null
  quelle: string
}

export type Kaeufergruppe = {
  group: string
  label: string
  confidence: number
  reason: string | null
  source: string
  ansatz: string
  ziel_anteil_min: number
  ziel_anteil_max: number
}

export type NextBestOffer = {
  produktgruppe: string
  label: string
  sparte: Sparte
  luecke_eur: number
  realistische_luecke_eur: number
  score: number
  empfehlung: string
}

export type BedarfsdeckungCockpit = {
  kunden_nr: string
  name: string
  plz: string | null
  ort: string | null
  sparten: Sparte[]
  herd_size_kuehe: number
  milchmenge_l_jahr: number
  ecm_kg: number | null
  kraftfutter_t_jahr: number
  ackerflaeche_ha: number
  bedarf_jahr_eur_gesamt: number
  ist_12m_eur_gesamt: number
  luecke_eur_gesamt: number
  realistische_luecke_eur_gesamt: number
  geschuetzte_luecke_eur_gesamt: number
  deckung_pct_gesamt: number
  kaeufergruppe: Kaeufergruppe
  produktgruppen: ProduktgruppeDeckung[]
  next_best_offer: NextBestOffer | null
}

export type PipelineEntry = {
  kunden_nr: string
  name: string
  plz: string | null
  ort: string | null
  sparten: Sparte[]
  herd_size_kuehe: number
  ackerflaeche_ha: number
  deckung_pct_gesamt: number
  luecke_eur_gesamt: number
  realistische_luecke_eur_gesamt: number
  kaeufergruppe: string
  kaeufergruppe_label: string
  top_produktgruppe: string
  top_sparte: Sparte
  top_luecke_eur: number
  top_score: number
  empfehlung: string
}

export function useBedarfsdeckung(kundenNr: string | undefined) {
  return useQuery({
    queryKey: ['bedarfsdeckung', kundenNr],
    queryFn: async () => {
      const res = await apiClient.get<BedarfsdeckungCockpit>(`/api/v1/crm/bedarfsdeckung/${encodeURIComponent(kundenNr ?? '')}`)
      return res.data
    },
    enabled: Boolean(kundenNr?.trim()),
  })
}

export function usePipeline(limit = 100) {
  return useQuery({
    queryKey: ['bedarfsdeckung-pipeline', limit],
    queryFn: async () => {
      const res = await apiClient.get<PipelineEntry[]>('/api/v1/crm/bedarfsdeckung/pipeline', { params: { limit } })
      return Array.isArray(res.data) ? res.data : []
    },
    initialDataUpdatedAt: 0,
  })
}
