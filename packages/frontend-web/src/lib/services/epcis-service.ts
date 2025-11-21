/**
 * EPCIS Service
 * API service for EPCIS (Electronic Product Code Information Services) events
 */

import { apiClient } from '../api-client'

export interface EpcisEvent {
  id: string
  tenant_id: string
  event_type: string
  event_time: string
  biz_step?: string | null
  read_point?: string | null
  lot_id?: string | null
  sku?: string | null
  quantity?: number | null
  extensions?: Record<string, any> | null
  created_at: string
}

export interface EpcisEventsResponse {
  items: EpcisEvent[]
  total: number
}

export interface CreateEpcisEvent {
  event_type: 'ObjectEvent' | 'AggregationEvent' | 'TransformationEvent' | 'TransactionEvent'
  event_time?: string
  biz_step?: string
  read_point?: string
  lot_id?: string
  sku?: string
  quantity?: number
  extensions?: Record<string, any>
  idempotency_key?: string
}

export const epcisService = {
  async listEpcisEvents(params?: { limit?: number }, tenantId?: string) {
    const headers = tenantId ? { 'X-Tenant-Id': tenantId } : undefined
    const res = await apiClient.get<EpcisEventsResponse>('/api/v1/inventory/epcis/events', {
      params,
      headers
    })
    return res.data
  },

  async createEpcisEvent(payload: CreateEpcisEvent, tenantId?: string) {
    const headers = tenantId ? { 'X-Tenant-Id': tenantId } : undefined
    const res = await apiClient.post<EpcisEvent>('/api/v1/inventory/epcis/events', payload, { headers })
    return res.data
  }
}