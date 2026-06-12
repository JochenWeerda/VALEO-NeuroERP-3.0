/**
 * Logistik Frachtkosten / Tarife (domain_logistics.freight_tariffs) — API aus logistics_freight.py
 */
import { apiClient } from '../api-client'

export type FreightTariffRow = Record<string, unknown> & {
  id?: string
  carrier_id?: string | null
  zone_from?: string | null
  zone_to?: string | null
  price_per_100kg?: number
  min_charge?: number
  tenant_id?: string | null
  status?: string | null
  storno_ts?: string | null
  storno_grund?: string | null
}

export type FreightSimulateResult = {
  carrier_id: string
  freight_cost_eur: number
  tariff_id?: string
  zone?: string
  calculation_details?: Record<string, unknown>
}

export async function listFreightTariffs(): Promise<FreightTariffRow[]> {
  const { data } = await apiClient.get<FreightTariffRow[]>('/api/v1/logistik/freight-tariffs')
  return Array.isArray(data) ? data : []
}

/** Mandanten-Tarif stornieren (soft); globale Tarife → 403. */
export async function cancelFreightTariff(
  tariffId: string,
  body?: { grund?: string },
): Promise<FreightTariffRow> {
  const { data } = await apiClient.post<FreightTariffRow>(
    `/api/v1/logistik/freight-tariffs/${encodeURIComponent(tariffId)}/cancel`,
    body ?? {},
  )
  return data as FreightTariffRow
}

/** GET simulate — keine Buchung (siehe Backend ``simulate_freight``). */
export async function simulateFreightCost(params: {
  carrier_id: string
  distance_km: number
  weight_kg: number
  postal_code_from: string
  postal_code_to: string
}): Promise<FreightSimulateResult> {
  const { data } = await apiClient.get<FreightSimulateResult>('/api/v1/logistik/freight-cost/simulate', {
    params,
  })
  return data as FreightSimulateResult
}
