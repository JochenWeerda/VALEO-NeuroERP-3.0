import { apiClient } from '@/lib/api-client'

export type MobileEventType =
  | 'delivery_confirmation'
  | 'inventory_count'
  | 'qs_probe_result'
  | 'harvest_acceptance'
  | 'silo_transfer'
  | 'generic'

export type MobileEvent = {
  event_type: MobileEventType
  payload: Record<string, unknown>
  idempotency_key?: string
}

export type SyncBatch = {
  device_id: string
  events: MobileEvent[]
}

export type SyncResult = {
  received: number
  queued: number
  rejected: number
  results: Array<{ idempotency_key: string; event_id?: string; status: string; reason?: string }>
}

export type QueueItem = {
  id: string
  tenant_id: string
  device_id: string
  event_type: string
  payload: Record<string, unknown>
  sync_status: 'pending' | 'processing' | 'done' | 'failed'
  error_message: string | null
  idempotency_key: string | null
  created_at: string
  processed_at: string | null
}

export type ProcessResult = {
  processed: number
  failed: number
  skipped: number
  total: number
}

export async function syncEvents(batch: SyncBatch): Promise<SyncResult> {
  return (await apiClient.post<SyncResult>('/api/v1/mobile/sync-events', batch)).data
}

export async function processQueue(limit = 50): Promise<ProcessResult> {
  return (await apiClient.post<ProcessResult>(`/api/v1/mobile/sync-process?limit=${limit}`)).data
}

export async function getQueue(status?: string, limit = 100): Promise<{ items: QueueItem[]; count: number }> {
  const p = new URLSearchParams()
  if (status) p.set('status', status)
  p.set('limit', String(limit))
  const qs = p.toString()
  return (await apiClient.get<{ items: QueueItem[]; count: number }>(`/api/v1/mobile/sync-queue?${qs}`)).data
}
