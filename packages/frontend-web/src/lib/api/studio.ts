import { apiClient } from '../api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

export interface StudioReport {
  violations: string[]
  readiness: { generatorReady?: boolean; errors?: string[]; warnings?: string[] }
  canPublish: boolean
  definitionReady: boolean
  requiresSimulation?: boolean
  definition: ScreenDefinition
}

export interface StudioDraftRecord {
  id: string
  status: string
  revision: string
  definition: ScreenDefinition
}

export async function fetchStudioDrafts(): Promise<StudioDraftRecord[]> {
  const response = await apiClient.get('/api/v1/studio/drafts')
  return response.data.drafts ?? []
}

export async function fetchStudioDraft(id: string): Promise<StudioDraftRecord> {
  const response = await apiClient.get(`/api/v1/studio/drafts/${encodeURIComponent(id)}`)
  return response.data as StudioDraftRecord
}

export async function fetchStudioCatalog() {
  const response = await apiClient.get('/api/v1/studio/catalog')
  return response.data as {
    permissions: { canDesign: boolean; canPublish: boolean }
    floorplans: string[]
    fieldTypes: string[]
    columnNavigation: string[]
    dataSources: Array<{ key: string; label: string; endpoint: string }>
    actions: Array<{ key: string; label: string; dangerLevel: string }>
  }
}

export async function validateStudioDraft(definition: ScreenDefinition): Promise<StudioReport> {
  const response = await apiClient.post('/api/v1/studio/validate', { definition })
  return response.data as StudioReport
}

export async function proposeStudioDraft(intent: string): Promise<StudioReport> {
  const response = await apiClient.post('/api/v1/studio/propose', { intent })
  return response.data as StudioReport
}

export async function saveStudioDraft(definition: ScreenDefinition, draftId?: string, expectedRevision?: string) {
  if (draftId && !expectedRevision) throw new Error('Gespeicherten Entwurfsstand zuerst laden.')
  const normalize = (value: unknown): unknown => {
    if (Array.isArray(value)) return value.map(normalize)
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([key, item]) => [key, normalize(item)]))
    return value
  }
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(normalize(JSON.parse(JSON.stringify(definition))))))
  const fingerprint = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('')
  const idempotencyKey = statusKey(draftId ? 'update' : 'create', draftId ?? definition.id, `${expectedRevision ?? ''}:${fingerprint}`)
  const payload = draftId ? { definition, expected_revision: expectedRevision, idempotency_key: idempotencyKey } : { definition, idempotency_key: idempotencyKey }
  const response = draftId
    ? await apiClient.put(`/api/v1/studio/drafts/${draftId}`, payload)
    : await apiClient.post('/api/v1/studio/drafts', payload)
  return response.data as StudioReport & StudioDraftRecord
}

const statusKeys = new Map<string, string>()
function statusKey(action: string, draftId: string, revision: string): string {
  const intent = `valeo.studio.status:${action}:${draftId}:${revision}`
  const cached = statusKeys.get(intent)
  if (cached) return cached
  let key: string | null = null
  try { key = sessionStorage.getItem(intent) } catch { /* memory fallback for unavailable browser storage */ }
  key ??= crypto.randomUUID()
  statusKeys.set(intent, key)
  try { sessionStorage.setItem(intent, key) } catch { /* retained in this client instance */ }
  return key
}

export async function submitStudioReview(draftId: string, expectedRevision: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/submit-review`, { expected_revision: expectedRevision, idempotency_key: statusKey('review', draftId, expectedRevision) })
  return response.data as StudioDraftRecord
}

export async function publishStudioDraft(draftId: string, expectedRevision: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/publish`, { expected_revision: expectedRevision, idempotency_key: statusKey('publish', draftId, expectedRevision) })
  return response.data as StudioReport & StudioDraftRecord & { route?: string }
}

export function studioRunPath(screenId: string) {
  return `/studio/run/${screenId.replace(/\//g, '__')}`
}


export interface StudioSimulationResult {
  passed: boolean
  candidate_revision: string
  profile: string | null
  failed_checks?: string[]
  error?: string
}

export async function simulateStudioDraft(draftId: string, expectedRevision: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${encodeURIComponent(draftId)}/simulate`, {
    expected_revision: expectedRevision, idempotency_key: statusKey('simulation', draftId, expectedRevision),
  })
  // An acknowledged simulation is complete. A deliberate new attempt gets a new
  // key, while a transport failure keeps the key for recovery of the same attempt.
  const intent = `valeo.studio.status:simulation:${draftId}:${expectedRevision}`
  statusKeys.delete(intent)
  try { sessionStorage.removeItem(intent) } catch { /* client-memory key was cleared */ }
  return response.data as StudioDraftRecord & { simulation: StudioSimulationResult }
}
