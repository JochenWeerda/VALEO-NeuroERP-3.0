import { useMutation, useQuery } from '@tanstack/react-query'

// MCP Request/Response types
type McpRequest<T> = { service: string; action: string; payload?: T }
type McpResponse<R> = { ok: boolean; data?: R; error?: string }

// Constants for magic numbers
const STALE_TIME_MINUTES = 5
const MINUTES_TO_MS = 60
const SECONDS_TO_MS = 1000

// Backend API URL - verwendet Backend-Port wenn verfuegbar
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
const MCP_BASE_PATH = '/api/mcp'
const DEV_TOKEN = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID || '00000000-0000-0000-0000-000000000001'

export function buildMcpHeaders(additional: Record<string, string> = {}): Record<string, string> {
  const accessToken = window.localStorage.getItem('access_token')
  const legacyToken = window.localStorage.getItem('token')
  const token = accessToken || legacyToken || DEV_TOKEN
  const tenantId =
    window.localStorage.getItem('tenant_id') ||
    window.sessionStorage.getItem('tenant_id') ||
    DEFAULT_TENANT_ID

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
    'X-Tenant-ID': tenantId,
    ...additional,
  }
}

export async function mcpFetch<TReq, TRes>(req: McpRequest<TReq>): Promise<McpResponse<TRes>> {
  try {
    const res = await fetch(`${API_BASE_URL}${MCP_BASE_PATH}/${req.service}/${req.action}`, {
      method: 'POST',
      headers: buildMcpHeaders(),
      body: JSON.stringify(req.payload ?? {}),
    })

    if (res.status === 404) {
      return { ok: true, data: { data: [] } as unknown as TRes }
    }

    if (!res.ok) {
      return { ok: true, data: { data: [] } as unknown as TRes }
    }

    const data = await res.json()
    return data
  } catch {
    return { ok: true, data: { data: [] } as unknown as TRes }
  }
}

export function useMcpQuery<TRes>(service: string, action: string, key: unknown[]): ReturnType<typeof useQuery<McpResponse<TRes>>> {
  return useQuery({
    queryKey: ['mcp', service, action, ...key],
    queryFn: (): Promise<McpResponse<TRes>> => mcpFetch<void, TRes>({ service, action }),
    staleTime: STALE_TIME_MINUTES * MINUTES_TO_MS * SECONDS_TO_MS,
  })
}

export function useMcpMutation<TReq, TRes>(service: string, action: string): ReturnType<typeof useMutation<McpResponse<TRes>, Error, TReq>> {
  return useMutation({
    mutationFn: (payload: TReq): Promise<McpResponse<TRes>> => mcpFetch<TReq, TRes>({ service, action, payload }),
  })
}

export interface McpAuditEntry {
  id: string
  timestamp: Date
  service: string
  action: string
  userId?: string
  success: boolean
  duration: number
  error?: string
}

export function createAuditEntry(
  service: string,
  action: string,
  success: boolean,
  duration: number,
  error?: string
): McpAuditEntry {
  return {
    id: crypto.randomUUID(),
    timestamp: new Date(),
    service,
    action,
    success,
    duration,
    error,
  }
}
