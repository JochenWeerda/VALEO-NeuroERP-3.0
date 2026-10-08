/**
 * Deep-Link helper for MCP tool `wms.cell.status`.
 * Only relative `/lager/silo-zellen/{id}` paths are accepted (no open redirect).
 */

import { apiClient } from '@/lib/api-client'

const CELL_ROUTE_RE = /^\/lager\/silo-zellen\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type CellOpenResult = {
  cell_id: string
  cell_code: string
  qs_status: string
  route_path: string
  screen_id: string
}

export function isSafeCellRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!trimmed.startsWith('/') || trimmed.includes('://') || trimmed.includes('?') || trimmed.includes('#')) {
    return false
  }
  return CELL_ROUTE_RE.test(trimmed)
}

export function pickSafeCellRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeCellRoutePath(trimmed) ? trimmed : null
}

export async function callCellStatusOpen(cellCode: string): Promise<CellOpenResult> {
  const key = cellCode.trim()
  if (!key) {
    throw new Error('cell_code is required')
  }
  const response = await apiClient.post<CellOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'wms.cell.status',
    parameters: { cell_code: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeCellRoutePath(body?.route_path)
  if (!route || !body?.cell_id) {
    throw new Error('MCP cell.status returned an unsafe or incomplete route')
  }
  return {
    cell_id: String(body.cell_id),
    cell_code: String(body.cell_code ?? key),
    qs_status: String(body.qs_status ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'lager/silo-cell'),
  }
}
