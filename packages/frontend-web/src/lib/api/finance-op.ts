import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Offene-Posten-Cockpit / OP-Aging (DOM-FIN-004): offene Beträge mit Fälligkeit,
 * Aging-Bucket, Mahnstufe und Skonto-Fenster. Backend: app/api/v1/endpoints/finance_op.py
 */

export type OpItem = {
  rechnungsnr: string | null
  rechnungsdatum: string | null
  faelligkeit: string | null
  konto_typ: string | null
  partner: string | null
  waehrung: string
  betrag: number | null
  offen: number | null
  bucket: string
  tage_ueberfaellig: number
  ueberfaellig: boolean
  mahnstufe: number
  skonto_aktiv: boolean
  skonto_prozent: number | null
  skonto_bis: string | null
}

export type OpBucket = { bucket: string; anzahl: number; summe: number }

export type OpResponse = {
  items: OpItem[]
  summary: { anzahl: number; summe_offen: number; summe_ueberfaellig: number; buckets: OpBucket[] }
}

export function useOffenePosten(typ = 'alle') {
  return useQuery({
    queryKey: ['finance-op', typ],
    queryFn: async () => {
      const res = await apiClient.get<OpResponse>('/api/v1/finance/offene-posten', { params: { typ } })
      return res.data ?? { items: [], summary: { anzahl: 0, summe_offen: 0, summe_ueberfaellig: 0, buckets: [] } }
    },
  })
}
