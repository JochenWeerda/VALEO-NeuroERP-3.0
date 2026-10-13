import { apiClient } from '../api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

export interface StudioReport {
  violations: string[]
  readiness: { generatorReady?: boolean; errors?: string[]; warnings?: string[] }
  canPublish: boolean
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
  const payload = draftId ? { definition, expected_revision: expectedRevision } : { definition }
  const response = draftId
    ? await apiClient.put(`/api/v1/studio/drafts/${draftId}`, payload)
    : await apiClient.post('/api/v1/studio/drafts', payload)
  return response.data as StudioReport & StudioDraftRecord
}

export async function submitStudioReview(draftId: string, expectedRevision: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/submit-review`, { expected_revision: expectedRevision })
  return response.data as StudioDraftRecord
}

export async function publishStudioDraft(draftId: string, expectedRevision: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/publish`, { expected_revision: expectedRevision })
  return response.data as StudioReport & StudioDraftRecord & { route?: string }
}

export function studioRunPath(screenId: string) {
  return `/studio/run/${screenId.replace(/\//g, '__')}`
}
