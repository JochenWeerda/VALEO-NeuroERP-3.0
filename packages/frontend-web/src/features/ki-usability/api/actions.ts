/**
 * Fetch actions from ki-usability-api (optional: filter by domain/mask)
 */

export interface Action {
  id: string
  label: string
  label_en?: string
  shortcut?: string
  description?: string
  category: string
  domain?: string
  mask?: string
  intent_phrases: string[]
  required_data: string[]
}

export interface ActionListResponse {
  actions: Action[]
  total: number
}

/** Base URL for ki-usability-api (dev: use Vite proxy /api/ki-usability → localhost:5200) */
const BASE =
  (import.meta.env as Record<string, string | undefined>).VITE_KI_USABILITY_API_URL ?? '/api/ki-usability'

export async function fetchActions(domain?: string, mask?: string): Promise<ActionListResponse> {
  const params = new URLSearchParams()
  if (domain) params.set('domain', domain)
  if (mask) params.set('mask', mask)
  const q = params.toString()
  const url = `${BASE}/api/v1/actions${q ? `?${q}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Actions fetch failed: ${res.status}`)
  return res.json() as Promise<ActionListResponse>
}

export async function fetchAction(actionId: string): Promise<Action | null> {
  const res = await fetch(`${BASE}/api/v1/actions/${encodeURIComponent(actionId)}`)
  if (res.status === 404) return null
  if (!res.ok) throw new Error(`Action fetch failed: ${res.status}`)
  return res.json() as Promise<Action>
}
