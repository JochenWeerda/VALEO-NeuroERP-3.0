/**
 * Deep-Link helper for MCP tools `dms.document.search` / `dms.gobd.export_status`.
 * Only relative `/docflow/nachweisraum/{id}` and `/docflow/gobd-export/{id}` paths.
 */

import { apiClient } from '@/lib/api-client'

const DMS_DOC_ROUTE_RE = /^\/docflow\/nachweisraum\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/
const DMS_GOBD_ROUTE_RE = /^\/docflow\/gobd-export\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type DmsDocOpenResult = {
  dokument_id: string
  titel: string
  status: string
  route_path: string
  screen_id: string
}

function isRelativeSafePath(path: string): boolean {
  return path.startsWith('/') && !path.includes('://') && !path.includes('?') && !path.includes('#')
}

export function isSafeDmsRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  if (!isRelativeSafePath(trimmed)) return false
  return DMS_DOC_ROUTE_RE.test(trimmed) || DMS_GOBD_ROUTE_RE.test(trimmed)
}

export function isSafeDmsDocumentRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  return isRelativeSafePath(trimmed) && DMS_DOC_ROUTE_RE.test(trimmed)
}

export function pickSafeDmsRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeDmsRoutePath(trimmed) ? trimmed : null
}

export function pickSafeDmsDocumentRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeDmsDocumentRoutePath(trimmed) ? trimmed : null
}

export async function callDocumentSearchOpen(dokumentId: string): Promise<DmsDocOpenResult> {
  const key = dokumentId.trim()
  if (!key) {
    throw new Error('dokument_id is required')
  }
  const response = await apiClient.post<{
    items?: Array<{
      dokument_id?: string
      titel?: string
      status?: string
      route_path?: string
      screen_id?: string
    }>
    count?: number
  }>('/api/v1/mcp/tools/call', {
    tool_name: 'dms.document.search',
    parameters: { dokument_id: key, limit: 1 },
    mode: 'dryRun',
  })
  const item = response.data?.items?.[0]
  const route = pickSafeDmsDocumentRoutePath(item?.route_path)
  if (!route || !item?.dokument_id) {
    throw new Error('MCP document.search returned an unsafe or incomplete route')
  }
  return {
    dokument_id: String(item.dokument_id),
    titel: String(item.titel ?? ''),
    status: String(item.status ?? ''),
    route_path: route,
    screen_id: String(item.screen_id ?? 'docflow/nachweisraum'),
  }
}
