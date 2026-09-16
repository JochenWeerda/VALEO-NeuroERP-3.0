import { apiClient } from '../api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

export interface StudioReport {
  violations: string[]
  readiness: { generatorReady?: boolean; errors?: string[]; warnings?: string[] }
  canPublish: boolean
  definition: ScreenDefinition
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
  const response = await apiClient.post('/api/v1/studio/propose', { intent }, {
    headers: { 'X-Actor-ID': currentStudioActor() },
  })
  return response.data as StudioReport
}

export async function saveStudioDraft(definition: ScreenDefinition, draftId?: string) {
  const payload = { definition }
  const headers = { 'X-Actor-ID': currentStudioActor() }
  const response = draftId
    ? await apiClient.put(`/api/v1/studio/drafts/${draftId}`, payload, { headers })
    : await apiClient.post('/api/v1/studio/drafts', payload, { headers })
  return response.data as StudioReport & { id: string; status: string }
}

export async function submitStudioReview(draftId: string) {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/submit-review`, {}, {
    headers: { 'X-Actor-ID': currentStudioActor() },
  })
  return response.data
}

export async function publishStudioDraft(draftId: string, actor = 'studio-reviewer') {
  const response = await apiClient.post(`/api/v1/studio/drafts/${draftId}/publish`, {}, {
    headers: { 'X-Actor-ID': actor },
  })
  return response.data as StudioReport & { id: string; status: string; route?: string }
}

export function studioRunPath(screenId: string) {
  return `/studio/run/${screenId.replace(/\//g, '__')}`
}

function currentStudioActor(): string {
  return 'studio-editor'
}
