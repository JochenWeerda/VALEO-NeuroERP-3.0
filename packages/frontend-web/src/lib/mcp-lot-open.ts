/**
 * Deep-Link helper for MCP tool `wms.lot.trace`.
 * Only relative `/charge/stamm/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const LOT_ROUTE_RE = /^\/charge\/stamm\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type LotOpenResult = {
  lot_id: string
  status: string
  route_path: string
  screen_id: string
}

export function isSafeLotRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return LOT_ROUTE_RE.test(trimmed)
}

export function pickSafeLotRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeLotRoutePath(trimmed) ? trimmed : null
}

export async function callLotTraceOpen(lotId: string): Promise<LotOpenResult> {
  const key = lotId.trim()
  if (!key) {
    throw new Error('lot_id is required')
  }
  const response = await apiClient.post<LotOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'wms.lot.trace',
    parameters: { lot_id: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeLotRoutePath(body?.route_path)
  if (!route || !body?.lot_id) {
    throw new Error('MCP lot.trace returned an unsafe or incomplete route')
  }
  return {
    lot_id: String(body.lot_id),
    status: String(body.status ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'charge/stamm'),
  }
}
