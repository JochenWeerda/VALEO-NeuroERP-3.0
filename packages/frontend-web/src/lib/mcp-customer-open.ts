/**
 * Deep-Link helper for MCP tool `crm.customer.open`.
 * Only relative `/crm/customers/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const CUSTOMER_ROUTE_RE = /^\/crm\/customers\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type CustomerOpenResult = {
  customer_id: string
  kunden_nr: string
  name: string
  route_path: string
  screen_id: string
}

export function isSafeCustomerRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return CUSTOMER_ROUTE_RE.test(trimmed)
}

export function pickSafeCustomerRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeCustomerRoutePath(trimmed) ? trimmed : null
}

export async function callCustomerOpen(kundenNr: string): Promise<CustomerOpenResult> {
  const key = kundenNr.trim()
  if (!key) {
    throw new Error('kunden_nr is required')
  }
  const response = await apiClient.post<CustomerOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'crm.customer.open',
    parameters: { kunden_nr: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeCustomerRoutePath(body?.route_path)
  if (!route || !body?.customer_id) {
    throw new Error('MCP customer.open returned an unsafe or incomplete route')
  }
  return {
    customer_id: String(body.customer_id),
    kunden_nr: String(body.kunden_nr ?? key),
    name: String(body.name ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'crm/customer-360'),
  }
}
