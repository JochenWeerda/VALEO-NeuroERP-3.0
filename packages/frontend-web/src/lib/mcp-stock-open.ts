/**
 * Deep-Link helper for MCP tool `lager.bestand.get`.
 * Only relative `/lager/artikel/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const STOCK_ROUTE_RE = /^\/lager\/artikel\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type StockOpenResult = {
  artikel_id: string
  verfuegbar: number
  route_path: string
  screen_id: string
}

export function isSafeStockRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return STOCK_ROUTE_RE.test(trimmed)
}

export function pickSafeStockRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeStockRoutePath(trimmed) ? trimmed : null
}

export async function callStockBestandOpen(artikelId: string): Promise<StockOpenResult> {
  const key = artikelId.trim()
  if (!key) {
    throw new Error('artikel_id is required')
  }
  const response = await apiClient.post<StockOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'lager.bestand.get',
    parameters: { artikel_id: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeStockRoutePath(body?.route_path)
  if (!route || !body?.artikel_id) {
    throw new Error('MCP lager.bestand.get returned an unsafe or incomplete route')
  }
  return {
    artikel_id: String(body.artikel_id),
    verfuegbar: Number(body.verfuegbar ?? 0),
    route_path: route,
    screen_id: String(body.screen_id ?? 'lager/article-stock'),
  }
}
