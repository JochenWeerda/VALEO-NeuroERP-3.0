import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/agrar/rations-optimization/feeding/supply'

export interface FeedingSupplyProjection {
  plan_version_id: string
  plan_version_no: number
  group_id: string
  group_name: string
  feed_id: string
  feed_name: string
  daily_demand_kg: number
  horizon_days: number
  safety_pct: number
  gross_demand_kg: number
  stock_kg: number | null
  reach_days: number | null
  shortage_kg: number | null
  trade_unit_kg: number | null
  suggested_order_kg: number | null
  order_rounding_delta_kg: number | null
  status: 'sufficient' | 'critical' | 'unknown'
}

export interface ProcurementHandoff {
  id: string
  status: 'proposed'
  projection: FeedingSupplyProjection
  reason: string
  created_at: string
}

export async function createProcurementHandoff(
  projection: FeedingSupplyProjection,
  reason: string,
): Promise<ProcurementHandoff> {
  const response = await apiClient.post<ProcurementHandoff>(`${BASE}/procurement-handoffs`, {
    plan_version_id: projection.plan_version_id,
    feed_id: projection.feed_id,
    horizon_days: projection.horizon_days,
    safety_pct: projection.safety_pct,
    idempotency_key: `feeding-supply-${crypto.randomUUID()}`,
    reason,
  })
  return response.data
}
