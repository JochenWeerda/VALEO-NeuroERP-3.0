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

export interface VoiceSummaryRequest {
  text: string
  max_words?: number
}

export interface VoiceSummaryResponse {
  source_text: string
  summary_text: string
  provider: string
  summary_applied: boolean
  estimated_seconds: number
  error?: string
}

export interface VoiceSynthesizeRequest {
  text: string
  language?: string
}

export interface VoiceSynthesizeResponse {
  text: string
  provider: string
  browser_hint: boolean
  audio_base64?: string | null
  content_type?: string | null
  language?: string
  hint?: string
  error?: string
}

export interface VoicePipelineRequest {
  mode: 'dictate' | 'summary' | 'intent'
  text?: string
  audio_base64?: string
  audio_format?: string
  language?: string
  tone?: 'business' | 'casual' | 'formal'
  context?: { domain?: string; mask?: string; tenant_id?: string }
  synthesize?: boolean
}

export interface VoicePipelineResponse {
  mode: string
  raw_text?: string
  polished_text?: string
  source_text?: string
  summary_text?: string
  provider?: string
  polish_applied?: boolean
  summary_applied?: boolean
  estimated_seconds?: number
  text?: string
  resolved?: {
    action_id: string
    params: Record<string, unknown>
    confidence: number
    raw_text: string
  } | null
  tts?: VoiceSynthesizeResponse
  error?: string
}

export interface VoiceTranscribeRequest {
  audio_base64: string
  audio_format?: 'wav' | 'webm' | 'mp3' | 'ogg'
  language?: string
}

export interface VoiceTranscribeResponse {
  text: string
  confidence: number
  provider: string
  language: string
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

export async function summarizeVoice(body: VoiceSummaryRequest): Promise<VoiceSummaryResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) return null
  return (await res.json()) as VoiceSummaryResponse
}

export async function synthesizeVoice(body: VoiceSynthesizeRequest): Promise<VoiceSynthesizeResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: body.text, language: body.language ?? 'de-DE' }),
  })
  if (!res.ok) return null
  return (await res.json()) as VoiceSynthesizeResponse
}

export async function runVoicePipeline(body: VoicePipelineRequest): Promise<VoicePipelineResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) return null
  return (await res.json()) as VoicePipelineResponse
}

export async function transcribeVoice(body: VoiceTranscribeRequest): Promise<VoiceTranscribeResponse | null> {
  const res = await fetch(`${BASE}/api/v1/voice/transcribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio_base64: body.audio_base64,
      audio_format: body.audio_format ?? 'webm',
      language: body.language ?? 'de-DE',
    }),
  })
  if (!res.ok) return null
  return (await res.json()) as VoiceTranscribeResponse
}
