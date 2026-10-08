/**
 * Deep-Link helper for MCP tool `einkauf.bestellung.status`.
 * Only relative `/einkauf/bestellung/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const PO_ROUTE_RE = /^\/einkauf\/bestellung\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type PoOpenResult = {
  bestellung_id: string
  bestellnummer: string
  status: string
  route_path: string
  screen_id: string
}

export function isSafePoRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return PO_ROUTE_RE.test(trimmed)
}

export function pickSafePoRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafePoRoutePath(trimmed) ? trimmed : null
}

export async function callPoStatusOpen(bestellungId: string): Promise<PoOpenResult> {
  const key = bestellungId.trim()
  if (!key) {
    throw new Error('bestellung_id is required')
  }
  const response = await apiClient.post<PoOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'einkauf.bestellung.status',
    parameters: { bestellung_id: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafePoRoutePath(body?.route_path)
  if (!route || !body?.bestellung_id) {
    throw new Error('MCP bestellung.status returned an unsafe or incomplete route')
  }
  return {
    bestellung_id: String(body.bestellung_id),
    bestellnummer: String(body.bestellnummer ?? key),
    status: String(body.status ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'einkauf/purchase-order'),
  }
}
