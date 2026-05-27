/**
 * Voice resolve: send transcribed text to ki-usability-api, get action_id + params
 */

export interface VoiceResolveRequest {
  text: string
  context?: { domain?: string; mask?: string; tenant_id?: string }
}

export interface VoiceResolveResponse {
  action_id: string
  params: Record<string, unknown>
  confidence: number
  raw_text: string
}

export interface VoicePolishRequest {
  text: string
  tone?: 'business' | 'casual' | 'formal'
}

export interface VoicePolishResponse {
  raw_text: string
  polished_text: string
  provider: string
  polish_applied: boolean
  error?: string
}

/** Base URL for ki-usability-api (dev: use Vite proxy /api/ki-usability → localhost:5200) */
const BASE =
  (import.meta.env as Record<string, string | undefined>).VITE_KI_USABILITY_API_URL ?? '/api/ki-usability'

export async function resolveVoice(
  body: VoiceResolveRequest
): Promise<VoiceResolveResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) return null
  const data = await res.json()
  if (data == null) return null
  return data as VoiceResolveResponse
}

export async function polishVoice(body: VoicePolishRequest): Promise<VoicePolishResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/polish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: body.text, tone: body.tone ?? 'business' }),
  })
  if (!res.ok) return null
  return (await res.json()) as VoicePolishResponse
}
