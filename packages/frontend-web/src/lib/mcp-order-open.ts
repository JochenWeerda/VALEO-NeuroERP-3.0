/**
 * Deep-Link helper for MCP tool `sales.order.status`.
 * Only relative `/sales/order-editor/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const ORDER_ROUTE_RE = /^\/sales\/order-editor\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type OrderOpenResult = {
  order_id: string
  auftrag_nr: string
  status: string
  route_path: string
  screen_id: string
}

export function isSafeOrderRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return ORDER_ROUTE_RE.test(trimmed)
}

export function pickSafeOrderRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeOrderRoutePath(trimmed) ? trimmed : null
}

export async function callOrderStatusOpen(auftragNr: string): Promise<OrderOpenResult> {
  const key = auftragNr.trim()
  if (!key) {
    throw new Error('auftrag_nr is required')
  }
  const response = await apiClient.post<OrderOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'sales.order.status',
    parameters: { auftrag_nr: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeOrderRoutePath(body?.route_path)
  if (!route || !body?.order_id) {
    throw new Error('MCP order.status returned an unsafe or incomplete route')
  }
  return {
    order_id: String(body.order_id),
    auftrag_nr: String(body.auftrag_nr ?? key),
    status: String(body.status ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'sales/sales-order'),
  }
}
