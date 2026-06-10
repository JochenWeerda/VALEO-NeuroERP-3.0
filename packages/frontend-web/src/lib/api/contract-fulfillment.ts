import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kontrakt-Erfüllungsstand (DOM-CON-004): kontrahiert vs. abgerufen je Kontrakt.
 * Backend: app/api/v1/endpoints/contract_fulfillment.py
 */

export type ContractRow = {
  contract_no: string
  typ: string
  party_id: string | null
  einheit: string | null
  status: string | null
  valid_to: string | null
  menge_kontrakt: number | null
  abgerufen: number | null
  erfuellung_pct: number
  erfuellung_status: string
  ueberfaellig: boolean
}

export type ContractPosition = {
  position_no: number
  artikel: string | null
  bezeichnung: string | null
  menge_kontrakt: number | null
  abgerufen: number | null
  offen: number
  status: string
  erfuellung_pct: number
  abweichung: boolean
  is_matif: boolean
}

export type ContractDetail = {
  found: boolean
  detail?: string
  contract_no?: string
  contract_type?: string
  party_id?: string | null
  status?: string | null
  einheit?: string | null
  valid_from?: string | null
  valid_to?: string | null
  ueberfaellig?: boolean
  pricing?: { modell: string | null; praemie_typ: string | null; praemie_wert: number | null; mindestpreis: number | null; basis: string | null }
  positionen?: ContractPosition[]
  luecken?: Array<{ schwere: string; text: string }>
  summary?: { menge_kontrakt: number; abgerufen: number; offen: number; erfuellung_pct: number; status: string; offene_luecken: number }
}

export function useContracts(typ = 'alle') {
  return useQuery({
    queryKey: ['contract-fulfillment', 'list', typ],
    queryFn: async () => {
      const res = await apiClient.get<{ items: ContractRow[] }>('/api/v1/contracts/fulfillment/list', { params: { typ } })
      return res.data?.items ?? []
    },
  })
}

export function useContractDetail(kontrakt: string | null) {
  return useQuery({
    queryKey: ['contract-fulfillment', 'detail', kontrakt],
    enabled: !!kontrakt,
    queryFn: async () => {
      const res = await apiClient.get<ContractDetail>('/api/v1/contracts/fulfillment', { params: { kontrakt } })
      return res.data
    },
  })
}
