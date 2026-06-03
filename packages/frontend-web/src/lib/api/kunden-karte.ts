import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/** CRM-Kundenkarte: alle Kunden als GeoJSON-POIs. */

export type KundenGeoJSON = {
  type: 'FeatureCollection'
  features: Array<{
    type: 'Feature'
    geometry: { type: 'Point'; coordinates: [number, number] }
    properties: { kunden_nr: string; name: string | null; plz: string | null; ort: string | null; typ: string; verbrueckt: boolean }
  }>
}

export function useKundenKarte(typ?: string) {
  return useQuery({
    queryKey: ['kunden-karte', typ ?? 'alle'],
    queryFn: async () => {
      const res = await apiClient.get<KundenGeoJSON>('/api/v1/crm/kunden-karte/map', {
        params: typ ? { typ } : {},
      })
      return res.data
    },
    staleTime: 60_000,
  })
}
