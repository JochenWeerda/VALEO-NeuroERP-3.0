/**
 * Deep-Link helpers for `agrar.contract.get` / `agrar.weighing_ticket.list`.
 * Only relative `/agrar/kontrakt/{id}` and `/waage/wiegeschein/{id}` paths.
 */

import { apiClient } from '@/lib/api-client'

const CONTRACT_ROUTE_RE = /^\/agrar\/kontrakt\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/
const WEIGHING_ROUTE_RE = /^\/waage\/wiegeschein\/([A-Za-z0-9][A-Za-z0-9._-]{0,63})$/

export type AgrarContractOpenResult = {
  kontrakt_id: string
  status: string
  route_path: string
  screen_id: string
}

export type WeighingOpenResult = {
  ticket_id: string
  partie_id: string
  route_path: string
  screen_id: string
}

function isRelativeSafePath(path: string): boolean {
  return path.startsWith('/') && !path.includes('://') && !path.includes('?') && !path.includes('#')
}

export function isSafeAgrarContractRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  return isRelativeSafePath(trimmed) && CONTRACT_ROUTE_RE.test(trimmed)
}

export function isSafeWeighingRoutePath(path: string): boolean {
  if (typeof path !== 'string') return false
  const trimmed = path.trim()
  return isRelativeSafePath(trimmed) && WEIGHING_ROUTE_RE.test(trimmed)
}

export function isSafeAgrarRoutePath(path: string): boolean {
  return isSafeAgrarContractRoutePath(path) || isSafeWeighingRoutePath(path)
}

export function pickSafeAgrarContractRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeAgrarContractRoutePath(trimmed) ? trimmed : null
}

export function pickSafeWeighingRoutePath(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return isSafeWeighingRoutePath(trimmed) ? trimmed : null
}

export async function callAgrarContractOpen(kontraktId: string): Promise<AgrarContractOpenResult> {
  const key = kontraktId.trim()
  if (!key) {
    throw new Error('kontrakt_id is required')
  }
  const response = await apiClient.post<AgrarContractOpenResult>('/api/v1/mcp/tools/call', {
    tool_name: 'agrar.contract.get',
    parameters: { kontrakt_id: key },
    mode: 'dryRun',
  })
  const body = response.data
  const route = pickSafeAgrarContractRoutePath(body?.route_path)
  if (!route || !body?.kontrakt_id) {
    throw new Error('MCP agrar.contract.get returned an unsafe or incomplete route')
  }
  return {
    kontrakt_id: String(body.kontrakt_id),
    status: String(body.status ?? ''),
    route_path: route,
    screen_id: String(body.screen_id ?? 'agrar/kontrakte'),
  }
}

export async function callWeighingTicketOpen(ticketId: string): Promise<WeighingOpenResult> {
  const key = ticketId.trim()
  if (!key) {
    throw new Error('ticket_id is required')
  }
  const response = await apiClient.post<{
    items?: Array<{
      ticket_id?: string
      partie_id?: string
      route_path?: string
      screen_id?: string
    }>
  }>('/api/v1/mcp/tools/call', {
    tool_name: 'agrar.weighing_ticket.list',
    parameters: { ticket_id: key, limit: 1 },
    mode: 'dryRun',
  })
  const item = response.data?.items?.[0]
  const route = pickSafeWeighingRoutePath(item?.route_path)
  if (!route || !item?.ticket_id) {
    throw new Error('MCP weighing_ticket.list returned an unsafe or incomplete route')
  }
  return {
    ticket_id: String(item.ticket_id),
    partie_id: String(item.partie_id ?? ''),
    route_path: route,
    screen_id: String(item.screen_id ?? 'waage/wiegeschein'),
  }
}
